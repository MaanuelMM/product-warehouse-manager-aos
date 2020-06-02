#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/02


import json

from functools import wraps
from flask import request, abort
from http import HTTPStatus
from validators import ArgsValidator, InstanceValidator
from responses import make_response, http_message
from uuid import UUID


def authorize(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if "X-API-Key" not in request.headers:
            abort(make_response(request.headers, HTTPStatus.UNAUTHORIZED,
                                json.dumps(http_message(HTTPStatus.UNAUTHORIZED))))
        return f(*args, **kwargs)
    return check_authorization


def validate_event(schema):
    def real_validate_event(f):
        @wraps(f)
        def validate_instance(*args, **kwargs):
            instance = None
            if request.is_json:  # or request.mimetype == '*/*': # application/json or */* are accepted
                try:
                    instance = request.json
                    InstanceValidator(schema).validate(instance)
                except:
                    abort(make_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                        http_message(HTTPStatus.UNPROCESSABLE_ENTITY))))
            else:
                abort(make_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                    http_message(HTTPStatus.UNPROCESSABLE_ENTITY))))
            return f(instance, *args, **kwargs)
        return validate_instance
    return real_validate_event


def validate_cors(f):
    @wraps(f)
    def cors_prefligth_headers(*args, **kwargs):
        origin = request.headers.get(
            "origin")
        access_control_request_method = request.headers.get(
            "access-control-request-method")

        if origin and access_control_request_method:
            response = make_response(request.headers)
            response.headers.add("Access-Control-Allow-Methods",
                                 access_control_request_method)  # something strange happens with prism here
            response.headers.add("Vary",
                                 "origin")
            abort(response)
        return f(*args, **kwargs)
    return cors_prefligth_headers


def validate_event_id(f):
    @wraps(f)
    def validate_uuid(event_id, *args, **kwargs):
        try:
            event_id = UUID(int=int(event_id))
        except:
            abort(make_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                http_message(HTTPStatus.UNPROCESSABLE_ENTITY))))
        return f(event_id, *args, **kwargs)
    return validate_uuid


def validate_args(schema):
    def real_validate_args(f):
        @wraps(f)
        def validate_query(*args, **kwargs):
            try:
                query = dict(request.args.items())
                ArgsValidator(schema).validate(query)
            except:
                abort(make_response(request.headers, HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps(
                    http_message(HTTPStatus.UNPROCESSABLE_ENTITY))))
            return f(query, *args, **kwargs)
        return validate_query
    return real_validate_args
