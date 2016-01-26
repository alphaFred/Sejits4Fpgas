""" """

import re
import os
import ast
import copy
import json
import logging
import tempfile
import sejits_ctree

from sejits_ctree.vhdl.nodes import VhdlFile
from collections import namedtuple
from sejits_ctree.frontend import get_ast


logger = logging.getLogger(__name__)

JitSyntDataModule = namedtuple("JitSyntDataModule", ["main_file", "file_names"])


class VhdlSynthModule(object):
    """
    Manages compilation of multiple ASTs.
    """

    def __init__(self):
        import os

        # write files to $TEMPDIR/sejits_ctree/run-XXXX
        ctree_dir = os.path.join(tempfile.gettempdir(), "sejits_ctree")
        if not os.path.exists(ctree_dir):
            os.mkdir(ctree_dir)

        self.synthesis_dir = tempfile.mkdtemp(prefix="run-", dir=ctree_dir)
        self.ll_module = None
        self.exec_engine = None
        #
        self._linked_files = []

    def __call__(self):
        """ Redirect call to python or vhdl kernel. """
        print "VhdlSynthModule got called"

    def _link_in(self, data_module):
        self._linked_files.append(data_module)
        # if self.ll_module is not None:
        #     self.ll_module.link_in(submodule)
        # else:
        #     self.ll_module = submodule

    def get_callable(self, entry_point_name, entry_point_typesig):
        """
        Returns a python callable that dispatches to the requested C function.
        """
        self._link_to_project()
        self._activate()
        return self

    def _link_to_project(self):
        ip_repo_dir = "../../ip_repo/proc_ip_1.0/"
        #
        hdl_dir = ip_repo_dir + "hdl/"
        #
        filenames = next(os.walk(hdl_dir))[2]
        #
        axi_file = [fname for fname in filenames if "AXI" in fname]
        assert len(axi_file) == 1, "Could not find unique AXI file in ip_repo"

        tmp_axi_file = hdl_dir + "temp_" + axi_file[0]
        axi_file = hdl_dir + axi_file[0]

        with open(tmp_axi_file, "w")as w_temp_file:
            with open(axi_file, "r") as r_temp_file:
                for line in r_temp_file:
                    if "-- Add user logic here" in line:
                        w_temp_file.write(line)
                        #
                        for lfile in self._linked_files:

                            node = lfile.main_file
                            entity = node.body[0]

                            from nodes import Component
                            from codegen import VhdlCodeGen

                            file_comp = Component(name=entity.name,
                                                  generics=entity.generics,
                                                  in_ports=entity.in_ports,
                                                  out_port=entity.out_port)
                            file_comp.lib_name = "work." + entity.name

                            gen_code = VhdlCodeGen().visit_Component(file_comp)
                            w_temp_file.write(gen_code)
                    else:
                        w_temp_file.write(line)
        #
        os.remove(axi_file)
        os.rename(tmp_axi_file, axi_file)
        #
        for data_module in self._linked_files:
            for path in data_module.file_names:
                os.system("cp " + path + " " + hdl_dir)

    def _activate(self):
        """ Activate synthesis subprocess. """
        # copy template project to synthesis directory
        # copy all vhdl files to template project ip folder
        # integrate vhdl files into templare project
        #   multiply process pipeline according to input width and data width
        #   integrate and connect pipelines into axi stream ip
        pass


