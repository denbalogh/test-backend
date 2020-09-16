"""Static routes

Blueprint defining static API routes.
"""

from flask import Blueprint, send_file
from util import response
from util.auth import noauth
import config
import socket
import time

static = Blueprint("static", __name__)


@noauth
@static.route("/info", methods=["GET"])
def get_info():
    payload = {
        "app"        : config.APP_ID,
        "apiVersion" : config.VERSION,
        "environment": config.ENVIRONMENT,
        "serverTime" : time.time()
    }
    if config.ENVIRONMENT == "dev":
        payload["host"] = socket.gethostname()
    return response(payload=payload)

@static.route("/ping", methods=["GET"])
@noauth
def ping_backend():
    return response(empty=True)

@static.route("/error", methods=["GET"])
@noauth
def raise_error():
    raise Exception()

@static.route("/openapi.yaml", methods=["GET"])
@noauth
def serve_spec():
    return send_file("static/openapi.yaml")

@static.route("/doc.html", methods=["GET"])
@noauth
def render_doc():
    return send_file("static/doc.html")
