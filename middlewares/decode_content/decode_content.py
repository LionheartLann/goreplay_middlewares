# -*- coding: utf-8 -*-
import json
from utils import log, calculate_md5


def decode_original_response_body(body: bytes):
    # load the body as a JSON object
    json_body = json.loads(body)
    # add the debug field to the JSON object

    result = {
        'scene_sign': json_body['data']["scene_sign"],
        "scene_id": json_body['data']["scene_id"],
        "is_action_verified": True,
    }

    params = json_body['data']['request_param']
    params['debug'] = "true"
    result['param'] = params
    # convert the JSON object back to a string
    new_body = json.dumps(result)
    # log(f"===raw new body: {new_body}")
    return new_body.encode()


def decode_original_response(content: bytes):
    # split the content into lines
    lines = content.split(b'\r\n')
    # find the index of the empty line separating headers and body
    empty_line_index = lines.index(b'')
    # get the headers
    headers = lines[:empty_line_index]
    # get the body
    body = b'\r\n'.join(lines[empty_line_index + 1 :])
    # load the body as a JSON object
    json_body = json.loads(body)
    # add the debug field to the JSON object

    result = {
        'scene_sign': json_body['data']["scene_sign"],
        "scene_id": json_body['data']["scene_id"],
        "is_action_verified": True,
    }
    params = json_body['data']['request_param']
    params['debug'] = "true"
    result['param'] = params

    # convert the JSON object back to a string
    new_body = json.dumps(result)
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


def decode_http_req(body: bytes):
    # load the body as a JSON object
    json_body = json.loads(body)
    # filter user_submission
    if json_body['scene_sign'] == "user_submission":
        return b''
        
    log("====decoding req===")
    # add the debug field to the JSON object
    json_body['param']['debug'] = "true"
    md5_data = json_body['param']['phone'] + "," + json_body['param']['ts']
    md5 = calculate_md5(md5_data)
    json_body['param']['md5'] = md5
    new_body = json.dumps(json_body)
    return new_body.encode()


def decode_http_req_content(content: bytes):
    # split the content into lines
    lines = content.split(b'\r\n')
    # find the index of the empty line separating headers and body
    empty_line_index = lines.index(b'')
    # get the headers
    headers = lines[:empty_line_index]
    # log(f"====headers: {headers}")
    # meta = headers[0].split(b' ')
    # log(f"====meta: {meta}")
    # log(f"====meta1: {meta[1]}")
    # req_id = meta[1]
    # get the body
    body = b'\r\n'.join(lines[empty_line_index + 1 :])
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
