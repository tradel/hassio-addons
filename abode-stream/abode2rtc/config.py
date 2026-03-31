import argparse
import json
import os

from logger import log
from utils import obscure_passwords
import const


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class ConfigParser:
    def __init__(self) -> None:
        self._parser = self._create_parser()
        self._args = self._parser.parse_args()
        self._options = self._load_options(self._args.config_file)

    def _create_parser(self):
        parser = argparse.ArgumentParser(description='Abode Camera streaming support for Home Assistant')
        parser.add_argument('--debug', '-d', action='store_true',
                            help='Enable debug logging')
        parser.add_argument('--config-file', '-c',
                            default=const.DEFAULT_CONFIG_PATH,
                            help='Path to configuration file (normally supplied by Home Assistant) ' +
                            '(default: %(default)s)')
        parser.add_argument('--supervisor-token', '-t', action=EnvDefault,
                            envvar='SUPERVISOR_TOKEN', required=False,
                            help='Home Assistant Supervisor token')
        parser.add_argument('--supervisor-url', '-s', action=EnvDefault,
                            envvar='SUPERVISOR_URL',
                            default=const.DEFAULT_SUPERVISOR_URL,
                            help='Home Assistant Supervisor URL (default: %(default)s)')
        parser.add_argument('--abode-username', '-u', action=EnvDefault,
                            envvar='ABODE_USERNAME', required=False,
                            help='Abode username')
        parser.add_argument('--abode-password', '-p', action=EnvDefault,
                            envvar='ABODE_PASSWORD', required=False,
                            help='Abode password')
        parser.add_argument('--locale', '-l', action=EnvDefault,
                            envvar='ABODE_LOCALE', default=const.DEFAULT_LOCALE,
                            help='Abode locale (default: %(default)s)')
        parser.add_argument('--port', '-P', action='store',
                            type=int, default=const.DEFAULT_PORTS['api'],
                            help='Port to listen on for API requests (default: %(default)s)')
        return parser

    def to_dict(self):
        return obscure_passwords({
            'debug': self.debug,
            'supervisor_token': self.supervisor_token,
            'supervisor_url': self.supervisor_url,
            'abode_username': self.abode_username,
            'abode_password': self.abode_password,
            'locale': self.locale,
            'api_port': self.port
        })

    def _load_options(self, config_path=const.DEFAULT_CONFIG_PATH):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except IOError as exc:
            log.error(f"Could not read Home Assistant config from {self.config_file}", exc_info=exc)
            return dict()

    def __getattr__(self, name):
        if getattr(self._args, name):
            return getattr(self._args, name)
        if name in self._options:
            return self._options[name]
        else:
            return None
