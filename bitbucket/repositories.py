import json
import requests
from requests.auth import HTTPDigestAuth

BASE_URL = 'https://api.bitbucket.org/1.0/'

def _optional_auth_get(url, username='', password='', **kwargs):
    if password:
        return requests.get(url, auth=(username, password), **kwargs)
    return requests.get(url, **kwargs)

def _json_or_error(r):
    if r.status_code != 200:
        r.raise_for_status()
    return json.loads(r.content)

def get_user_repos(username, password=''):
    url = BASE_URL + 'user/repositories/'
    r = requests.get(url, auth=(username, password))
    return _json_or_error(r)

def search_repositories(name):
    url = BASE_URL + 'repositories/'
    r = requests.get(url, params={'name': name})
    return _json_or_error(r)

def get_repository(ownername, repo_slug, username, password=''):
    url = BASE_URL + 'repositories/%s/%s/' % (ownername, repo_slug)
    r = _optional_auth_get(url, username, password)
    return _json_or_error(r)

def get_tags(ownername, repo_slug, username, password=''):
    url = BASE_URL + 'repositories/%s/%s/tags/' % (ownername, repo_slug)
    r = _optional_auth_get(url, username, password)
    return _json_or_error(r)

def get_branches(ownername, repo_slug, username, password=''):
    url = BASE_URL + 'repositories/%s/%s/branches/' % (ownername, repo_slug)
    r = _optional_auth_get(url, username, password)
    return _json_or_error(r)

def create_repository(name, username, password, scm='hg', is_private=True):
    url = BASE_URL + 'repositories/'
    r = requests.post(url, data={'name': name, 'scm': scm, 
            'is_private': str(bool(is_private))}, auth=(username, password))
    return _json_or_error(r)

def update_repository(username, repo_slug, password, **opts):
    url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
    if opts.get('is_private'): opts['is_private'] = 'True'
    r = requests.put(url, data=opts, auth=(username, password))
    return _json_or_error(r)

def delete_repository(username, repo_slug, password):
    url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
    r = requests.delete(url, auth=(username, password))
    return r.status_code == 204

def download_file(repo_user, repo_slug, filename, username='', password=''):
    url = 'https://bitbucket.org/%s/%s/downloads/%s' % \
        (repo_user, repo_slug, filename)
    
    print url
    if password:
        r = requests.get(url, auth=HTTPDigestAuth(username, password))
    else:
        r = requests.get(url)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)
    else:
        r.raise_for_status()
