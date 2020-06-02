#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Authors:      MaanuelMM
# Created:      2020/06/01
# Last update:  2020/06/02


from datetime import datetime, timezone
from jsonschema import Draft7Validator, validators


def args_validator(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    # maybe it's possible to sanitize both default values and extra keys at once, but i'm tired
    def sanitize_args(validator, properties, instance, schema):
        # delete extra keys
        for prop in list(instance.keys()):
            if prop not in properties:
                del instance[prop]

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": sanitize_args},
    )


def instance_validator(validator_class):
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

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": sanitize_instance},
    )


ArgsValidator = args_validator(Draft7Validator)

InstanceValidator = instance_validator(ArgsValidator)
