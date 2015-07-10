# -*- coding: utf-8 -*-
"""
    env2config.util
    ~~~~~~~~~~~~~~~
    Standalone utility functions.
    
    :license: MIT, see LICENSE for more details.
"""

import sys
import os
import logging

LOG_FORMAT = '[%(asctime)s] env2config.%(module)s %(levelname)s: %(message)s'

# global logger instance
_logger = None


def create_logger():
    '''Create a logger'''

    global _logger
    if _logger is not None:
        return _logger

    log_level_string = os.environ.get('LOG_LEVEL', 'INFO')
    log_level = logging.getLevelName(log_level_string.upper())

    # getLevelName returns an int when passed a valid log level name.
    # returns a string, otherwise.
    if not isinstance(log_level, int):
        raise ValueError('LOG_LEVEL of "{0}" not found'.format(log_level_string))

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger = logging.getLogger('env2config')
    del logger.handlers[:]
    logger.addHandler(handler)
    logger.setLevel(log_level)

    _logger = logger
    return _logger
