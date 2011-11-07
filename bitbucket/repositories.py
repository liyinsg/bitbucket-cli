import requests
import json
from .config import USERNAME, PASSWORD, BASE_URL

def _optional_auth_get(url, username, password, **kwargs):
	if password:
		return requests.get(url, auth=(username, password), **kwargs)
	return requests.get(url, **kwargs)

def _json_or_error(r):
	if r.status_code != 200:
		r.raise_for_status()
	return json.loads(r.content)

def get_user_repos(username=USERNAME, password=PASSWORD):
	url = BASE_URL + 'user/repositories/'
	r = requests.get(url, auth=(username, password))
	return _json_or_error(r)

def search_repositories(name):
	url = BASE_URL + 'repositories/'
	r = requests.get(url, params={'name': name})
	return _json_or_error(r)

def get_repository(username, repo_slug, password=PASSWORD):
	url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
	r = _optional_auth_get(url, username, password)
	return _json_or_error(r)

def get_tags(username, repo_slug, password=PASSWORD):
	url = BASE_URL + 'repositories/%s/%s/tags/' % (username, repo_slug)
	r = _optional_auth_get(url, username, password)
	return _json_or_error(r)

def get_branches(username, repo_slug, password=PASSWORD):
	url = BASE_URL + 'repositories/%s/%s/branches/' % (username, repo_slug)
	r = _optional_auth_get(url, username, password)
	return _json_or_error(r)

def create_repository(name, scm='hg', is_private=True,
		username=USERNAME, password=PASSWORD):
	url = BASE_URL + 'repositories/'
	r = requests.post(url, data={'name': name, 'scm': scm, 
			'is_private': str(bool(is_private))}, auth=(username, password))
	return _json_or_error(r)

def update_repository(username, repo_slug, password=PASSWORD, **opts):
	url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
	r = requests.put(url, data=opts, auth=(username, password))
	return _json_or_error(r)

def delete_repository(username, repo_slug, password=PASSWORD):
	url = BASE_URL + 'repositories/%s/%s/' % (username, repo_slug)
	r = requests.delete(url, auth=(username, password))
	return r.status_code == 200
