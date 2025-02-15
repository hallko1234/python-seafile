import json
import requests

from seafileapi.exceptions import ClientHttpError
from seafileapi.utils import urljoin


def parse_headers(token):
    return {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json',
    }


def parse_response(response):
    if response.status_code >= 400:
        # ConnectionError ist eine eingebaute Python-Exception, die nur eine Fehlermeldung als String erwartet.
        # Wer mehr Kontrolle benötigt, könnte hier eine benutzerdefinierte Exception werfen.
        raise ConnectionError(f"HTTP {response.status_code}: {response.text}")
    else:
        try:
            data = json.loads(response.text)
            return data
        except Exception:
            return None


class Repo:
    def __init__(self, token, server_url):
        self.server_url = server_url
        self.token = token
        self.repo_id = None
        self.timeout = 30
        self.headers = None
        self._by_api_token = True

    def auth(self, by_api_token=True):
        if not by_api_token:
            self._by_api_token = False
        self.headers = parse_headers(self.token)

    def _repo_info_url(self):
        if self._by_api_token:
            return f"{self.server_url.rstrip('/')}/api/v2.1/via-repo-token/repo-info/"
        return f"{self.server_url.rstrip('/')}/api/v2.1/repos/{self.repo_id}/"

    def _repo_dir_url(self):
        if self._by_api_token:
            return f"{self.server_url.rstrip('/')}/api/v2.1/via-repo-token/dir/"
        return f"{self.server_url.rstrip('/')}/api/v2.1/repos/{self.repo_id}/dir/"

    def _repo_file_url(self):
        if self._by_api_token:
            return f"{self.server_url.rstrip('/')}/api/v2.1/via-repo-token/file/"
        return f"{self.server_url.rstrip('/')}/api/v2.1/repos/{self.repo_id}/file/"

    def get_repo_details(self):
        url = self._repo_info_url()
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        repo = parse_response(response)
        if not repo:
            return {}
        return {
            'repo_id': repo.get('repo_id'),
            'repo_name': repo.get('repo_name'),
            'size': repo.get('size'),
            'file_count': repo.get('file_count'),
            'last_modified': repo.get('last_modified'),
        }

    def list_dir(self, dir_path='/'):
        url = self._repo_dir_url()
        params = {
            'p': dir_path,
            'path': dir_path
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        resp = parse_response(response)
        if resp and 'dirent_list' in resp:
            return resp['dirent_list']
        return []

    def create_dir(self, path):
        url = self._repo_dir_url()
        params = {'path': path} if '/via-repo-token' in url else {'p': path}
        data = {
            'operation': 'mkdir',
        }
        response = requests.post(url, params=params, json=data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def rename_dir(self, path, newname):
        url = self._repo_dir_url()
        params = {'path': path} if '/api/v2.1/via-repo-token' in url else {'p': path}
        data = {
            'operation': 'rename',
            'newname': newname
        }
        response = requests.post(url, params=params, json=data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def delete_dir(self, path):
        url = self._repo_dir_url()
        params = {'path': path} if '/via-repo-token' in url else {'p': path}
        response = requests.delete(url, params=params, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def get_file(self, path):
        # /api2/repos/{repo_id}/file/detail/
        base_file_url = self._repo_file_url()
        if '/via-repo-token' not in base_file_url:
            # Für den Normalfall ergänzen wir den Pfad
            base_file_url = urljoin(self.server_url, f'api2/repos/{self.repo_id}/file/detail/')
        params = {'path': path} if '/via-repo-token' in base_file_url else {"p": path}
        response = requests.get(base_file_url, params=params, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def create_file(self, path):
        url = self._repo_file_url()
        params = {'path': path} if '/via-repo-token' in url else {'p': path}
        data = {
            "operation": "create"
        }
        response = requests.post(url, params=params, json=data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def rename_file(self, path, newname):
        """
        Rename a file.
        :param path: file path
        :param newname: new file name
        """
        url = self._repo_file_url()
        params = {'path': path} if '/via-repo-token' in url else {'p': path}
        data = {
            "operation": "rename",
            "newname": newname
        }
        response = requests.post(url, params=params, json=data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def delete_file(self, path):
        """
        Delete a file/folder
        :param path: file/folder path
        :return: e.g. {'success': True, 'commit_id': '214703...'}
        """
        url = self._repo_file_url()
        params = {'path': path} if '/via-repo-token' in url else {'p': path}
        response = requests.delete(url, params=params, headers=self.headers, timeout=self.timeout)
        return parse_response(response)


class SeafileAPI:
    def __init__(self, login_name, password, server_url):
        self.login_name = login_name
        self.username = None
        self.password = password
        self.server_url = server_url.strip().strip('/')
        self.token = None
        self.timeout = 30
        self.headers = None

    def auth(self):
        data = {
            'username': self.login_name,
            'password': self.password,
        }
        url = f"{self.server_url.rstrip('/')}/api2/auth-token/"
        res = requests.post(url, data=data, timeout=self.timeout)
        if res.status_code != 200:
            raise ClientHttpError(res.status_code, res.content)

        token = res.json().get('token')
        # Seafile-Token haben i.d.R. eine Länge von 40 Zeichen
        if not token or len(token) != 40:
            raise ValueError("Invalid Seafile API token received")

        self.token = token
        self.headers = parse_headers(token)

    def _repo_obj(self, repo_id):
        repo = Repo(self.token, self.server_url)
        repo.repo_id = repo_id
        repo.auth(by_api_token=False)
        return repo

    def list_repos(self):
        url = urljoin(self.server_url, 'api2/repos')
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def get_repo(self, repo_id):
        url = urljoin(self.server_url, f'api2/repos/{repo_id}')
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = parse_response(response)
        if not data:
            return None
        rid = data.get('id')
        return self._repo_obj(rid)

    def create_repo(self, repo_name, passwd=None, story_id=None):
        url = urljoin(self.server_url, 'api2/repos/')
        data = {
            "name": repo_name,
        }
        if passwd:
            data['passwd'] = passwd
        if story_id:
            data['story_id'] = story_id

        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        if response.status_code == 200:
            resp_data = parse_response(response)
            repo_id = resp_data.get('repo_id') if resp_data else None
            if repo_id:
                return self._repo_obj(repo_id)

    def delete_repo(self, repo_id):
        """Remove this repo. Only the repo owner can do this."""
        url = urljoin(self.server_url, f'/api2/repos/{repo_id}/')
        requests.delete(url, headers=self.headers, timeout=self.timeout)
        # Keine Rückgabe vom Endpoint, daher nur True signalisieren
        return True

