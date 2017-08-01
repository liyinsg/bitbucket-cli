import os
from .repositories import get_repository

try:
    from configparser import SafeConfigParser as ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

def detect_scm(path='.'):
    git_path = os.path.join(path, '.git')
    hg_path = os.path.join(path, '.hg')
    # .git is a dir in the typical case, but can be a file for submodules (file points to actual git dir)
    if os.path.isdir(git_path) or os.path.isfile(git_path):
        return 'git'
    if os.path.isdir(hg_path):
        return 'hg'
    return ''


def gen_url(scm, protocol, username, reponame):
    templates = {
        'git': {
            'ssh': 'git@bitbucket.org:%s/%s.git',
            'https': 'https://bitbucket.org/%s/%s.git'
        },
        'hg': {
            'ssh': 'ssh://hg@bitbucket.org/%s/%s',
            'https': 'https://bitbucket.org/%s/%s'
        }
    }
    try:
        return templates[scm][protocol] % (username, reponame)
    except KeyError as ex:
        raise Exception('Key error while generating url. Unknown argument `%s`' % ex)


def clone(protocol, ownername, reponame, username, password):
    repo = get_repository(ownername, reponame, username, password)
    scm = repo['scm']
    url = gen_url(scm, protocol, ownername, reponame)
    os.system('%s clone %s' % (scm, url))


def pull(protocol, username, reponame):
    scm = detect_scm()
    url = gen_url(scm, protocol, username, reponame)
    if scm == 'git':
        os.system('git pull %s master' % url)
    elif scm == 'hg':
        os.system('hg pull %s' % url)


def push(protocol, username, reponame):
    scm = detect_scm()
    url = gen_url(scm, protocol, username, reponame)
    if scm == 'git':
        os.system('git push %s master' % url)
    elif scm == 'hg':
        os.system('hg push %s' % url)


def push_upstream(remotename='origin'):
    scm = detect_scm()

    if scm == 'git':
        os.system('git push --set-upstream %s master' % remotename)
    elif scm == 'hg':
        parser = ConfigParser()
        parser.read(['.hg/hgrc'])
        url = parser.get('paths', remotename)
        parser.set('paths', 'default', url)
        parser.set('paths', 'default-push', url)
        f = open('.hg/hgrc', 'w')
        parser.write(f)
        f.close()
        os.system('hg push')


def add_remote(protocol, username, reponame, remotename='origin'):
    scm = detect_scm()
    url = gen_url(scm, protocol, username, reponame)

    if scm == 'git':
        os.system('git remote add %s %s' % (remotename, url))
    elif scm == 'hg':
        parser = ConfigParser()
        parser.read(['.hg/hgrc'])
        if not parser.has_section('paths'):
            parser.add_section('paths')
        if not parser.has_option('paths', remotename):
            parser.set('paths', remotename, url)
            f = open('.hg/hgrc', 'w')
            parser.write(f)
            f.close()
        else:
            print("Error: remote %s already exists" % remotename)
