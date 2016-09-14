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
from sejits4fpgas.src.utils import BITCACHE
from sejits4fpgas.src.vhdl_ctree.frontend import get_ast
from sejits4fpgas.src.vhdl_ctree.c.nodes import MultiNode
from sejits4fpgas.src.vhdl_ctree.jit import LazySpecializedFunction
from sejits4fpgas.src.errors import TransformationError
from collections import namedtuple
#
from sejits4fpgas.src.config import config

logger = logging.getLogger(__name__)
logger.disabled = config.getboolean("Logging", "disable_logging")
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
        # ---------------------------------------------------------------------
        logger.info("Initialized new {} instance".format(self.__class__.__name__))
        # ---------------------------------------------------------------------

        self._linked_files = []
        self.project_hash = None

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
            libHwIntfc.process1d_img.argtypes = [ctl.ndpointer(np.uint32, ndim=1, flags='C'), c.c_uint]
            libHwIntfc.process3d_img.argtypes = [c.c_void_p, c.c_uint, c.c_uint]
            libHwIntfc.process_img.argtypes = [c.c_void_p, c.c_uint, c.c_uint, c.c_uint]
            self.hw_interface = libHwIntfc

    def set_project_hash(self, project_hash):
        self.project_hash = project_hash

    def __call__(self, *args, **kwargs):
        """Redirect call to python or vhdl kernel."""
        if os.uname()[-1] == "armv7l":
            if len(args) > 1:
                raise TransformationError("Multiple input data currently not supported by the hardware")
            #
            self._program_bitfile(self.project_hash)
            #
            if len(args[0].shape) <= 2:
                mod_arg = args[0].astype(np.uint32)
                orig_arg_shape = mod_arg.shape
                #
                mod_arg = mod_arg.flatten()
                #self.hw_interface.process1d_img(mod_arg, np.uint(len(mod_arg)))
                self.hw_interface.process_img(c.c_void_p(mod_arg.ctypes.data), np.uint(len(mod_arg)), orig_arg_shape[0],
                                              orig_arg_shape if orig_arg_shape < 1024 else 1024)
            else:
                orig_arg_shape = args[0].shape
                #
                mod_arg = args[0].flatten()
                # self.hw_interface.process3d_img(c.c_void_p(mod_arg.ctypes.data), len(mod_arg), 1)
                self.hw_interface.process_img(c.c_void_p(mod_arg.ctypes.data), np.uint(len(mod_arg))/4, orig_arg_shape[0],
                                              orig_arg_shape if orig_arg_shape < 1024 else 1024)
            #
            out_img = mod_arg.astype(np.uint8)
            out_img = out_img.reshape(orig_arg_shape)
            #
            return out_img
        else:
            #raise TransformationError("Call to HW only on ARM")
            return args[0]

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
        #
        if os.uname()[-1] == "armv7l":
            if self.project_hash not in BITCACHE:
                #
                logger.log(level=logging.INFO, msg="Cache miss for bitstream file")
                #
                self._synthesize_vivado_proj()
                self._store_bitfile(self.project_hash)
                # add new bitstream file to cache folder
                BITCACHE[self.project_hash] = resource_filename("sejits4fpgas", config.get("Paths", "bitfile_path")) + self.project_hash + ".bit"
            else:
                logger.log(level=logging.INFO, msg="Cache hit for bitstream file")
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
            host_proj_folder = config.get("Automation", "host_v_proj_path")

            logger.log(level=logging.INFO, msg="Copy .vhd files to " + connection_str + host_proj_folder + "template_project.srcs/sources_1/new/")

            try:
                for file in glob.glob(self.v_proj_fol + "template_project.srcs/sources_1/new/*"):
                    logger.log(level=logging.DEBUG, msg="Copying {0} to remote host".format(file))
                    subprocess.check_call(["scp", "-i", "/home/linaro/.ssh/zedboard_autoconnect", file,
                                     connection_str + host_proj_folder + "template_project.srcs/sources_1/new/"])

                # move tcl script to remote host
                logger.log(level=logging.INFO, msg="Copy .tcl script to " + connection_str + host_proj_folder)
                tcl_file_path = self.v_proj_fol + "template_project.tcl"
                subprocess.check_call(["scp", "-i", "/home/linaro/.ssh/zedboard_autoconnect", tcl_file_path,
                                 connection_str + host_proj_folder])

                # execute synthesis script
                script_path = config.get("Automation", "script_path")
                subprocess.check_call(["ssh", "-i", "/home/linaro/.ssh/zedboard_autoconnect",
                                       connection_str + "./vivado_automation.sh"])
            except subprocess.CalledProcessError:
                logger.log(level=logging.ERROR, msg="Error while synthesizing FPGA")
                raise TransformationError(msg="Error while synthesizing FPGA")
            else:
                logger.log(level=logging.INFO, msg="Successfully synthesized FPGA")
        else:
            logger.log(level=logging.INFO, msg="Can not start syntehtisation on: {}".format(os.uname()[-1]))
            pass

    def _store_bitfile(self, bitfile_hash):
        connection_str = config.get("Automation", "user") + "@" + config.get("Automation", "host") + ":"

        host_proj_folder = config.get("Automation", "host_v_proj_path")
        bitfile_folder_path = resource_filename("sejits4fpgas", config.get("Paths", "bitfile_path"))

        try:
            # copy generated bit file to client
            subprocess.check_call(["scp", "-i", "/home/linaro/.ssh/zedboard_autoconnect",
                             connection_str + host_proj_folder + "template_project.runs/impl_1/top.bit",
                             bitfile_folder_path + str(bitfile_hash) + ".bit"])
        except subprocess.CalledProcessError:
            logger.log(level=logging.ERROR, msg="Error while storing FPGA-bitfile")
            raise TransformationError(msg="Error while storing FPGA-bitfile")
        else:
            logger.log(level=logging.INFO, msg="Successfully stored FPGA-bitfile")

    def _program_bitfile(self, bitfile_name):
        try:
            subprocess.check_call("cat " +
                                  resource_filename("sejits4fpgas", config.get("Paths", "bitfile_path")) +
                                  bitfile_name + ".bit > /dev/xdevcfg", shell=True)
        except subprocess.CalledProcessError:
            logger.log(level=logging.ERROR, msg="Error while programming FPGA")
            raise TransformationError(msg="Error while programming FPGA")
        else:
            logger.log(level=logging.INFO, msg="Successfully programmed FPGA")


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
        try:
            ret = super(VhdlLazySpecializedFunction, self).__call__(*args, **kwargs)
        except TransformationError:
            logger.exception(msg="TransformationError raised, calling python implementation instead...")
            # clear cache of ctree framework
            # subprocess.call(["ctree", "-cc"])
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
