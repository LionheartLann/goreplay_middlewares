#! /Users/lannister/anaconda3/bin/python3
# -*- coding: utf-8 -*-

import sys
import fileinput
import binascii
import json

# Used to find end of the Headers section
EMPTY_LINE = b'\r\n\r\n'


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


def decode_http_content(content: bytes):
    # split the content into lines
    lines = content.split(b'\r\n')
    # find the index of the empty line separating headers and body
    empty_line_index = lines.index(b'')
    # get the headers
    headers = lines[:empty_line_index]
    # get the body
    body = b'\r\n'.join(lines[empty_line_index+1:])
    # load the body as a JSON object
    # log(f"===raw body: {body}")
    json_body = json.loads(body)
    # add the debug field to the JSON object
    json_body['param']['debug'] = "true"
    # convert the JSON object back to a string
    new_body = json.dumps(json_body)
    # log(f"===raw new body: {new_body}")
    # update the Content-Length header with the new length of the body
    new_headers = []
    for header in headers:
        if header.startswith(b'Content-Length:'):
            new_headers.append(f'Content-Length: {len(new_body)}'.encode())
        else:
            new_headers.append(header)
    # join the headers and body back together
    new_content = b'\r\n'.join(new_headers + [b'', new_body.encode()])
    return new_content


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

        log('===================================')
        request_type_id = int(raw_metadata.split(b' ')[0])
        log('Request type: {}'.format({
          1: 'Request',
          2: 'Original Response',
          3: 'Replayed Response'
        }[request_type_id]))
        log('===================================')

        log('Original data:')
        log(line)

        log('Decoded request:')
        log(decoded)

        new_body_decoded = decode_http_content(decoded)
        # new_body_decoded = decode_http_content(raw_content)
        log('Decoded new request:')
        log(new_body_decoded )

        # encoded = binascii.hexlify(raw_metadata + b'\n' + raw_headers + raw_content).decode('ascii')
        encoded = binascii.hexlify(new_body_decoded).decode('ascii')
        log('Encoded data:')
        log(encoded)

        sys.stdout.write(encoded + '\n')
        return encoded + '\n'

if __name__ == '__main__':
    process_stdin()

