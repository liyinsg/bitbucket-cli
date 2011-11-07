from .config import USERNAME, PASSWORD, SCM
from .repositories import *
from . import scm
import optparse
import os

def run():
	p = optparse.OptionParser()
	
	p.add_option('--username', '-u', dest='username', default=USERNAME,
		help='your bitbucket username')
	p.add_option('--password', '-p', dest='password', default=PASSWORD,
		help='your bitbucket password')
	p.add_option('--public', '-o', action='store_false', dest='private',
		help='make this repo public')
	p.add_option('--private', '-c', action='store_true', dest='private',
		help='make this repo private')
	p.add_option('--scm', '-s', dest='scm', default=SCM,
		help='which scm to use (git|hg)')

	options, arguments = p.parse_args()

	if len(arguments) == 0:
		p.print_usage()
		exit()

	if arguments[0] == 'create':
		create_repository(arguments[1], options.username, options.password, 
				options.scm, options.private)
	elif arguments[0] == 'update':
		update_repository(options.username, arguments[1], options.password,
			scm=options.scm, private=options.private)
	elif arguments[0] == 'delete':
		delete_repository(options.username, arguments[1], options.password)
	elif arguments[0] == 'clone':
		scm.clone('https', arguments[1], arguments[2])
	elif arguments[0] == 'pull':
		scm.pull('https', arguments[1], arguments[2])
	elif arguments[0] == 'create-from-local':
		scm_type = scm.detect_scm()
		if scm_type:
			reponame = os.path.basename(os.getcwd())
			try:
				create_repository(reponame, options.username, options.password,
					scm_type, options.private)
			except Exception, e: print e
			scm.push('ssh', options.username, reponame)
		else:
			print('Could not detect a git or hg repo in your current directory.')
	
