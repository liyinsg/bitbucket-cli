import json
import requests
from requests.auth import HTTPDigestAuth

BASE_URL = 'https://api.bitbucket.org/1.0/'
BASE_URL_V2 = 'https://api.bitbucket.org/2.0/'


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
        return r.json()
    except:
        print r.content
        raise

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


def open_pull(username, password, ownername, repo_slug, source='',
              destination='master', title='',
              description='',
              close_source_branch=False, reviewers=''):
    ''' Opens a pull request against the current repository. '''
    name = ownername or username
    url = BASE_URL_V2 + 'repositories/{0}/{1}/pullrequests'.format(name,
                                                                   repo_slug)
    full_name = '/'.join([name, repo_slug])
    if not title:
        title = 'Merging {0} into {1}'.format(source, destination)

    payload = json.dumps({'title': title,
           'description': description,
           'source': {
               'branch': {
                   'name': source,
               },
               'repository': {
                   'full_name': full_name,
               }
           },
         'destination': {
             'branch': {
                 'name': destination
             }
         },
         # 'reviewers': [
         #     {
         #         'username': ''
         # }],
         'close_source_branch': close_source_branch
    })
    headers = {'Content-Type': 'application/json'}

    r = requests.post(url, data=payload, headers=headers,
                      auth=(username, password))
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


def set_privilege(ownername, repo_slug, privilege, privilege_account, username, password):
    url = BASE_URL + 'privileges/%s/%s/%s' % (ownername, repo_slug, privilege_account)
    if privilege == 'none':
        r = requests.delete(url, auth=(username, password))
    else:
        r = requests.put(url, data=privilege, auth=(username, password))
    return _json_or_error(r)

def set_group_privilege(ownername, repo_slug, privilege, teamname, groupname, username, password):
    url = BASE_URL + 'group-privileges/%s/%s/%s/%s' % (ownername, repo_slug, teamname, groupname)
    if privilege == 'none':
        r = requests.delete(url, auth=(username, password))
    else:
        r = requests.put(url, data=privilege, auth=(username, password))
    return _json_or_error(r)

def update_repository(username, repo_slug, password, **opts):
    owner = opts.get("owner", username)
    url = BASE_URL + 'repositories/%s/%s/' % (owner, repo_slug)
    if opts.get('is_private'):
        opts['is_private'] = 'True'
    r = requests.put(url, data=opts, auth=(username, password))
    return _json_or_error(r)


def delete_repository(username, repo_slug, password, owner=None):
    if not owner:
        owner = username
    url = BASE_URL_V2 + 'repositories/%s/%s/' % (owner, repo_slug)
    r = requests.delete(url, auth=(username, password))
    if r.status_code not in range(200, 300):
        r.raise_for_status()

def download_file(repo_user, repo_slug, filename, username='', password=''):
    url = 'https://bitbucket.org/%s/%s/downloads/%s' % \
        (repo_user, repo_slug, filename)

    print(url)
    if password:
        r = requests.get(url, auth=HTTPDigestAuth(username, password))
    else:
        r = requests.get(url)

    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)
    else:
        r.raise_for_status()
