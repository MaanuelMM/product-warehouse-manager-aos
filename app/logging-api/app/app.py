#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/05/27
# Last update:  2020/06/02


import json  # another alternative is using jsonify provided by flask

from data import Data
from flask import Flask
from wrappers import authorize, validate_event, validate_cors, validate_event_id, validate_args
from handlers import EventHandler

try:
    data = Data()
    event_handler = EventHandler(
        data.DB_HOST, data.DB_PORT, data.DB_INDEX, data.PREFIX)
    server = Flask(__name__)
except:
    exit(1)


@server.route(data.PREFIX, methods=['OPTIONS'])
@validate_cors
@authorize
def options_base():
    return event_handler.options_handler(data.ALLOW_BASE)


@server.route(data.PREFIX, methods=['GET'])
@authorize
@validate_args(data.EVENT_ARGS_SCHEMA)
def cget_base(query):  # request.args for parametrized url
    return event_handler.cget_handler(query)


@server.route(data.PREFIX, methods=['POST'])
@authorize
@validate_event(data.EVENT_REQUEST_SCHEMA)
def post_base(instance):
    return event_handler.post_handler(instance, [element for element in data.EVENT_REQUEST_SCHEMA["properties"]])


@server.route(data.PREFIX + "/<event_id>", methods=['OPTIONS'])
@validate_cors
@authorize
@validate_event_id
def options_id(event_id):
    return event_handler.options_handler(data.ALLOW_ID)


@server.route(data.PREFIX + "/<event_id>", methods=['GET'])
@authorize
@validate_event_id
def get_id(event_id):
    return event_handler.get_handler(event_id)


if __name__ == "__main__":
    try:
        server.run(host=data.HOST, port=data.PORT)
    except:
        exit(1)
