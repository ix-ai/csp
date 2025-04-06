#!/usr/bin/env python3
""" Web server that logs HTTP POST requests """

import logging
import os
import json
from flask import Flask
from flask import request
from waitress import serve
from .lib.constants import VERSION, BUILD, W001, W002, W003, W004
from .lib import prometheus, constants

log = logging.getLogger(constants.NAME)

class CSP():
    """ The main CSP class """

    settings = {
        'max_content_length': 32768,
        'address': '*',
        'port': 9180,
        'enable_healthz_version': False,
        'enable_metrics': False,
        'csp_path': '/csp',
        'healthz_path': '/healthz',
        'metrics_path': '/metrics',
        'enable_user_agent': False,
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
        if self.settings['enable_metrics']:
            self.server.add_url_rule(self.settings['metrics_path'], 'metrics', self.metrics, methods=['GET', 'POST'])

    def log_csp(self):
        """ Logs the content posted """

        result = ('OK', 200)

        try:
            if request.content_length == 0:
                raise TypeError(W002)
            if request.content_length > self.settings['max_content_length']:
                log.warning(f'{W001} ({request.content_length}). Dropping.')
                result = (W001, 413)
                prometheus.PROM_INVALID_VIOLATION_REPORTS_COUNTER.labels(reason='too-large').inc(1)
        except TypeError:
            log.warning(W002)
            result = (W002, 422)
            prometheus.PROM_INVALID_VIOLATION_REPORTS_COUNTER.labels(reason='empty').inc(1)

        if result == ('OK', 200):
            log.debug(f"{request.environ}")
            content = request.get_data(as_text=True)
            try:
                if self.settings['enable_user_agent']:
                    log.info(self.__process_csp(json.loads(content), request.user_agent))
                else:
                    log.info(self.__process_csp(json.loads(content), None))
            except CSPError:
                log.debug(f'{W004}: `{content}`')
                log.warning(W004)
                result = (W004, 422)
                prometheus.PROM_INVALID_VIOLATION_REPORTS_COUNTER.labels(reason='non-csp').inc(1)
            except json.decoder.JSONDecodeError:
                log.debug(f'{W003}: `{content}`')
                log.warning(W003)
                result = (W003, 422)
                prometheus.PROM_INVALID_VIOLATION_REPORTS_COUNTER.labels(reason='non-json').inc(1)

        return result

    def __process_csp(self, content, user_agent):
        """ Takes the JSON content and creates the metrics for it """
        try:
            report = content['csp-report']
        except KeyError:
            raise CSPError from KeyError

        try:
            labels = {
                'blocked_uri': report['blocked-uri'],
                'document_uri': report['document-uri'],
                'original_policy': report['original-policy'],
                'violated_directive': report['violated-directive'],
                'line_number': report.get('line-number', 0),
                'source_file': report.get('source-file'),
            }

            if user_agent is None:
                prometheus.PROM_VALID_VIOLATION_REPORTS_COUNTER.labels(**labels).inc(1)
            else:
                labels.update({
                    'user_agent_platform': user_agent.platform,
                    'user_agent_browser': user_agent.browser,
                    'user_agent_version': user_agent.version,
                })
                prometheus.PROM_VALID_VIOLATION_REPORTS_COUNTER_AGENT.labels(**labels).inc(1)

            return json.dumps(labels)
        except KeyError:
            raise CSPError from KeyError

        return json.dumps(content)

    def healthz(self):
        """ Healthcheck """
        version_string = f'{__package__} {VERSION}-{BUILD}'

        log.debug(f'Healthcheck {version_string}')

        message = 'OK'
        if self.settings['enable_healthz_version']:
            message = version_string
        return (message, 200)

    def metrics(self):
        """ Prometheus Metrics """
        return prometheus.init()

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


class CSPError(Exception):
    """ The CSP Exception resides here """
