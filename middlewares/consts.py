# -*- coding: utf-8 -*-

from enum import Enum

# Used to find end of the Headers section
EMPTY_LINE = b'\r\n\r\n'


class PayLoadType(Enum):
    request = b"1"
    original_response = b"2"
    replayed_response = b"3"
