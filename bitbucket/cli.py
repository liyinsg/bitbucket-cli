from .config import USERNAME, PASSWORD, SCM, PROTOCOL
from .repositories import *
from . import scm
import argparse
import getpass
import sys
import os


def password(func):
    def decorator(args):
        if args.password == "":
            args.password = getpass.getpass('password: ')
        func(args)
    return decorator


@password
def create_command(args):
    create_repository(args.reponame, 
                      args.username, 
                      args.password, 
                      args.scm, 
                      args.private)

@password
def update_command(args):
    update_repository(args.username, 
                      args.reponame, 
                      args.password, 
                      scm=args.scm, 
                      private=args.private)

@password
def delete_command(args):
    delete_repository(args.username, 
                      args.reponame, 
                      args.password)

@password
def clone_command(args):
    scm.clone(args.protocol, 
              args.ownername, 
              args.reponame, 
              args.username, 
              args.password)

def pull_command(args):
    scm.pull(args.protocol, 
             args.ownername, 
             args.reponame)

@password
def create_from_local(args):
    scm_type = scm.detect_scm()
    if scm_type:
        reponame = os.path.basename(os.getcwd()).lower()
        try:
            create_repository(reponame, args.username, args.password,
                scm_type, args.private)
        except Exception, e: 
            print e
        scm.add_remote(args.protocol, args.username, reponame)
        scm.push_upstream()
    else:
        print('Could not detect a git or hg repo in your current directory.')
            

def download_command(args):
    download_file(args.ownername, args.reponame, args.filename, 
            args.username, args.password)
    print "Successfully downloaded " + args.filename 


def run():
    # root command parser
    p = argparse.ArgumentParser(description='Interact with BitBucket')
    
    def add_standard_args(parser, args_to_add):
        if 'username' in args_to_add:
            parser.add_argument('--username', '-u', default=USERNAME,
                help='your bitbucket username')
        if 'password' in args_to_add:
            parser.add_argument('--password', '-p', default=PASSWORD,
                help='your bitbucket password')
        if 'private' in args_to_add:
            parser.add_argument('--private', '-c', action='store_true', default=False, 
                help='make this repo private')
        if 'scm' in args_to_add:
            parser.add_argument('--scm', '-s', default=SCM,
                help='which scm to use (git|hg)')
        if 'protocol' in args_to_add:
            parser.add_argument('--protocol', '-P', default=PROTOCOL,
                help='which network protocol to use (https|ssh)')
        if 'ownername' in args_to_add:
            parser.add_argument('ownername',
                    type=str,
                    help='bitbucket account name')
        if 'reponame' in args_to_add:
           parser.add_argument('reponame', 
                    type=str,
                    help='the bitbucket repository name')

    subparsers = p.add_subparsers()

    # create command parser
    create_cmd_parser = subparsers.add_parser('create')
    add_standard_args(create_cmd_parser, 'username password protocol private scm reponame')
    create_cmd_parser.set_defaults(func=create_command)

    # update command parser
    update_cmd_parser = subparsers.add_parser('update')
    add_standard_args(update_cmd_parser, 'username password protocol private scm ownername reponame')
    update_cmd_parser.set_defaults(func=update_command)

    # delete command parser
    delete_cmd_parser = subparsers.add_parser('delete')
    add_standard_args(delete_cmd_parser, 'username reponame password')
    delete_cmd_parser.set_defaults(func=delete_command)

    # clone command parser
    clone_cmd_parser = subparsers.add_parser('clone')
    add_standard_args(clone_cmd_parser, 'username password protocol ownername reponame')
    clone_cmd_parser.set_defaults(func=clone_command)

    # pull command parser
    pull_cmd_parser = subparsers.add_parser('pull')
    add_standard_args(pull_cmd_parser, 'protocol ownername reponame')
    pull_cmd_parser.set_defaults(func=pull_command)

    # create-from-local command parser
    create_from_local_cmd_parser = subparsers.add_parser('create_from_local')
    add_standard_args(create_from_local_cmd_parser, 'username password protocol private scm ownername reponame')
    create_from_local_cmd_parser.set_defaults(func=create_from_local)

    # download command parser
    download_cmd_parser = subparsers.add_parser('download')
    add_standard_args(download_cmd_parser, 'username password ownername reponame')
    download_cmd_parser.add_argument('filename', type=str,
        help='the file you want to download')
    download_cmd_parser.set_defaults(func=download_command)

    try:
        args = p.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        sys.exit(0)
