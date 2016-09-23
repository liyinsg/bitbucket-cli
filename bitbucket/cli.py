import os
import re
import sys
import getpass
import argparse
import scm
from .repositories import download_file
from .repositories import create_repository
from .repositories import update_repository
from .repositories import delete_repository
from .repositories import get_user_repos
from .repositories import set_privilege
from .repositories import set_group_privilege
from .repositories import open_pull
from .config import USERNAME, PASSWORD, SCM, PROTOCOL
from requests.exceptions import HTTPError
from requests.status_codes import _codes as status_codes


def password(func):
    # very basic password input
    def decorator(args):
        if not args.username:
            args.username = raw_input('username: ')
        if not args.password:
            args.password = getpass.getpass('password: ')
        func(args)
    return decorator


def display_repo_info(repo_info, owner=None, reposlug=None):
    repo_info['private'] = '-' if 'is_private' in repo_info else '+'
    if 'scm' not in repo_info:
        repo_info['scm'] = scm.detect_scm()

    if owner:
        repo_info['owner'] = owner
    if reposlug:
        repo_info['slug'] = reposlug

    print '[{private}{scm: >4}] {owner}/{slug}'.format(**repo_info)


@password
def create_command(args):
    result = create_repository(args.reponame,
                               args.username,
                               args.password,
                               args.scm,
                               args.private,
                               args.owner)
    print ''
    print 'Repository successfully created.'
    display_repo_info(result)


@password
def update_command(args):
    result = update_repository(args.username,
                      args.reponame,
                      args.password,
                      owner = args.owner,
                      is_private=args.private)
    print ''
    print 'Repository successfully updated.'
    display_repo_info(result)


@password
def delete_command(args):
    delete_repository(args.username,
                      args.reponame,
                      args.password,
                      args.owner)
    owner = args.owner or args.username
    print '{0}/{1} was deleted.'.format(owner, args.reponame)


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
        create_repository(reponame, args.username, args.password,
                          scm_type, args.private, args.owner)
        scm.add_remote(args.protocol, args.owner or args.username, reponame)
        scm.push_upstream()
    else:
        print ('Could not detect a git or hg repo in your current directory.')

def add_remote(args):
    scm.add_remote(args.protocol, args.username, args.reponame,
                    args.remotename)

def download_command(args):
    download_file(args.ownername, args.reponame, args.filename,
                  args.username, args.password)
    print "Successfully downloaded " + args.filename


@password
def list_command(args):
    response = get_user_repos(args.username, args.password)
    repo_count = 0
    filters = []
    # filter for public and/or private repo
    filters.append(lambda repo: (args.list_public and not repo.get('is_private', False)) or
                                (args.list_private and repo.get('is_private', False)) or
                                (args.list_public == args.list_private))
    # filter for type of repository
    filters.append(lambda repo: args.scm == 'all' or repo['scm'] == args.scm)
    # filter name on regular expression
    exp = re.compile(args.expression, re.IGNORECASE)
    filters.append(lambda repo: exp.search(repo['name']))

    for repo in response:
        if all([filter(repo) for filter in filters]):
            repo_count += 1
            display_repo_info(repo)

    print '{0} repositories listed'.format(repo_count)


@password
def open_pull_command(args):
    reponame = os.path.basename(os.getcwd()).lower() if not hasattr(args, 'reponame') or not args.reponame else args.reponame
    result = open_pull(args.username,
                       args.password,
                       args.owner,
                       reponame,
                       args.source,
                       args.destination,
                       args.title,
                       args.description,
                       args.close_source_branch)
    print "Pull request successfully opened. Link: {0}".format(
            result["links"]["html"]["href"])


@password
def privilege_command(args):
    set_privilege(args.ownername, args.reponame, args.privilege,
                  args.privilege_account, args.username, args.password)

@password
def group_privilege_command(args):
    set_group_privilege(args.ownername, args.reponame, args.privilege,
                        args.teamname, args.groupname,
                        args.username, args.password)