class LazySpecializedFunction(object):

    """ A callable object that will synthesize and load code just-in-time. """

    ProgramConfig = namedtuple('ProgramConfig',
                               ['args_subconfig', 'tuner_subconfig'])

    _directory_fields = ['__class__.__name__', 'backend_name']

    class NameExtractor(ast.NodeVisitor):

        """ Extracts the first FunctionDef name found. """

        def visit_FunctionDef(self, node):
            """ Visit FunctionDef node and return name. """
            return node.name

        def generic_visit(self, node):
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            res = self.visit(item)
                            if res:
                                return res
                elif isinstance(value, ast.AST):
                    res = self.visit(value)
                    if res:
                        return res

    def __init__(self, py_ast=None, sub_dir=None, backend_name="zynq"):
        """ Initialize LazySpecializedFunction. """
        self.sub_dir = sub_dir or \
            self.NameExtractor().visit(self.original_tree)
        self.original_tree = py_ast
        self.backend_name = backend_name

    @property
    def original_tree(self):
        return copy.deepcopy(self._original_tree)

    @original_tree.setter
    def original_tree(self, value):
        if not hasattr(self, '_original_tree'):
            self._original_tree = value
        elif ast.dump(self.__original_tree, True, True) != \
                ast.dump(value, True, True):
            raise AttributeError('Cannot redefine the ast')

    @property
    def info_filename(self):
        return 'info.json'

    def get_info(self, path):
        info_filepath = os.path.join(path, self.info_filename)
        if not os.path.exists(info_filepath):
            return {'hash': None, 'files': []}
        with open(info_filepath) as info_file:
            return json.load(info_file)

    def set_info(self, path, dictionary):
        info_filepath = os.path.join(path, self.info_filename)
        with open(info_filepath, 'w') as info_file:
            return json.dump(dictionary, info_file)

    def __call__(self, *args, **kwargs):
        """
        Determines the program_configuration to be run. If it has yet to be
        built, build it. Then, execute it. If the selected
        program_configuration for this function has already been code
        generated for, this method draws from the cache.
        """
        sejits_ctree.STATS.log("specialized function call")

        logger.info("detected specialized function call with arg types: %s",
                    [type(a) for a in args] +
                    [type(kwargs[key]) for key in kwargs])

        program_config = self.get_program_config(args, kwargs)
        dir_name = self.config_to_dirname(program_config)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        sejits_ctree.STATS.log("specialized function cache miss")
        logger.info("specialized function cache miss.")
        transform_result = self.get_transform_result(
            program_config, dir_name)

        csf = self.finalize(transform_result, program_config)

        return csf(*args, **kwargs)

    def get_program_config(self, args, kwargs):
        """ Return ProgramConfig namedtuple. """
        # Don't break old specializers that don't support kwargs
        try:
            args_subconfig = self.args_to_subconfig(args, kwargs)
        except TypeError:
            args_subconfig = self.args_to_subconfig(args)

        logger.info("arguments subconfig: %s", args_subconfig)

        return self.ProgramConfig(args_subconfig, None)

    """
    def get_transform_result(self, program_config, dir_name, cache=True):
        transform_result = self.run_transform(program_config)
        return transform_result
    """

    def get_transform_result(self, program_config, dir_name, cache=True):
        info = self.get_info(dir_name)
        # check to see if the necessary code is in the persistent cache
        if hash(self) != info['hash'] and self.original_tree is not None \
                or not cache:
            # need to run transform() for code generation
            logger.info('Hash miss. Running Transform\n')
            sejits_ctree.STATS.log("Filesystem cache miss")
            transform_result = self.run_transform(program_config)

            # Saving files to cache directory
            for source_file in transform_result:
                assert isinstance(source_file, VhdlFile), \
                    "Transform must return an iterable of Files"
                if source_file.generated:
                    source_file.path = dir_name

            new_info = {'hash': hash(self),
                        'files': [os.path.join(f.path, f.get_filename())
                                  for f in transform_result]}
            self.set_info(dir_name, new_info)
        else:
            logger.info('Hash hit. Skipping transform')
            sejits_ctree.STATS.log('Filesystem cache hit')
            # retrieves VhdlFile from from cache
            # TODO: reintegrate code below!
            # files = [getFile(path) for path in info['files']]
            # transform_result = files
            transform_result = None
        return transform_result

    def run_transform(self, program_config):
        transform_result = self.transform(self.original_tree, program_config)
        return transform_result

    def config_to_dirname(self, program_config):
        """Returns the subdirectory name under .compiled/funcname"""
        # fixes the directory names and squishes invalid chars
        regex_filter = re.compile(r"""[/\?%*:|"<>()'{} ]""")

        def deep_getattr(obj, s):
            parts = s.split('.')
            for part in parts:
                obj = getattr(obj, part)
            return obj

        path_parts = [
            self.sub_dir,
            str(self._hash(program_config.args_subconfig)),
            str(self._hash(program_config.tuner_subconfig))]

        for attrib in self._directory_fields:
            path_parts.append(str(deep_getattr(self, attrib)))
        filtered_parts = [
            str(re.sub(regex_filter, '_', part)) for part in path_parts]
        compile_path = str(sejits_ctree.CONFIG.get('jit', 'COMPILE_PATH'))

        path = os.path.join(compile_path, *filtered_parts)
        ret = re.sub('_+', '_', path)
        return ret

    @staticmethod
    def _hash(o):
        if isinstance(o, dict):
            return hash(frozenset(
                LazySpecializedFunction._hash(item) for item in o.items()
            ))
        else:
            return hash(str(o))

    @classmethod
    def from_function(cls, func, folder_name=''):
        func_ast = get_ast(func)
        return cls(py_ast=func_ast, sub_dir=folder_name or func.__name__)

    # =====================================================
    # Methods to be overridden by the user

    def transform(self, tree, program_config):
        """
        Convert the AST 'tree' into a C AST, optionally taking advantage of the
        actual runtime arguments.
        """
        raise NotImplementedError()

    def finalize(self, transform_result, program_config):
        """
        This function will be passed the result of transform.  The specializer
        should return an ConcreteSpecializedFunction.
        """
        raise NotImplementedError("Finalize must be implemented")

    def args_to_subconfig(self, args):
        """
        Extract features from the arguments to define uniqueness of
        this particular invocation. The return value must be a hashable
        object, or a dictionary of hashable objects.
        """
        logger.warn("arguments will not influence program_config. " +
                    "Consider overriding args_to_subconfig() in %s.",
                    type(self).__name__)
        return dict()


class ConcreteSpecializedFunction(object):

    """ A function backed by synthesized and loaded code. """

    pass
