from .config import USERNAME, PASSWORD, SCM, PROTOCOL
from .repositories import *
from . import scm
import argparse
import os

def run():
	p = argparse.ArgumentParser(description='Interact with BitBucket')
	
	p.add_argument('--username', '-u', dest='username', default=USERNAME,
		help='your bitbucket username')
	p.add_argument('--password', '-p', dest='password', default=PASSWORD,
		help='your bitbucket password')
	p.add_argument('--public', '-o', action='store_false', dest='private',
		help='make this repo public')
	p.add_argument('--private', '-c', action='store_true', dest='private',
		help='make this repo private')
	p.add_argument('--scm', '-s', dest='scm', default=SCM,
		help='which scm to use (git|hg)')
	p.add_argument('--protocol', '-P', dest='protocol', default=PROTOCOL,
		help='which network protocol to use (https|ssh)')
	p.add_argument('subcommand', 
		help='the subcommand as described in the README file')
	p.add_argument('subargs', nargs='*',
		help='the subcommand arguments')

	args = p.parse_args()
	subcom = args.subcommand
	subargs = args.subargs

	if not subcom:
		p.print_usage()
		exit()

	if subcom == 'create':
		create_repository(subargs[0], args.username, args.password, 
				args.scm, args.private)
	elif subcom == 'update':
		update_repository(args.username, subargs[0], args.password,
			scm=args.scm, private=args.private)
	elif subcom == 'delete':
		delete_repository(args.username, subargs[0], args.password)
	elif subcom == 'clone':
		scm.clone(args.protocol, subargs[0], subargs[1], 
			args.username, args.password)
	elif subcom == 'pull':
		scm.pull(args.protocol, subargs[0], subargs[1])
	elif subcom == 'create-from-local':
		scm_type = scm.detect_scm()
		if scm_type:
			reponame = os.path.basename(os.getcwd())
			try:
				create_repository(reponame, args.username, args.password,
					scm_type, args.private)
			except Exception, e: print e
			scm.push(args.protocol, args.username, reponame)
		else:
			print('Could not detect a git or hg repo in your current directory.')
	elif subcom == 'download':
		download_file(subargs[0], subargs[1], subargs[2], args.password)
        print "Successfully downloaded " + subargs[2]
