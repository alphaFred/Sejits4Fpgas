import ConfigParser
from pkg_resources import resource_filename

config = ConfigParser.SafeConfigParser()
config.read(resource_filename("sejits4fpgas", "app.config"))
