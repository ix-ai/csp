#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Helper functions """

import logging
import os
from distutils.util import strtobool

log = logging.getLogger("csp")


def gather_environ(keys) -> dict:
    """
    Return a dict of environment variables correlating to the keys dict
    :param keys: The environ keys to use, each of them correlating to `int`, `list`, `string`, `boolean` or `filter`
    :return: A dict of found environ values
    """
    environs = {}
    for key, key_type in keys.items():
        if os.environ.get(key.upper()):
            environs.update({key: os.environ[key.upper()]})
            if key_type == 'int':
                try:
                    environs[key] = int(environs[key])
                except ValueError:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Ignoring.")
                    del environs[key]
                    continue
            if key_type == 'list':
                environs[key] = environs[key].split(' ')
            if key_type == 'boolean':
                try:
                    environs[key] = bool(strtobool(environs[key]))
                except ValueError:
                    log.warning(f"`{environs[key]}` not understood for {key.upper()}. Setting to False.")
                    environs[key] = False
                    continue
            if key_type == 'filter':
                filters = environs[key].split('=', 1)
                environs[key] = {filters[0]: filters[1]}
            log.info(f'{key.upper()} is set')
    return environs
