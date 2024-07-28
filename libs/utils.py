#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Utilities: setup logging
"""

import logging
from array import array

logger = logging.getLogger(__name__)

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

def check_array_itemsize() -> None:
    """Log warning if size > expected. Log error if size < expected."""
    def check(expected:int, actual:int) -> None:
        if actual < expected:
            logger.error(f"'B' is {actual} bytes. Expect 'B' is {expected} bytes.")
        if actual > expected:
            logger.warning(f"'B' is {actual} bytes. Expect 'B' is {expected} bytes.")
    # Unsigned ints
    data = array('B', [1]); check(expected=1,actual=data.itemsize)
    data = array('H', [1]); check(expected=2,actual=data.itemsize)
    data = array('I', [1]); check(expected=4,actual=data.itemsize)
    data = array('L', [1]); check(expected=8,actual=data.itemsize)
    data = array('Q', [1]); check(expected=8,actual=data.itemsize)
    # Float
    data = array('f', [1]); check(expected=4,actual=data.itemsize)
    data = array('d', [1]); check(expected=8,actual=data.itemsize)
