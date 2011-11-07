import os
import ConfigParser

def get_default(config, section, key, default=''):
	try:
		return config.get(section, key)
	except ConfigParser.NoSectionError:
		return default
	except ConfigParser.NoOptionError:
		return default

CONFIG_FILE = os.path.expanduser('~/.bitbucket')

config = ConfigParser.SafeConfigParser()
config.read([CONFIG_FILE])

USERNAME = get_default(config, 'auth', 'username')
PASSWORD = get_default(config, 'auth', 'password')
SCM = get_default(config, 'options', 'scm', 'hg')

