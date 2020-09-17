# Overview

This minimal backend provides endpoints for basic user and team management, as well as the according controllers and SQLAlchemy models.

The application is tested with Python 3.8.3.

# Running the service

In the default configuration, the application is using a local SQLite database for persistent storage. It requires a running Redis instance. The Redis instance does not require any configuration. The application will read the Redis connection information from the environment variable `REDIS_HOST` (e.g. `REDIS_HOST=localhost:6379`), an optional password can be set via `REDIS_PASSWORD`.

After installing all requirements from `requirements.txt` the service can be started with `python -m flask run`, or alternatively by running the main file `python main.py`.

# Using the service

To generate some accounts that can be used to login, a setup script is provided: `python setup.py`. After running the setup script, a login-request can be sent to `POST /tpa/v1/user/login` using credentials `coach@fableplus.com:test123`.

The login-request will return a token that can be used to authenticate for further requests. The token needs to be used as a bearer token in the `Authentication` header.

# Running the tests

For running the provided pytest test-cases, the dependencies from `test.requirements.txt` need to be installed. Afterwards the tests can be run with `python -m pytest ./tests`