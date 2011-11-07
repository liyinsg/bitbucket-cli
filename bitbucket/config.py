import os
from ConfigParser import SafeConfigParser as ConfigParser

CONFIG_FILE = os.path.expanduser('~/.bitbucket')
BASE_URL = 'https://api.bitbucket.org/1.0/'

try:
	config = ConfigParser()
	config.read([CONFIG_FILE])

	USERNAME = config.get('auth', 'username')
	PASSWORD = config.get('auth', 'password')
except:
	USERNAME = ''
	PASSWORD = ''
