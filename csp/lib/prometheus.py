#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Initializes the prometheus metrics """

from prometheus_client import Counter, Info, make_wsgi_app

# Prometheus metrics
PROM_VALID_VIOLATION_REPORTS_COUNTER = Counter(
    'csp_valid_violation_reports', 'Counts the number of valid violation reports', [
        'blocked_uri',
        'document_uri',
        'original_policy',
        'violated_directive',
        'line_number',
        'source_file',
    ]
)
PROM_INVALID_VIOLATION_REPORTS_COUNTER = Counter(
    'csp_invalid_violation_reports', 'Counts the number of invalid violation reports', [
        'reason',
    ]
)
PROM_VERSION_INFO = Info('csp_version', 'Information about CSP')


def init():
    """ Initializes Prometheus """
    return make_wsgi_app()
