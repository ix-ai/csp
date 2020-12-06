#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" processes the environment variables and starts csp """

import logging
from . import csp
from .lib import helpers
from .lib import constants
from .lib import prometheus

log = logging.getLogger('csp')

# The environ keys to use, each of them correlating to `int`, `list`, `string`, `boolean` or `filter`
options = helpers.gather_environ({
    'max_content_length': 'int',
    'address': 'string',
    'port': 'int',
    'enable_healthz_version': 'boolean',
    'enable_metrics': 'boolean',
    'csp_path': 'string',
    'healthz_path': 'string',
    'metrics_path': 'string',
})
c = csp.CSP(**options)

version = f'{constants.VERSION}-{constants.BUILD}'
log.warning(f"Starting **{__package__} {version}**. Listening on {c.get_address()}:{c.get_port()}")
prometheus.PROM_VERSION_INFO.info({'version': f'{version}'})
c.start()
