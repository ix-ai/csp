#!/usr/bin/env python3
""" Web server that logs HTTP POST requests """

import logging
import os
import json
from flask import Flask
from flask import request
from waitress import serve
from .lib.constants import VERSION, BUILD, W001, W002, W003
log = logging.getLogger('csp')


class CSP():
    """ The main CSP class """

    settings = {
        'max_content_length': 32768,
        'address': '*',
        'port': 9180,
        'enable_healthz_version': False,
        'csp_path': '/csp',
        'healthz_path': '/healthz',
        'metrics_path': '/metrics',  # Placeholder
    }

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.settings:
                self.settings[k] = v
            else:
                log.warning(f'{k} not found in settings. Ignoring.')
        self.server = Flask(__name__)
        self.server.secret_key = os.urandom(64).hex()
        self.server.add_url_rule(self.settings['csp_path'], 'csp', self.log_csp, methods=['POST'])
        self.server.add_url_rule(self.settings['healthz_path'], 'healthz', self.healthz, methods=['GET'])

    def log_csp(self):
        """ Logs the content posted """

        result = ('OK', 200)

        try:
            if request.content_length == 0:
                raise TypeError(W002)
            if request.content_length > self.settings['max_content_length']:
                log.warning(f'{W001} ({request.content_length}). Dropping.')
                result = (W001, 413)
        except TypeError:
            log.warning(W002)
            result = (W002, 422)

        if result == ('OK', 200):
            log.debug(f"{request.environ}")
            content = request.get_data(as_text=True)
            try:
                json_content = json.loads(content)
                log.info(f'{json.dumps(json_content)}')
                # Placeholder: json_content can now be analysed. Ideally, with a function outside of the CSP class
            except json.decoder.JSONDecodeError:
                log.debug(f'{W003}: `{content}`')
                result = (W003, 422)

        return result

    def healthz(self):
        """ Healthcheck """
        version_string = f'{__package__} {VERSION}-{BUILD}'

        log.debug(f'Healthcheck {version_string}')

        message = 'OK'
        if self.settings['enable_healthz_version']:
            message = version_string
        return (message, 200)

    def start(self):
        """ Start the web server """
        serve(
            self.server,
            host=self.settings['address'],
            port=self.settings['port'],
            ident=None,
        )

    def get_port(self) -> int:
        """ returns the configured port from self.settings['port'] """
        return self.settings['port']

    def get_address(self) -> int:
        """ returns the configured address from self.settings['port'] """
        return self.settings['address']
