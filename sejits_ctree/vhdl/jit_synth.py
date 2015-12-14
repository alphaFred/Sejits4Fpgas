""" """

import re
import os
import ast
import copy
import logging
import sejits_ctree

from collections import namedtuple
from sejits_ctree.frontend import get_ast

log = logging.getLogger(__name__)


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

    def __init__(self, py_ast=None, sub_dir=None, backend_name="default"):
        """ Initialize LazySpecializedFunction. """
        self.sub_dir = sub_dir or \
            self.NameExtractor().visit(self.original_tree)
        self.original_tree = py_ast
        self.backend_name = "zynq"

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

    def __call__(self, *args, **kwargs):
        """
        Determines the program_configuration to be run. If it has yet to be
        built, build it. Then, execute it. If the selected
        program_configuration for this function has already been code
        generated for, this method draws from the cache.
        """
        sejits_ctree.STATS.log("specialized function call")

        log.info("detected specialized function call with arg types: %s",
                 [type(a) for a in args] +
                 [type(kwargs[key]) for key in kwargs])

        program_config = self.get_program_config(args, kwargs)
        dir_name = self.config_to_dirname(program_config)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        sejits_ctree.STATS.log("specialized function cache miss")
        log.info("specialized function cache miss.")
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

        log.info("arguments subconfig: %s", args_subconfig)

        return self.ProgramConfig(args_subconfig, None)

    def get_transform_result(self, program_config, dir_name, cache=True):
        transform_result = self.run_transform(program_config)
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
        return re.sub('_+', '_', path)

    def args_to_subconfig(self, args):
        """
        Extract features from the arguments.

        These features are used to define uniqueness of this particular
        invocation. The return value must be a hashable object, or a
        dictionary of hashable objects.
        """
        log.warn("arguments will not influence program_config. " +
                 "Consider overriding args_to_subconfig() in %s.",
                 type(self).__name__)
        return dict()

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


class ConcreteSpecializedFunction(object):

    """ A function backed by synthesized and loaded code. """

    pass
