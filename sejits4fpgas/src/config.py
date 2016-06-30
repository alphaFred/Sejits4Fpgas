from pkg_resources import resource_filename
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(resource_filename("sejits4fpgas", "app.config"))
