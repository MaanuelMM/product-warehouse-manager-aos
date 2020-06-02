#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/02


from os import environ as env


class Data:

    def __init__(self):
        try:
            self.PREFIX = env.get("PREFIX", "/events")

            # throws an exception if PREFIX isn't empty and doesn't start with slash or its length is lower or equal to 1
            assert (
                (self.PREFIX[0] == "/" and len(self.PREFIX) > 1)
                or self.PREFIX == ""
            )

            self.HOST = env.get("HOST", "0.0.0.0")
            self.PORT = int(env.get("PORT", "4010"))

            self.DB_HOST = env.get("DB_HOST", "localhost")
            self.DB_PORT = int(env.get("DB_PORT", "9200"))

            self.DB_INDEX = env.get("DB_INDEX", "logs")

            self.EVENT_REQUEST_SCHEMA = {
                "title": "EventRequestSchema",
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

            self.EVENT_ARGS_SCHEMA = {
                "title": "EventArgsSchema",
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string"
                    },
                    "dateFrom": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "dateTo": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "message": {
                        "type": "string"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["info", "warn", "error"],
                    }
                }
            }

            self.ALLOW_BASE = "GET,POST"
            self.ALLOW_ID = "GET"
        except:
            raise
