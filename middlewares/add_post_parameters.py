#! /usr/bin/python3
# -*- coding: utf-8 -*-

###! /Users/lannister/anaconda3/bin/python3

import sys
import fileinput
import binascii
import json

from collections import namedtuple
from decode_content.decode_content import decode_original_response_body, decode_http_req
from utils import *

Meta = namedtuple("Meta", ["payload_type", "request_id", "timestamp", "latency"])


# Req = {}


def process_stdin():
    """
    Process STDIN and output to STDOUT
    """
    for raw_line in fileinput.input():

        line = raw_line.rstrip()

        # Decode base64 encoded line
        decoded = bytes.fromhex(line)

        # Split into metadata and payload, the payload is headers + body
        (raw_metadata, payload) = decoded.split(b'\n', 1)

        # Split into headers and payload
        headers_pos = find_end_of_headers(payload)
        raw_headers = payload[:headers_pos]
        raw_content = payload[headers_pos:]

        # get Meta
        meta = Meta(*raw_metadata.split(b' '))

        log('===================================')
        request_type_id = int(raw_metadata.split(b' ')[0])
        log(
            'Request type: {}'.format(
                {1: 'Request', 2: 'Original Response', 3: 'Replayed Response'}[
                    request_type_id
                ]
            )
        )
        log('===================================')

        log('Original data:')
        log(line)

        log('Decoded request:')
        log(decoded)

        # if meta.payload_type == PayLoadType.original_response.value:
        #     log("=========original response=========")
        #     new_body_decoded = decode_original_response_body(raw_content)
        #     # Req[meta.request_id] = new_body_decoded
        if meta.payload_type == PayLoadType.request.value:
            log("=========replayed req=========")
            # continue
            new_body_decoded = decode_http_req(raw_content)
            log('Decoded new request:')
            log(new_body_decoded)
            if not new_body_decoded:
                continue

        encoded = binascii.hexlify(
            raw_metadata + b'\n' + raw_headers + new_body_decoded
        ).decode('ascii')
        log('Encoded data:')
        log(encoded)

        sys.stdout.write(encoded + '\n')
        return encoded + '\n'


if __name__ == '__main__':
    process_stdin()
