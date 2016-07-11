""" """
import os
import glob
import ast
import logging
import subprocess
import ctypes as c
import numpy as np
import numpy.ctypeslib as ctl
from pkg_resources import resource_filename
from sejits4fpgas.src.vhdl_ctree.frontend import get_ast
from sejits4fpgas.src.vhdl_ctree.c.nodes import MultiNode
from sejits4fpgas.src.vhdl_ctree.jit import LazySpecializedFunction
from sejits4fpgas.src.errors import TransformationError
from collections import namedtuple
#
from sejits4fpgas.src.config import config

logger = logging.getLogger(__name__)
logger.disabled = config.getboolean("Logging", "disable_logging")


class VhdlSynthModule(object):

    """ Manages synthetisation of all VhdlFiles in VhdlProject."""

    def __init__(self):
        # ---------------------------------------------------------------------
        logger.info("Initialized new {} instance".format(self.__class__.__name__))
        # ---------------------------------------------------------------------

        self._linked_files = []

        # Get and check vivado project folder path
        self.v_proj_fol = resource_filename("sejits4fpgas", config.get("Paths", "vivado_proj_path"))
        if not os.path.isdir(self.v_proj_fol):
            logger.warning("Could not find Vivado Project at: {}".format(self.v_proj_fol))
            raise TransformationError("Could not find Vivado Project")

        # Get and check hw interface path and module name
        hw_intfc_path = config.get("HwInterface", "hw_intfc_path")
        hw_intfc_name = config.get("HwInterface", "hw_intfc_module")

        hw_intfc_filepath = resource_filename("sejits4fpgas", hw_intfc_path + hw_intfc_name)

        if not os.path.isfile(hw_intfc_filepath):
            logger.warning("Could not find HW interface module: {}".format(hw_intfc_filepath))
            raise TransformationError("Could not find HW interface module")

        if os.uname()[-1] == "armv7l":
            # Load hw interface and define argument types
            libHwIntfc = c.cdll.LoadLibrary(hw_intfc_filepath)
            libHwIntfc.process_img.argtypes = [ctl.ndpointer(np.uint32, ndim=1, flags='C'), c.c_uint, c.c_uint, c.c_uint]
            self.hw_interface = libHwIntfc.process_img

    def __call__(self, *args, **kwargs):
        """Redirect call to python or vhdl kernel."""
        if os.uname()[-1] == "armv7l":
            if len(args) > 1:
                raise TransformationError("Multiple input data currently not supported by the hardware")
            mod_arg = args[0].astype(np.uint32)
            img_w = mod_arg.shape[0]
            orig_arg_shape = mod_arg.shape
            #
            mod_arg = mod_arg.flatten()
            self.hw_interface(mod_arg, np.uint(len(mod_arg)), img_w, config.getint("Dma", "dma_chunk_size"))
            #
            out_img = mod_arg.astype(np.uint8)
            out_img = out_img.reshape(orig_arg_shape)
            #
            return out_img
        else:
            return "Concrete Specialized Function called on x86"

    def _link_in(self, submodule):
        """Add submodule to list of linked files.

        :param submodule: path to VHDL file
        :type submodule: str
        """
        logger.debug("Added new submodule:{} to {}".format(submodule, self.__class__.__name__))
        self._linked_files.append(submodule)

    def get_callable(self, entry_point_name, entry_point_typesig):
        """Return a python callable that redirects to hardware."""
        self._update_vivado_proj()
        self._synthesize_vivado_proj()
        return self

    def _update_vivado_proj(self):
        """Link all files to Vivado template project."""
        # vivado src folder
        v_src_fol = self.v_proj_fol + "template_project.srcs/sources_1/new/"

        # Clean up source folder
        for proj_file in glob.glob(v_src_fol + "*"):
            if os.path.basename(proj_file) != "top.vhd":
                os.remove(proj_file)

        # Copy all files to vivado template src folder and save file names
        file_names = []
        for file_path in self._linked_files:
            os.system("cp " + file_path + " " + v_src_fol)
            file_names.append(os.path.basename(file_path))

        # Include source files names in vivado projects TCL script
        tcl_file_path = self.v_proj_fol + "template_project.sav"
        mod_tcl_file_path = self.v_proj_fol + "template_project.tcl"
        # If saved tcl script does not exist copy existing tcl to new .sav file
        if not os.path.exists(tcl_file_path):
            os.system("cp " + mod_tcl_file_path + " " + tcl_file_path)

        with open(tcl_file_path, "r") as old_tcl, open(mod_tcl_file_path, "w") as new_tcl:
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

    def _synthesize_vivado_proj(self):
        """Initialize Vivado synthesis subprocess."""
        if os.uname()[-1] == "armv7l":
            logger.log(level=logging.INFO, msg="Execute synthesis script")
            # TODO: Implement generation of async subprocess, calling synthesis script on remote
            connection_str = config.get("Automation", "user") + "@" + config.get("Automation", "host") + ":"
            # move vhdl files to remote host
            host_proj_folder = config.get("Automation", "host_v_proj_path")

            logger.log("Copy .vhd files to " + connection_str + host_proj_folder + "template_project.srcs/sources_1/new/")
            for file in glob.glob(host_proj_folder + "*"):
                subprocess.call(["scp", "-i", ".ssh/zedboard_autoconnect", file,
                                 connection_str + host_proj_folder + "template_project.srcs/sources_1/new/"])

            # move tcl script to remote host
            logger.log("Copy .tcl script to " + connection_str + host_proj_folder)
            tcl_file_path = self.v_proj_fol + "template_project.tcl"
            subprocess.call(["scp", "-i", ".ssh/zedboard_autoconnect", tcl_file_path,
                             connection_str + host_proj_folder])

            # execute synthesis script
            script_path = config.get("Automation", "script_path")
            remote_cmd = "vivado -mode batch -nojournal -nolog -notrace -source " + script_path
            subprocess.call(["ssh", "-i", ".ssh/zedboard_autoconnect", "philipp@philipp-thinkpad-x250",
                             "'" + remote_cmd + "'"])
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
            logger.exception(msg="TransformationError raised, calling python implementation instead...")
            # clear cache of ctree framework
            subprocess.call(["ctree", "-cc"])
            ret = self.py_func(*args, **kwargs)
        #
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
