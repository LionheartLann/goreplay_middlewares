#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import fileinput
import binascii

from collections import namedtuple
from decode_content.decode_content import decode_original_response_body, decode_http_req
from utils import *


Meta = namedtuple("Meta", ["payload_type", "request_id", "timestamp", "latency"])
Headers = namedtuple("Headers", ["request_method", "path", "http_version"])
# Req = {}


def get_headers(header_bytes: bytes):
    path_data = header_bytes.split(b"\r\n")[0]
    return Headers(*path_data.split(b" "))


def process_stdin(raw_line: bytes):
    """
    Process STDIN and output to STDOUT
    """
    line = raw_line.rstrip()

    # Decode base64 encoded line
    decoded = bytes.fromhex(line)

    # Split into metadata and payload, the payload is headers + body
    (raw_metadata, payload) = decoded.split(b"\n", 1)

    # Split into headers and payload
    headers_pos = find_end_of_headers(payload)
    raw_headers = payload[:headers_pos]
    raw_content = payload[headers_pos:]

    # get Meta
    meta = Meta(*raw_metadata.split(b" "))
    if meta.payload_type != PayLoadType.request.value:
        # log(f"=========filter by payload_type: {meta.payload_type}")
        return

    headers = get_headers(raw_headers)
    # log(f"headers: {headers._asdict()}")
    if headers.path != b"/service/check":
        # log(f"=======filter by path: {headers.path}")
        return

    log("===================================")
    request_type_id = int(raw_metadata.split(b" ")[0])
    log(
        "Request type: {}".format(
            {1: "Request", 2: "Original Response", 3: "Replayed Response"}[
                request_type_id
            ]
        )
    )
    log("===================================")

    log("Original data:")
    log(line)

    log("Decoded request:")
    log(decoded)

    # if meta.payload_type == PayLoadType.original_response.value:
    #     log("=========original response=========")
    #     new_body_decoded = decode_original_response_body(raw_content)
    #     # Req[meta.request_id] = new_body_decoded

    new_body_decoded = decode_http_req(raw_content)
    log("Decoded new request:")
    log(new_body_decoded)
    if not new_body_decoded:
        log("=========filter by req body params=========")
        return

    encoded = binascii.hexlify(
        raw_metadata + b"\n" + raw_headers + new_body_decoded
    ).decode("ascii")
    log("Encoded data:")
    log(encoded)

    sys.stdout.write(encoded + "\n")
    sys.stdout.flush()
    log("=========replayed success!=========")


if __name__ == "__main__":
    for raw_line in fileinput.input():
        process_stdin(raw_line)
