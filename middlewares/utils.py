# -*- coding: utf-8 -*-

import sys
import hashlib
from consts import *


def log(msg):
    """
    Logging to STDERR as STDOUT and STDIN used for data transfer
    @type msg: str or byte string
    @param msg: Message to log to STDERR
    """
    try:
        msg = str(msg) + '\n'
    except:
        pass
    sys.stderr.write(msg)
    sys.stderr.flush()


def find_end_of_headers(byte_data):
    """
    Finds where the header portion ends and the content portion begins.
    @type byte_data: str or byte string
    @param byte_data: Hex decoded req or resp string
    """
    return byte_data.index(EMPTY_LINE) + 4


def calculate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()
