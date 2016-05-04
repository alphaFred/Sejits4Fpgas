""" """
import os
import glob
import logging
import numpy as np
from collections import namedtuple
#
from utils import CONFIG


logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "ENABLE_LOGGING")
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


VhdlSyntData = namedtuple("VhdlSyntData", ["main_file", "file_paths"])


class VhdlSynthModule(object):
    """Manages synthetisation of generated AST."""

    def __init__(self):
        """Initialize VhdlSynthModule instance."""
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
            print "Concrete Specialized Function called on x86"
            return 0

    def _link_in(self, submodule):
        self._linked_files.append(submodule)

    def get_callable(self, entry_point_name, entry_point_typesig):
        """Return a python callable that redirects to hardware."""
        self._link_to_vivado_project()
        self._activate()
        return self

    def _link_to_vivado_project(self):
        """Link all files to vivado template project."""
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
        """Activate synthesis subprocess."""
        # copy template project to synthesis directory
        # copy all vhdl files to template project ip folder
        # integrate vhdl files into templare project
        #   multiply process pipeline according to input width and data width
        #   integrate and connect pipelines into axi stream ip
        libHwIntfc = c.cdll.LoadLibrary('/home/linaro/libHwIntfc.so')
        libHwIntfc.process1d_img.argtypes = [ctl.ndpointer(np.uint32, ndim=1, flags='C'), c.c_uint]
        self.hw_interface = libHwIntfc.process1d_img
