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
PASSWORD = get_default(config, 'auth', 'password', None)
SCM = get_default(config, 'options', 'scm', 'hg')
PROTOCOL = get_default(config, 'options', 'protocol', 'https')

if PASSWORD and (os.stat(CONFIG_FILE).st_mode & 0o044):
    print ('****************************************************\n'
           '  Warning: config file is readable by other users.\n'
           '  If you are storing your password in this file,\n'
           '  it may not be secure\n'
           '****************************************************')
