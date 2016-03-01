# ---------------------------------------------------------------------------
# logging
from os import path, getcwd
import logging

logging.basicConfig(filename='vhdl_sejits.log', level=logging.DEBUG)
LOG = logging.getLogger(__name__)
LOG.info("initializing sejits_ctree")

try:
    # python 2
    import ConfigParser as configparser
except ImportError:
    # python 3
    import configparser

CONFIG = configparser.ConfigParser()
DEFAULT_CFG_FILE_PATH = path.join(path.abspath(path.dirname(__file__)),
                                  "defaults.cfg")

LOG.info("reading default configuration from: %s", DEFAULT_CFG_FILE_PATH)

CONFIG.readfp(open(DEFAULT_CFG_FILE_PATH), filename="defaults.cfg")