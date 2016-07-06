import glob
import os
from sejits4fpgas.src.config import config
from pkg_resources import resource_filename

from sejits4fpgas.src.nodes import VhdlFile

# ---------------------------------------------------------------------------
STDLIBS = ["ieee", "ieee.std_logic_1164.all"]
# ---------------------------------------------------------------------------


def get_basic_blocks():
    prebuilt_files = []
    path = resource_filename("sejits4fpgas", config.get("Paths", "basic_block_path"))
    for fn in glob.glob(path + "*"):
        fname = os.path.basename(os.path.splitext(fn)[0])
        prebuilt_files.append(VhdlFile.from_prebuilt(name=fname, path=fn))
    return prebuilt_files