def run():
    # root command parser
    p = argparse.ArgumentParser(description='Interact with BitBucket',
            usage='bitbucket <command> [<args>]',
            epilog='See `bitbucket <command> --help` for more information on a specific command.')

    def add_standard_args(parser, args_to_add):
        # each command has a slightly different use of these arguments,
        # therefore just add the ones specified in `args_to_add`.
        if 'username' in args_to_add:
            parser.add_argument('--username', '-u', default=USERNAME,
                            help='your bitbucket username')
        if 'password' in args_to_add:
            parser.add_argument('--password', '-p', default=PASSWORD,
                            help='your bitbucket password')
        if 'owner' in args_to_add:
            parser.add_argument('--owner', '-w', default='',
                            help='repository owner')
        if 'private' in args_to_add:
            parser.add_argument('--private', '-c', action='store_true',
                            dest='private',
                            default=True,
                            help='make this repo private')
        if 'public' in args_to_add:
            parser.add_argument('--public ', '-o', action='store_false',
                            dest='private',
                            default=True,
                            help='make this repo public')
        if 'scm' in args_to_add:
            parser.add_argument('--scm', '-s', default=SCM,
                            help='which scm to use (git|hg)')
        if 'protocol' in args_to_add:
            parser.add_argument('--protocol', '-P', default=PROTOCOL,
                            help=('which network protocol '
                                  'to use (https|ssh)'))
        if 'ownername' in args_to_add:
            parser.add_argument('ownername',
                            type=str,
                            help='bitbucket account name')
        if 'reponame' in args_to_add:
            parser.add_argument('reponame',
                            type=str,
                            default=None,
                            help='the bitbucket repository name')
        parser.add_argument('--debug', action='store_true', default=False)

    command_names = ('create', 'update', 'delete', 'clone', 'create_from_local', 'pull_request',
                     'pull', 'download', 'list', 'privilege')
    # SUBPARSER
    subp = p.add_subparsers(title='Commands', metavar='\n  '.join(command_names))

    # CREATE COMMAND PARSER
    create_cmd_parser = subp.add_parser('create',
                        usage=('bitbucket create [-h] [--username USERNAME]\n'
                               '                        [--password PASSWORD] [--private | --public]\n'
                               '                        [--scm SCM] [--protocol PROTOCOL]\n'
                               '                        [--owner OWNER]\n'
                               '                        reponame'),
                        description='create a new bitbucket repository')
    add_standard_args(create_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'private',
                       'public',
                       'scm',
                       'owner',
                       'reponame'))
    create_cmd_parser.set_defaults(func=create_command)

    #
    # UPDATE COMMAND PARSER
    #
    update_cmd_parser = subp.add_parser('update',
                            usage=('bitbucket update [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        [--private | --public]\n'
                                   '                        [--owner OWNER]\n'
                                   '                        reponame'),
                            description='update an existing bitbucket repository')
    add_standard_args(update_cmd_parser,
                      ('username',
                       'password',
                       'private',
                       'public',
                       'owner',
                       'reponame'))
    update_cmd_parser.set_defaults(func=update_command)

    #
    # DELETE COMMAND PARSER
    #
    delete_cmd_parser = subp.add_parser('delete',
                            usage=('bitbucket delete [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        [--owner OWNER]\n'
                                   '                        reponame'),
                            description='delete an existing bitbucket repository')
    add_standard_args(delete_cmd_parser,
                      ('username',
                       'reponame',
                       'password',
                       'owner'))
    delete_cmd_parser.set_defaults(func=delete_command)

    #
    # CLONE COMMAND PARSER
    #
    clone_cmd_parser = subp.add_parser('clone',
                            usage=('bitbucket clone [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        [--protocol PROTOCOL]\n'
                                   '                        ownername\n'
                                   '                        reponame'),
                            description='clone a bitbucket repository')
    add_standard_args(clone_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'ownername',
                       'reponame'))
    clone_cmd_parser.set_defaults(func=clone_command)

    #
    # PULL COMMAND PARSER
    #
    pull_cmd_parser = subp.add_parser('pull',
                            usage=('bitbucket pull [-h] [--protocol PROTOCOL]\n'
                                   '                        ownername\n'
                                   '                        reponame'),
                            description='pull....')
    add_standard_args(pull_cmd_parser,
                      ('protocol',
                       'ownername',
                       'reponame'))
    pull_cmd_parser.set_defaults(func=pull_command)

    #
    # CREATE-FROM-LOCAL COMMAND PARSER
    #
    create_from_local_cmd_parser = subp.add_parser('create_from_local',
                            usage=('bitbucket create_from_local [-h]\n'
                                   '                        [--username USERNAME]\n'
                                   '                        [--password PASSWORD] [--private | --public]\n'
                                   '                        [--scm SCM] [--protocol PROTOCOL]\n'
                                   '                        [--owner OWNER]\n'),
                            description='create a bitbucket repo from existing local repo')
    add_standard_args(create_from_local_cmd_parser,
                      ('username',
                       'password',
                       'protocol',
                       'private',
                       'public',
                       'scm',
                       'owner'))
    create_from_local_cmd_parser.set_defaults(func=create_from_local)

    #
    # OPEN-pull_request COMMAND PARSER
    #
    # ex: bb pull_request [opens a pull request for the current branch to master]
    # ex: bb pull_request master [opens a pull request for the current branch to master]
    # ex: bb pull_request master feature/new-feature [opens a pull request for feature/new-feature to master]
    open_pull_cmd_parser = subp.add_parser('pull_request',
                             usage=('bitbucket pull_request [-h]\n'
                                    '                        [--username USERNAME]\n'
                                    '                        [--password PASSWORD] [--private | --public]\n'
                                    '                        [--owner OWNER]\n'
                                    '                        [--title TITLE]\n'
                                    '                        [--description DESCRIPTION]\n'
                                    '                        [--reponame REPOSITORY NAME]\n'
                                    '                        [--close-branch]\n'
                                    '                        source\n'
                                    '                        destination\n'),
                             description='open a bitbucket pull request for current repo from source to destination')
    open_pull_cmd_parser.add_argument('source', default='',
                                      help='the source branch')
    open_pull_cmd_parser.add_argument('destination', default='master',
                                      help='the destination branch')
    open_pull_cmd_parser.add_argument('--title', '-t', required=False, default='',
                                      help='the title for the pull request')
    open_pull_cmd_parser.add_argument('--description', '-d', required=False, default='This request was automatically generated.',
                                      help='the description for the pull request')
    open_pull_cmd_parser.add_argument('--reponame', '-r', required=False, default='',
                                      help='the repository for this pull request')
    open_pull_cmd_parser.add_argument('--close-branch', '-cb', required=False, action='store_true', default=False,
                                      dest='close_source_branch',
                                      help='close the branch when the pull request is merged')
    add_standard_args(open_pull_cmd_parser, ('owner', 'username', 'password'))
    open_pull_cmd_parser.set_defaults(func=open_pull_command)

    #
    # DOWNLOAD COMMAND PARSER
    #
    download_cmd_parser = subp.add_parser('download',
                            usage=('bitbucket download [-h] [--username USERNAME]\n'
                                   '                        [--password PASSWORD]\n'
                                   '                        ownername\n'
                                   '                        reponame\n'
                                   '                        filename'),
                            description='download a file from a bitbucket repo')
    add_standard_args(download_cmd_parser,
                      ('username',
                       'password',
                       'ownername',
                       'reponame'))
    download_cmd_parser.add_argument('filename', type=str,
                                     help='the file you want to download')
    download_cmd_parser.set_defaults(func=download_command)

    #
    # LIST COMMAND PARSER
    #
    list_cmd_parser = subp.add_parser('list',
                            usage=('bitbucket list [-h] [--username USERNAME]\n'
                                   '                      [--password PASSWORD]\n'
                                   '                      [--public]\n'
                                   '                      [--private]\n'
                                   '                      [--scm SCM]\n'
                                   '                      [--expression EXPRESSION]'),
                            description='list all bitbucket repos')
    add_standard_args(list_cmd_parser,
                      ('username',
                       'password'))
    list_cmd_parser.set_defaults(func=list_command)
    list_cmd_parser.add_argument('--private', '-c', action='store_true',
              dest='list_private',
              default=False,
              help='list private repositories only.')
    list_cmd_parser.add_argument('--public ', '-o', action='store_true',
              dest='list_public',
              default=False,
              help='list public repositories only.')
    list_cmd_parser.add_argument('--scm', '-s', default='all',
              help='list only the given scm (git|hg)')
    list_cmd_parser.add_argument('--expression', '-e', default='.*',
              help='list only repository names matching expression')


    #
    # PRIVILEGE COMMAND PARSER
    #
    privilege_cmd_parser = subp.add_parser('privilege',
                            usage=('bitbucket privilege [-h]\n'
                                   '                    [--username USERNAME]\n'
                                   '                    [--password PASSWORD]\n'
                                   '                    ownername\n'
                                   '                    reponame\n'
                                   '                    privilege_account\n'
                                   '                    privilege'),
                            description='update account privilege on an existing repo')
    add_standard_args(privilege_cmd_parser,
                      ('username',
                       'password',
                       'ownername',
                       'reponame'))
    privilege_cmd_parser.add_argument('privilege_account', type=str,
                                      help='the account you want to change')
    privilege_cmd_parser.add_argument('privilege', choices=['read', 'write', 'admin', 'none'],
                                      help='the privilege to grant')
    privilege_cmd_parser.set_defaults(func=privilege_command)

    #
    # GROUP-PRIVILEGE COMMAND PARSER
    #
    group_privilege_cmd_parser = subp.add_parser('group-privilege',
                                  usage=('bitbucket group-privilege [-h]\n'
                                         '                          [--username USERNAME]\n'
                                         '                          [--password PASSWORD]\n'
                                         '                          ownername\n'
                                         '                          reponame\n'
                                         '                          teamname\n'
                                         '                          groupname\n'
                                         '                          privilege\n'),
                                  description='update group privilege on an existing repo')
    add_standard_args(group_privilege_cmd_parser,
                      ('username',
                       'password',
                       'ownername',
                       'reponame'))
    group_privilege_cmd_parser.add_argument('teamname', type=str,
                                            help='the team account that has the group')
    group_privilege_cmd_parser.add_argument('groupname', type=str,
                                            help='the group you want to change')
    group_privilege_cmd_parser.add_argument('privilege', choices=['read', 'write', 'admin', 'none'],
                                            help='the privilege to grant')
    group_privilege_cmd_parser.set_defaults(func=group_privilege_command)

    #
    # Add Remote Command
    #

    add_remote_cmd_parser = subp.add_parser('add_remote',
            usage = ('bitbucket add_remote [-h]\n'
                     '                     [--username USERNAME]\n'
                     '                     [--password PASSWORD]\n'
                     '                     ownername\n'
                     '                     reponame\n'
                     '                     [--protocol PROTOCOL]\n'
                     '                     [--remote REMOTE]\n'),
                     description='add remote url')
    add_standard_args(add_remote_cmd_parser,
                        ('username', 'password',
                         'ownername', 'reponame',
                         'protocol'))
    add_remote_cmd_parser.add_argument('--remote', '-r',
                    dest='remotename', default='origin',
                    help = 'the name of the remote')
    add_remote_cmd_parser.set_defaults(func=add_remote)

    def debug_print_error(args):
        if args and args.debug:
            import traceback
            print '-' * 60
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_tb(exc_tb)
            print '-' * 60

    def print_http_error(ex):
        import re
        http_err_code = ex.response.status_code
        http_err = status_codes.get(http_err_code, [''])[0]
        print '\nRequest Error {0}: {1}'.format(http_err_code, http_err.replace('_', ' '))
        # Errros are being sent back as html, so let's strip
        # out the markup to make it a bit more readable on the
        # commandline.
        msg = re.sub('\<[^\>]+\>', ' ', ex.response.content)
        msg = re.sub(' +', ' ', msg)
        msg = msg.strip()
        if msg:
            print msg

    args = None

    try:
        args = p.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        pass
    except HTTPError as ex:
        # If we get this, then we know it's something with requests
        print_http_error(ex)
        debug_print_error(args)
        sys.exit(1)
