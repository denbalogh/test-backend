from flask.testing import FlaskClient

import config

class TestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self._token = None
        super(TestClient, self).__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        if self._token is not None:
            headers = kwargs.get("headers", None)
            if headers is None:
                headers =  {}
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers

        if "path" in kwargs and not kwargs["path"].startswith(config.BASE_ROUTE):
            kwargs["path"] = config.BASE_ROUTE + kwargs["path"]
        elif len(args) == 1 and not args[0].startswith(config.BASE_ROUTE):
            args = tuple([config.BASE_ROUTE + args[0]] + list(args[1:]))

        return super().open(*args, **kwargs)

    def login(self, credentials):
        r = self.post("/user/login", json=credentials)
        self.token = r.json["token"]

    def logout(self):
        self.post("/user/logout")
        self.token = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
