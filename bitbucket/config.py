import os
import ConfigParser


def get_default(config, section, key, default=''):
    try:
        return config.get(section, key)
    except ConfigParser.NoSectionError:
        return default
    except ConfigParser.NoOptionError:
        return default

# https://github.com/scrapy/scrapy/blob/master/scrapy/utils/conf.py#L66
def closest_bitbucket_file(path='.', prevpath=None):
    """Return the path to the closest .bitbucket file by traversing the current
    directory and its parents
    """
    if path == prevpath:
        return ''
    path = os.path.abspath(path)
    cfgfile = os.path.join(path, '.bitbucket')
    if os.path.exists(cfgfile):
        return cfgfile
    return closest_bitbucket_file(os.path.dirname(path), path)


CONFIG_FILE = closest_bitbucket_file() or os.path.expanduser('~/.bitbucket')
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
