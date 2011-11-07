from .config import USERNAME, PASSWORD, SCM
from .repositories import *
import optparse

def run():
	p = optparse.OptionParser()
	
	p.add_option('--username', '-u', dest='username', default=USERNAME)
	p.add_option('--password', '-p', dest='password', default=PASSWORD)
	p.add_option('--public', '-o', action='store_false', dest='private')
	p.add_option('--private', '-c', action='store_true', dest='private')
	p.add_option('--scm', '-s', dest='scm', default=SCM)

	options, arguments = p.parse_args()

	if arguments[0] == 'create':
		create_repository(arguments[1], options.username, options.password, 
				options.scm, options.private)
	elif arguments[0] == 'update':
		update_repository(options.username, arguments[1], options.password,
			scm=options.scm, private=options.private)
	elif arguments[0] == 'delete':
		delete_repository(options.username, arguments[1], options.password)
	
