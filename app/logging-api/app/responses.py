#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/02

from flask import make_response as Response
from werkzeug.datastructures import EnvironHeaders
from http import HTTPStatus
from hashlib import sha256


# this can be done WAY better with inheritance... but i'm dead
def _base_response_with_common_cors_headers(incoming_headers: EnvironHeaders):
    response = Response()

    response.headers.pop("content-type")

    response.headers.add("Access-Control-Allow-Origin",
                         incoming_headers.get("origin", default="*"))
    response.headers.add("Access-Control-Allow-Headers",
                         incoming_headers.get("access-control-request-headers", default="*"))
    response.headers.add("Access-Control-Allow-Credentials",
                         "true")
    response.headers.add("Access-Control-Expose-Headers",
                         incoming_headers.get("access-control-expose-headers", default="*"))

    return response


# json.dumps(message_dict(code_enum))

def make_response(incoming_headers: EnvironHeaders, status_code: int = HTTPStatus.NO_CONTENT, data: str = None, etag: bool = False, mimetype: str = 'application/json'):
    response = _base_response_with_common_cors_headers(incoming_headers)

    response.status_code = status_code

    if data is not None:
        response.set_data(data)
        response.mimetype = mimetype
        # response.headers.add("Content-Length", str(len(response.data)))
    else:
        response.headers.add("Content-Length", "0")

    if etag:  # i don't know who it works, so let's do this
        checkshum = sha256()
        checkshum.update(response.get_data())
        response.headers.add("Etag", checkshum.hexdigest())

    return response


def http_message(code: HTTPStatus):
    return {
        "code": code,
        "message": code.description
    }
