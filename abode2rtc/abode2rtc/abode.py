import json
import os
import re
import tempfile
from datetime import datetime
from threading import Timer
from typing import Union
from urllib.parse import urljoin

import const
import requests
from logger import log
from utils import generate_uuid


class AbodeApiClient:
    def __init__(self, username: str = None, password: str = None, locale: str = const.DEFAULT_LOCALE) -> None:
        self._username = username
        self._password = password
        self._locale = locale
        self._session = requests.Session()
        self._features = None
        self._devices = None
        self._cameras = None
        self._token_timer = None
        if self._username and self._password:
            self.login()

    def _request(self, method: str, uri: str, data=None, raise_for_status=False) -> Union[dict, list]:
        response = self._session.request(method, urljoin(const.BASE_URL, uri), data=data)
        if raise_for_status:
            response.raise_for_status()
        return response.json()

    def _set_auth_headers(self) -> None:
        self._session.headers.update({'Abode-Api-Token': self._api_key,
                                      'Authorization': f"Bearer {self._access_token}"})

    def _get_api_key(self) -> str:
        login = self._request('POST', '/api/auth2/login', data={
            'id': self._username,
            'password': self._password,
            'locale_code': self._locale,
            'uuid': generate_uuid()
        })
        return login['token']

    def _get_access_token(self) -> str:
        claims = self._request('GET', '/api/auth2/claims')
        self._start_refresh_timer()
        return claims['access_token']

    def _refresh_access_token(self) -> None:
        log.info("Refreshing Abode access token")
        self._access_token = self._get_access_token()
        self._set_auth_headers()
        self._start_refresh_timer()

    def _start_refresh_timer(self) -> None:
        if self._token_timer:
            self._token_timer.cancel()
        self._token_timer = Timer(const.TOKEN_REFRESH_INTERVAL, self._refresh_access_token)
        self._token_timer.start()

    def login(self) -> None:
        self._api_key = self._get_api_key()
        self._access_token = self._get_access_token()
        self._set_auth_headers()

    def _get_features(self) -> dict:
        if not self._features:
            self._features = self._request('GET', '/integrations/v1/features')
            if 'cameras' not in self._features:
                log.warning("No cameras found in Abode feature API response")
        return self._features

    def _get_devices(self) -> list:
        if not self._devices:
            self._devices = self._request('GET', '/api/v1/devices')
        return self._devices

    def _get_cameras(self) -> list:
        if not self._cameras:
            self._get_devices()
            self._cameras = [d for d in self._devices if d['type_tag'] == const.CAMERA_TYPE and
                             d['origin'] == 'abode_cam']
            if len(self._cameras) == 0:
                log.warning("No cameras found in your Abode setup")
        return self._cameras

    @property
    def features(self) -> dict:
        return self._get_features()

    @property
    def devices(self) -> list:
        return self._get_devices()

    @property
    def cameras(self) -> list:
        return self._get_cameras()

    def by_uuid(self, cam_uuid: str) -> dict:
        results = [d for d in self.cameras if d['uuid'] == cam_uuid]
        if len(results) == 0:
            raise KeyError(f"Camera with UUID {cam_uuid} not found")
        return results[0]

    def by_name(self, cam_name: str) -> dict:
        results = [d for d in self.cameras if d['name'] == cam_name]
        if len(results) == 0:
            raise KeyError(f"Camera with name '{cam_name}' not found")
        return results[0]

    def by_id(self, cam_id: str) -> dict:
        results = [d for d in self.cameras if d['id'] == cam_id]
        if len(results) == 0:
            raise KeyError(f"Camera with id {cam_id} not found")
        return results[0]

    def camera(self, id: str) -> dict:
        if id.startswith('XF:'):
            return self.by_id(id)
        elif re.fullmatch(r'[0-9a-f]{32}', id):
            return self.by_uuid(id)
        else:
            return self.by_name(id)

    def has_247_recording(self, id: str) -> bool:
        cam = self.camera(id)
        return cam['canStream247']

    def to_json(self) -> dict:
        return {
            'username': self._username,
            'password': self._password,
            'api_key': self._api_key,
            'access_token': self._access_token,
            'features': self.features,
            'devices': self.devices,
            'cameras': self.cameras
        }

    @classmethod
    def from_json(cls, data) -> 'AbodeApiClient':
        self = cls()
        self._username = data['username']
        self._password = data['password']
        self._api_key = data['api_key']
        self._access_token = data['access_token']
        self._features = data['features']
        self._devices = data['devices']
        self._cameras = data['cameras']
        self._set_auth_headers
        return self

    @staticmethod
    def _temp_path() -> str:
        return os.path.join(tempfile.gettempdir(), 'abode.json')

    def save(self, path: str = None) -> None:
        path = path or self._temp_path()
        with open(path, 'w') as f:
            json.dump(self.to_json(), f)
        return path

    @classmethod
    def load(cls, path: str = None) -> 'AbodeApiClient':
        path = path or cls._temp_path()
        with open(path, 'r') as f:
            self = cls.from_json(json.load(f))
            self._set_auth_headers()
            return self

    def get_kvs_stream(self, id: str) -> dict:
        cam = self.camera(id)
        log.debug(f"Getting KVS endpoint url for camera {cam['name']}")
        data = self._request('POST', f"/integrations/v1/camera/{cam['uuid']}/kvs/stream", raise_for_status=False)
        if 'errorCode' in data:
            if data['errorCode'] == const.ERR_CAMERA_OFFLINE:
                log.warning(f"Camera '{cam['name']}' is offline, skipping")
                return None
            else:
                raise Exception(f"Error {data['errorCode']} ({data['message']}) getting stream for {cam['name']}")
        return data
