import os
from urllib.parse import urlparse, urlunparse

import dotenv

# If a .env file is present, load it
dotenv.load_dotenv()

VERSION = "1"

APP_ID = "tpa"
APP_URL = os.environ.get("APP_URL", "")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
IN_DOCKER = os.environ.get("IN_DOCKER", "false").lower() == "true"

BASE_ROUTE = "/tpa/v" + VERSION

DEFAULT_REDIS = "localhost:6379"
DEFAULT_DB = "sqlite:///dev.db"

REDIS = os.environ.get("REDIS_HOST", DEFAULT_REDIS)
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

DB_URI = os.environ.get("DB_URI", DEFAULT_DB)

DEBUG = os.environ.get("DEBUG", "false" if ENVIRONMENT == "live" else "true").lower() == "true"

APP_SECRET = "supersecuresecret"
