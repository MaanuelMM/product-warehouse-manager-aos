#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/05/27
# Last update:  2020/06/01


import json  # another alternative is using jsonify provided by flask

from os import environ as env
from functools import wraps
from flask import Flask, request, abort, make_response, Response
from werkzeug.datastructures import EnvironHeaders
# from flask_cors import CORS, cross_origin
from http import HTTPStatus
from datetime import datetime, timezone
# from dateutil import parser, tz
# from jsonschema import validate, FormatChecker
from jsonschema import Draft7Validator, validators


def _response_with_common_cors_headers(incoming_headers: EnvironHeaders):
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

def message_response(incoming_headers: EnvironHeaders, status_code: int = HTTPStatus.NO_CONTENT, data: str = None, mimetype: str = 'application/json'):
    response = _response_with_common_cors_headers(incoming_headers)

    response.status_code = status_code

    if data is not None:
        response.data = data
        response.mimetype = mimetype
        response.headers.add("Content-Length", str(len(response.data)))
    else:
        response.headers.add("Content-Length", "0")

    return response


def message_dict(code: HTTPStatus):
    return {
        "code": code,
        "message": code.description
    }


def extend_validator(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    # maybe it's possible to sanitize both default values and extra keys at once, but i'm tired
    def sanitize_instance(validator, properties, instance, schema):
        # set defaults to instance (date-time included)
        for property, subschema in properties.items():
            # neither date nor time are considered, only date-time
            if "format" in subschema and subschema["format"] == "date-time":
                instance.setdefault(property, str(
                    datetime.now(timezone.utc).isoformat()))
            elif "default" in subschema:
                instance.setdefault(property, subschema["default"])

        # delete extra keys
        for prop in list(instance.keys()):
            if prop not in properties:
                del instance[prop]

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": sanitize_instance},
    )


SchemaValidator = extend_validator(Draft7Validator)


EVENT_REQUEST_SCHEMA = {
    "title": "EventRequestBody",
    "type": "object",
    "required": ["origin", "message"],
    "properties": {
        "origin": {
            "type": "string"
        },
        "date": {
            "type": "string",
            "format": "date-time"
        },
        "message": {
            "type": "string"
        },
        "level": {
            "type": "string",
            "enum": ["info", "warn", "error"],
            "default": "info"
        }
    }
}

ALLOW_BASE = "GET,POST"
ALLOW_ID = "GET"

try:
    PREFIX = env.get("PREFIX", "/events")

    # throws an exception if PREFIX doesn't start with slash
    assert PREFIX[0] == "/"

    HOST = env.get("HOST", "0.0.0.0")
    PORT = int(env.get("PORT", "4010"))

    server = Flask(__name__)
    # CORS(server, supports_credentials=True)
    # server.config['CORS_HEADERS'] = 'Content-Type'
except:
    exit(1)


def authorize(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if "X-API-Key" not in request.headers:
            abort(message_response(request.headers, HTTPStatus.UNAUTHORIZED,
                                   json.dumps(message_dict(HTTPStatus.UNAUTHORIZED))))
        return f(*args, **kwargs)
    return check_authorization


def validate_event(f):
    @wraps(f)
    def validate_instance(*args, **kwargs):
        instance = None
        if request.is_json:  # or request.mimetype == '*/*': # application/json or */* are accepted
            try:
                instance = request.json
                SchemaValidator(EVENT_REQUEST_SCHEMA).validate(instance)
            except:
                abort(message_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                    message_dict(HTTPStatus.UNPROCESSABLE_ENTITY))))
        else:
            abort(message_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                message_dict(HTTPStatus.UNPROCESSABLE_ENTITY))))
        return f(instance, *args, **kwargs)
    return validate_instance


def cors_handler(f):
    @wraps(f)
    def cors_prefligth_headers(*args, **kwargs):
        origin = request.headers.get(
            "origin")
        access_control_request_method = request.headers.get(
            "access-control-request-method")

        if origin and access_control_request_method:
            response = message_response(request.headers)
            response.headers.add("Access-Control-Allow-Methods",
                                 access_control_request_method)  # something strange happens with prism here
            response.headers.add("Vary",
                                 "origin")
            abort(response)
        return f(*args, **kwargs)
    return cors_prefligth_headers


@server.route(PREFIX, methods=['OPTIONS'])
@cors_handler
@authorize
def options_base():
    response = message_response(request.headers, HTTPStatus.NO_CONTENT, json.dumps(
        message_dict(HTTPStatus.NO_CONTENT)))
    response.headers.add("Allow", ALLOW_BASE)
    return response


@server.route(PREFIX, methods=['GET'])
@authorize
def cget_base():  # request.args for parametrized url
    example = {"events": [{"event": {"eventId": 878923748, "origin": "ORDERS", "date": "2020-05-27T19:06:46.375Z",
                                     "message": "string", "level": "info", "_links": {"parent": {"href": "string"}, "self": {"href": "string"}}}}]}

    return message_response(request.headers, HTTPStatus.OK, json.dumps(example))


@server.route(PREFIX, methods=['POST'])
@authorize
@validate_event
def post_base(instance):
    return message_response(request.headers, HTTPStatus.CREATED, json.dumps(instance))


@server.route(PREFIX + "/<event_id>", methods=['OPTIONS'])
@cors_handler
@authorize
def options_id(event_id):
    response = message_response(request.headers, HTTPStatus.NO_CONTENT, json.dumps(
        message_dict(HTTPStatus.NO_CONTENT)))
    response.headers.add("Allow", ALLOW_ID)
    return response


@server.route(PREFIX + "/<event_id>", methods=['GET'])
@authorize
def get_id(event_id):
    example = {"event": {"eventId": 878923748, "origin": "ORDERS", "date": "2020-05-27T19:06:46.375Z",
                         "message": "string", "level": "info", "_links": {"parent": {"href": "string"}, "self": {"href": "string"}}}}

    return message_response(request.headers, HTTPStatus.OK, json.dumps(example))


if __name__ == "__main__":
    try:
        server.run(host=HOST, port=PORT)
    except:
        exit(1)
