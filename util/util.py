""" Common utilities

This module defines helper functions and decorators that can be used accross
all submodules.
"""

import hashlib
import os
import time
from functools import wraps

import jsonschema
import simplejson as json
from flask import Response, g, jsonify, request

import config
import error


def get_request_ip():
    """Returns the requester's IP address regardless of proxying webservers and spoofed headers"""
    if request.headers.getlist("X-Forwarded-For"):
        forwarded_for = request.headers.getlist("X-Forwarded-For")[0]
        # The header field might contain an IP list and port numbers
        # Filter for only the first IP address
        return forwarded_for.split(",")[0].split(":")[0]
    else:
        trusted_proxies = {'127.0.0.1'}
        route = request.access_route + [request.remote_addr]

        return next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)

def validate(schema):
    """Decorator to validate the JSON payload against a JSON schema"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            payload = None
            try:
                payload = request.get_json()
            except:
                raise error.NoJsonPayloadException()
            if payload is None:
                raise error.NoJsonPayloadException()
            else:
                try:
                    jsonschema.validate(payload, json.load(open(os.path.dirname(os.path.realpath(__file__)) + "/../schema/" + schema + ".json", "r")), format_checker=jsonschema.FormatChecker())
                    g.payload = payload
                except jsonschema.ValidationError as e:
                    raise error.MalformedPayloadException(e.message)
            return f(*args, **kw)
        return wrapper
    return decorator


def deprecated(fn):
    """Decorator to mark an endpoint as deprecated."""
    fn.is_deprecated = True
    return fn

def response(payload=None, status_code=200, error_code=None, error_message=None, success=None, empty=False, created=None):
    """Method to build the default API response"""
    if empty:
        response = ""
        status_code = 200
        r = Response()
    else:
        response = {}

        if payload is not None:
            response = payload
        elif success is not None or created is not None:
            response = {}
        if success is not None:
            response["success"] = success
        if created is not None:
            response["id"] = created

        if error_code is not None:
            error_response = {"errorCode": error_code}
            if error_message is not None:
                error_response["errorMessage"] = error_message
            response["error"] = error_response

        r = jsonify(**response)

        if error_code is not None:
            r.headers.add("X-ErrorCode", error_code)

    r.status_code = status_code

    return r

def hash_password(string):
    return str(hashlib.sha1(string.encode('utf-8')).hexdigest())
