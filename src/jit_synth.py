""" """
import os
import glob
import ast
import logging
import subprocess
import ctypes as c
import numpy as np
import numpy.ctypeslib as ctl
from .vhdl_ctree.frontend import get_ast
from .vhdl_ctree.c.nodes import MultiNode
from .vhdl_ctree.jit import LazySpecializedFunction
from .utils import TransformationError
from collections import namedtuple
#
from utils import CONFIG


logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "DISABLE_LOGGING")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


class VhdlSynthModule(object):

    """ Manages synthetisation of all VhdlFiles in VhdlProject."""

    def __init__(self):
        self._linked_files = []
        # vivado project folder
        self.v_proj_fol = os.path.dirname(__file__) + CONFIG.get("vivado", "PROJ_FOLDER_PATH")
        if os.path.isdir(self.v_proj_fol):
            logger.info("Found Vivado Project at: %s" % self.v_proj_fol)
        else:
            log_txt = "Could not find Vivado Project at: %s" % self.v_proj_fol
            logger.warning(log_txt)
        # ---------------------------------------------------------------------
        # LOGGING
        # ---------------------------------------------------------------------
        logger.info("Initialized VhdlSynthModule")
        # ---------------------------------------------------------------------
        self.hw_interface = None

    def __call__(self, *args, **kwargs):
        """Redirect call to python or vhdl kernel."""
        if os.uname()[-1] == "armv7l":
            if len(args) > 1:
                raise TransformationError("Multiple input data currently not supported by the hardware")
            mod_arg = args[0].astype(np.uint32)
            self.hw_interface(mod_arg, len(mod_arg))
            return mod_arg
        else:
            return "Concrete Specialized Function called on x86"

    def _link_in(self, submodule):
        """Add submodule to list of linked files.

        :param submodule: path to VHDL file
        :type submodule: str
        """
        self._linked_files.append(submodule)

    def get_callable(self, entry_point_name, entry_point_typesig):
        """Return a python callable that redirects to hardware."""
        self._link_to_vivado_project()
        self._activate()
        return self

    def _link_to_vivado_project(self):
        """Link all files to Vivado template project."""
        # vivado src folder
        v_src_fol = self.v_proj_fol + "template_project.srcs/sources_1/new/"

        # Clean up source folder
        for proj_file in glob.glob(v_src_fol + "*"):
            if os.path.basename(proj_file) != "top.vhd":
                os.remove(proj_file)

        # Copy all files to top folder and save file names
        file_names = []
        for file_path in self._linked_files:
            os.system("cp " + file_path + " " + v_src_fol)
            file_names.append(os.path.basename(file_path))

        # Add update source files in TCL script
        saved_tcl_file_path = self.v_proj_fol + "template_project.sav"
        mod_tcl_file_path = self.v_proj_fol + "template_project.tcl"
        if not os.path.exists(saved_tcl_file_path):
            os.system("cp " + mod_tcl_file_path + " " + saved_tcl_file_path)

        with open(saved_tcl_file_path, "r") as old_tcl, open(mod_tcl_file_path, "w") as new_tcl:
                line = old_tcl.readline()

                # TODO: find better way than with while loops

                # read till set origin_dir
                while "set origin_dir" not in line:
                    new_tcl.write(line)
                    line = old_tcl.readline()

                new_tcl.write("set origin_dir " + '"' + os.path.abspath(self.v_proj_fol) + '"')
                line = ""

                # read till create_project
                while "create_project" not in line:
                    new_tcl.write(line)
                    line = old_tcl.readline()

                new_tcl.write("create_project -force template_project ./template_project\n")
                line = ""

                # read till set files begins
                while "set files" not in line:
                    new_tcl.write(line)
                    line = old_tcl.readline()
                # read till end of set files
                while "]\n" != line:
                    new_tcl.write(line)
                    line = old_tcl.readline()

                # insert new files
                tcl_set_file = ' "[file normalize "$origin_dir/template_project.srcs/sources_1/new/{file_name}"]"\\\n'

                for vhdl_file_name in file_names:
                    new_tcl.write(tcl_set_file.format(file_name=vhdl_file_name))
                new_tcl.write("]\n")

                # copy rest of file
                for line in old_tcl.readlines():
                    new_tcl.write(line)

    def _activate(self):
        """Initialize Vivado synthesis subprocess."""
        if os.uname()[-1] == "armv7l":
            print "Execute synthesis script"
        else:
            pass


class VhdlLazySpecializedFunction(LazySpecializedFunction):

    def __init__(self, py_ast=None, sub_dir=None, backend_name="default", py_func=None):
        """Extend existing LazySpecializedFunction with error handling and default execution.

        Herefore the parameter py_func is added  in order to also pass the Python function of the AST passed to py_ast.

        :param py_ast: Python AST representation of py_func
        :param sub_dir: sub directory
        :param backend_name: Unused in VHDL Back-End
        :type backend_name: str
        :param py_func: Python function which is also passed in its AST representation as py_ast
        :type py_func: function

        """
        self.py_func = py_func
        super(VhdlLazySpecializedFunction, self).__init__(py_ast, sub_dir, backend_name)

    def __call__(self, *args, **kwargs):
        """ Added error-handling with Python fall-back around super.__call__.

        If calling the __call__ method of the super-class raises an TransformationError exeption, the passed Python
        function will be called instead of an specialized version. In case of an TransformationError, the cache is
        cleared.

        .. todo:: refine cache cleaning in error case
        """
        ret = None
        try:
            ret = super(VhdlLazySpecializedFunction, self).__call__(*args, **kwargs)
        except TransformationError:
            print "Calling Python function ..."
            subprocess.call(["ctree", "-cc"])
            ret = self.py_func(*args, **kwargs)
        finally:
            return ret

    @classmethod
    def from_function(cls, func, folder_name=''):
        class Replacer(ast.NodeTransformer):
            def visit_Module(self, node):
                return MultiNode(body=[self.visit(i) for i in node.body])

            def visit_FunctionDef(self, node):
                if node.name == func.__name__:
                    node.name = 'apply'
                node.body = [self.visit(item) for item in node.body]
                return node

            def visit_Name(self, node):
                if node.id == func.__name__:
                    node.id = 'apply'
                return node

        func_ast = Replacer().visit(get_ast(func))
        return cls(py_ast=func_ast, sub_dir=folder_name or func.__name__, py_func=func)
