def test_unauthorized(unauthorized_client):
    r = unauthorized_client.get("/user/info")

    assert r.status_code == 401

def test_invalid_token(unauthorized_client):
    unauthorized_client.token = "invalid_token"
    r = unauthorized_client.get("/user/info")

    assert r.status_code == 401, r.json
    assert r.json["error"]["errorCode"] == 1103

    unauthorized_client.token = None

def test_login_wrong_password(unauthorized_client, credentials):
    r = unauthorized_client.post("/user/login", json={"mail": credentials["mail"], "password" : credentials["password"]+"_invalid"})
    assert r.status_code == 403
    assert r.json["error"]["errorCode"] == 1203

def test_login_logout(unauthorized_client, credentials):
    r = unauthorized_client.post("/user/login", json=credentials)
    assert r.status_code == 200
    assert "token" in r.json

    token = r.json["token"]
    unauthorized_client.token = token

    r = unauthorized_client.get("/user/info")
    assert r.status_code == 200
    assert r.json["mail"] == credentials["mail"]

    r = unauthorized_client.post("/user/logout")
    assert r.status_code == 200

    r = unauthorized_client.get("/user/info")
    assert r.status_code == 401

def test_login_nonexisting(unauthorized_client):
    credentials = {"mail": "blablablubb@nomail.com", "password" : "BlaBla"}
    r = unauthorized_client.post("/user/login", json=credentials)
    assert r.status_code in [403, 404]