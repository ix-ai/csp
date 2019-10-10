#!/usr/bin/env python3
""" Web server that logs HTTP POST requests """

import logging
import os
import sys
import pygelf
from flask import Flask
from flask import request
from waitress import serve

LOG = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

APP = Flask(__name__)
APP.secret_key = os.urandom(64).hex()

SETTINGS = {
    'content_length': int(os.environ.get('MAX_CONTENT_LENGTH', 4096)),
    'port': int(os.environ.get('PORT', 9180)),
    'address': os.environ.get('ADDRESS', '*'),
    'gelf_host': os.environ.get('GELF_HOST'),
    'gelf_port': int(os.environ.get('GELF_PORT', 12201)),
}


def configure_logging():
    """ Configures the logging """
    gelf_enabled = False

    if os.environ.get('GELF_HOST'):
        GELF = pygelf.GelfUdpHandler(
            host=SETTINGS['gelf_host'],
            port=SETTINGS['gelf_port'],
            debug=True,
            include_extra_fields=True,
            _ix_id=os.path.splitext(sys.modules['__main__'].__file__)[0][1:],
        )
        LOG.addHandler(GELF)
        gelf_enabled = True
    LOG.info('Initialized logging with GELF enabled: {}'.format(gelf_enabled))


@APP.route('/csp', methods=['POST'])
def log_csp():
    """ Logs the content posted """

    return_message = 'OK'
    if request.content_length > SETTINGS['content_length']:
        return_message = 'Request too large ({}). Dropping.'.format(request.content_length)
        LOG.error(return_message)
    else:
        content = request.get_data(as_text=True)
        LOG.info('{}'.format(content))

    return return_message


if __name__ == '__main__':
    configure_logging()
    LOG.info("Starting {}, listening on {}:{}".format(
        os.path.splitext(sys.modules['__main__'].__file__)[0][1:],
        SETTINGS['address'],
        SETTINGS['port']
    ))
    serve(APP, host=SETTINGS['address'], port=SETTINGS['port'])
