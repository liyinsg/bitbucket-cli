import json
import requests
from requests.auth import HTTPDigestAuth

BASE_URL = 'https://api.bitbucket.org/1.0/'


def _optional_auth_get(url, username='', password='', **kwargs):
    if password:
        return requests.get(url, auth=(username, password), **kwargs)
    return requests.get(url, **kwargs)


def _json_or_error(r):
    # Let's just assume that successful calls to bitbucket
    # will be in the 200 range regardless of the exact number.
    # XXX: alternatively, we could pass in the expected error.
    if r.status_code not in range(200, 300):
        r.raise_for_status()
    try:
        return json.loads(r.content)
    except:
        pass


def get_user_repos(username, password=''):
    url = BASE_URL + 'user/repositories/'
    r = requests.get(url, auth=(username, password))
    return _json_or_error(r)


def search_repositories(name):
    # TODO: this method is current not used or implemented in the cli
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
    # TODO: this method is current not used or implemented in the cli
    url = BASE_URL + 'repositories/%s/%s/branches/' % (ownername, repo_slug)
    r = _optional_auth_get(url, username, password)
    return _json_or_error(r)


def create_repository(name, username, password, scm='hg', is_private=True, owner=''):
    url = BASE_URL + 'repositories/'
    payload = {'name': name,
               'scm': scm,
               'is_private': str(bool(is_private))}
    if owner != '':
        payload['owner'] = owner
    r = requests.post(url, data=payload, auth=(username, password))
    return _json_or_error(r)


def update_repository(username, repo_slug, password, **opts):
    url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
    if opts.get('is_private'):
        opts['is_private'] = 'True'
    r = requests.put(url, data=opts, auth=(username, password))
    return _json_or_error(r)


def delete_repository(username, repo_slug, password):
    url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
    r = requests.delete(url, auth=(username, password))
    # previously testing explicitly for 204 and handling errors
    # differently from the other calls.
    return _json_or_error(r)


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
