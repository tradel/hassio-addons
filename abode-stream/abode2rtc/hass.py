from urllib.parse import urljoin

import requests

from logger import log
from utils import obscure_passwords
from const import DEFAULT_PORTS, DEFAULT_SUPERVISOR_URL


class HassApiClient:
    def __init__(self, token, supervisor_url=DEFAULT_SUPERVISOR_URL) -> None:
        self.token = token
        self.url = supervisor_url
        self.has_api = False
        self._http = requests.Session()
        self._get_token()

    def _get_token(self) -> None:
        if self.token:
            log.debug(f"Got HA supervisor token: {self.token}")
            self.has_api = True
            self._http.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json"
                })
        else:
            log.warning("Unable to get HA supervisor token")

    def _request(self, method: str, uri: str, data=None, raise_for_status=True):
        if not self.has_api:
            return None
        method = method.upper()
        log.info(f"Calling Home Assistant API: {method} {uri}")
        log.debug(f"Full URL: {urljoin(self.url, uri)}")
        log.debug(f"Headers:  {obscure_passwords(self._http.headers)}")
        log.debug(f"Data:     {data}")
        response = self._http.request(method, urljoin(self.url, uri), data=data)
        if raise_for_status:
            response.raise_for_status()
        log.debug(f"Response from Home Assistant: {response.content}")
        return response.json()

    def get_hass_config(self) -> dict:
        log.info("Checking Home Assistant configuration")
        return self._request('GET', '/core/api/config')

    def has_abode_integration(self) -> bool:
        config = self.get_hass_config() or dict()
        components = config.get('components', list())
        log.debug(f"Installed components: {components}")
        return 'abode' in components

    def get_states(self) -> list:
        log.info("Getting current state of entities")
        return self._request('GET', '/core/api/states')

    def get_abode_cams(self) -> list:
        def __is_abode_cam(state) -> bool:
            if not state['entity_id'].startswith('camera.'):
                return False
            elif 'device_id' not in state['attributes']:
                return False
            elif not state['attributes']['device_id'].startswith('XF:'):
                return False
            elif 'device_type' not in state['attributes']:
                return False
            elif not state['attributes']['device_type'].startswith('Abode Cam'):
                return False
            return True
        states = self.get_states()
        return [s for s in states if __is_abode_cam(s)]

    def get_addon_config(self) -> dict:
        return self._request('GET', '/addons/self/info')

    def get_addon_ports(self) -> dict:
        my_info = self.get_addon_config()
        port_info = my_info['data']['network']
        return {
            'go2rtc': port_info.get('1984/tcp', DEFAULT_PORTS['go2rtc']),
            'rtsp': port_info.get('8554/tcp', DEFAULT_PORTS['rtsp']),
            'webrtc': port_info.get('8555/tcp', DEFAULT_PORTS['webrtc']),
            'api': port_info.get('80/tcp', DEFAULT_PORTS['api'])
        }
