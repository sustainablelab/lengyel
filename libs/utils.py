#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Utilities: setup logging
"""

import logging

def setup_logging(loglevel:str="DEBUG") -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            "%(asctime)s %(levelname)s in '%(funcName)s()' (%(filename)s:%(lineno)d) -- %(message)s",
            datefmt="%H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
