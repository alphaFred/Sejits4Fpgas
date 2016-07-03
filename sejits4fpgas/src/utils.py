import glob
import os

from sejits4fpgas.src.nodes import VhdlFile

# ---------------------------------------------------------------------------
STDLIBS = ["ieee", "ieee.std_logic_1164.all"]
# ---------------------------------------------------------------------------


def get_basic_blocks(path):
    prebuilt_files = []
    for fn in glob.glob(path + "*"):
        fname = os.path.basename(os.path.splitext(fn)[0])
        prebuilt_files.append(VhdlFile.from_prebuilt(name=fname, path=fn))
    return prebuilt_files
