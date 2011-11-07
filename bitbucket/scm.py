import os
import subprocess

def detect_scm(path='.'):
	git_path = os.path.join(path, '.git')
	hg_path = os.path.join(path, '.hg')
	if os.path.isdir(git_path):
		return 'git'
	if os.path.isdir(hg_path):
		return 'hg'
	return ''

def gen_url(scm, method, username, reponame):
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
	if scm not in {'git', 'hg'} or method not in {'ssh', 'https'}:
		return ''
	return templates[scm][method] % (username, reponame)

def clone(scm, method, username, reponame):
	url = gen_url(scm, method, username, reponame)
	os.system('%s clone %s' % (scm, url))

def pull(method, username, reponame):
	scm = detect_scm()
	url = get_url(scm, method, username, reponame)
	if scm == 'git':
		os.system('git pull %s master' % url)
	elif scm == 'hg':
		os.system('hg pull %s' % url)

def push(method, username, reponame):
	scm = detect_scm()
	url = get_url(scm, method, username, reponame)
	if scm == 'git':
		os.system('git push %s master' % url)
	elif scm == 'hg':
		os.system('hg push %s' % url)
	
