#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/02

import json

from flask import request
from responses import make_response, http_message
from http import HTTPStatus
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError, NotFoundError
from uuid import uuid1, UUID


# the biggest $#*! i've ever done - in a bad way
class EventHandler():

    def __init__(self, host: str, port: int, index: str, prefix: str):
        try:
            self.es = Elasticsearch(hosts=[(host + ':' + str(port))])
            self.index = index
            self.prefix = prefix
        except:
            raise

    @staticmethod
    def _order_data(data: dict, schema_order: list):
        new_data = dict()

        for element in schema_order:
            new_data[element] = data[element]

        return new_data

    def _generate_dict_body(self, data: dict, event_id: int):
        new_data = dict()

        new_data["eventId"] = event_id
        new_data.update(data)
        new_data["_links"] = {
            "parent": {
                "href": self.prefix
            },
            "self": {
                "href": self.prefix + f"/{event_id}"
            }
        }

        return new_data

    @staticmethod
    def _join_list(data: list, separator: str = ','):
        return separator.join(map(str, data))

    def _generate_csv_body(self, data: dict, event_id: int):  # no headers
        new_data = list()

        new_data.append(event_id)
        new_data.append(EventHandler._join_list(
            [value for value in data.values()]))
        new_data.append(self.prefix)
        new_data.append(self.prefix + f"/{event_id}")

        return EventHandler._join_list(new_data)

    @staticmethod
    def _generate_csv_header(data: dict):
        new_data = list()

        new_data.append("eventId")
        new_data.append(EventHandler._join_list(
            [key for key in data]))
        new_data.append("_parent_href_link")
        new_data.append("_self_href_link")

        return EventHandler._join_list(new_data)

    def _get_event_by_id(self, event_id: UUID):
        data = None

        try:
            data = self.es.get(index=self.index, id=event_id)["_source"]
        except NotFoundError:
            data = dict()
        except Exception:
            pass

        return data

    def _search_events(self, query: dict):
        result = None

        try:
            if query:
                result = self.es.search(index=self.index, body={'query': {'bool': {'must': [
                                        {'match': {key: value}} for key, value in query.items()]}}})['hits']['hits']
            else:
                result = self.es.search(index=self.index, body={'query': {'match_all': {}}})[
                    'hits']['hits']
        except NotFoundError:
            result = dict()
        except Exception:
            pass

        return result

    @staticmethod
    def options_handler(allow_header):
        response = make_response(request.headers)
        response.headers.add("Allow", allow_header)
        return response

    def post_handler(self, data: dict, schema_order: list):
        response = None

        while True:
            try:
                body = EventHandler._order_data(data, schema_order)
                event_id = uuid1()
                self.es.create(index=self.index, id=event_id, body=body)
                response_body = self._generate_dict_body(body, event_id.int)
                response = make_response(
                    request.headers, HTTPStatus.CREATED, json.dumps(response_body))
                response.headers.add(
                    "Location", response_body["_links"]["self"]["href"])
                break
            except ConflictError:  # it's pretty impossible an uuid collision, but who knows...
                continue
            except Exception:  # here is if something really bad happens, so let's exit and thow a 500 error
                response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
                    http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))
                break

        return response

    def get_handler(self, event_id: UUID):
        response = None

        data = self._get_event_by_id(event_id)
        if data:
            if str(request.accept_mimetypes) == 'text/csv':
                response = make_response(request.headers, HTTPStatus.OK, EventHandler._join_list(
                    [EventHandler._generate_csv_header(data), self._generate_csv_body(
                        data, event_id.int)], '\n'), True, 'text/csv')
            else:  # default to 'application/json'
                response = make_response(request.headers, HTTPStatus.OK, json.dumps(
                    self._generate_dict_body(data, event_id.int)), True)
        elif data is not None:
            response = make_response(request.headers, HTTPStatus.NOT_FOUND, json.dumps(
                http_message(HTTPStatus.NOT_FOUND)))
        else:
            response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
                http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))

        return response

    def cget_handler(self, query):
        response = None

        data = self._search_events(query)
        if data:
            if str(request.accept_mimetypes) == 'text/csv':
                csv = [EventHandler._generate_csv_header(data[0])] # all are the same - in other words, i don't care
                for event in data:
                    csv.append(self._generate_csv_body(
                        event['_source'], UUID(event['_id']).int))
                response = make_response(request.headers, HTTPStatus.OK, EventHandler._join_list(
                    csv, '\n'), True, 'text/csv')
            else:
                dict_list = list()
                for event in data:
                    dict_list.append(self._generate_dict_body(
                        event['_source'], UUID(event['_id']).int))
                response = make_response(
                    request.headers, HTTPStatus.OK, json.dumps({'events': dict_list}), True)
        elif data is not None:
            response = make_response(request.headers, HTTPStatus.NOT_FOUND, json.dumps(
                http_message(HTTPStatus.NOT_FOUND)))
        else:
            response = make_response(request.headers, HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps(
                http_message(HTTPStatus.INTERNAL_SERVER_ERROR)))

        return response
