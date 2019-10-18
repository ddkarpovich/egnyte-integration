import urllib
import requests

from egnyte_app.integration import config
from egnyte_app.integration.exceptions import TokenExchangeFailed


def get_authorize_url() -> str:
    url = f'https://{config.EGNYTE_DOMAIN}.egnyte.com/puboauth/token'
    params = {
        'client_id': config.EGNYTE_CLIENT_KEY,
        'redirect_uri': config.EGNYTE_OAUTH_CALLBACK,
        'scope': ','.join(config.EGNYTE_SCOPES),
        'response_type': 'code'
    }
    return f'{url}?{urllib.parse.urlencode(params)}'


def exchange_code(code: str) -> str:
    url = f'https://{config.EGNYTE_DOMAIN}.egnyte.com/puboauth/token'
    data = {
        'client_id': config.EGNYTE_CLIENT_KEY,
        'client_secret': config.EGNYTE_CLIENT_SECRET,
        'redirect_uri': config.EGNYTE_AUTHORIZE_CALLBACK,
        'grant_type': 'authorization_code',
        'code': code
    }

    response = requests.post(url, data=data)

    if response.status_code != 200:
        raise TokenExchangeFailed

    data = response.json()

    if not all([k in data for k in ['access_token', 'expires_in']]):
        raise TokenExchangeFailed

    return data['access_token'], data['expires_in']


def get_user_info(access_token: str) -> dict:
    url = f'https://{config.EGNYTE_DOMAIN}.egnyte.com/pubapi/v1/userinfo'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()


class EgnyteEventsAPI:
    EVENTS_ENDPOINT = '/pubapi/v1/events'
    EVENTS_CURSOR_ENDPOINT = '/pubapi/v1/events/cursor'

    def __init__(self, domain: str, access_token: str):
        self.domain = domain
        self.access_token = access_token

    def do_get(self, endpoint: str, params=None):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = requests.get(self.make_url(endpoint), headers=headers, params=params)
        return response.status_code, response.json()

    def make_url(self, endpoint: str) -> str:
        return f'https://{self.domain}.egnyte.com{endpoint}'

    def fetch(self, start_id: int, count=None) -> dict:
        params = {
            'id': start_id,
            'count': count
        }
        code, data = self.do_get(self.EVENTS_ENDPOINT, params)
        return data

    @property
    def oldest_event_id(self):
        code, data = self.do_get(self.EVENTS_CURSOR_ENDPOINT)
        return int(data.get('latest_event_id')) - 1
