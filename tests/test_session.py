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
    
def test_set_trial_not_global_admin(unauthorized_client, credentials):
    #Login as regular user
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    body = { "user_id": "1", "in_the_past": False }
    r = unauthorized_client.put("/user/trial", json=body)
    
    #Should not be available
    assert r.status_code == 403
    assert r.json["error"]["errorMessage"] == "Only global admin has access to this endpoint"
    
def test_delete_trial_not_global_admin(unauthorized_client, credentials):
    #Login as regular user
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    body = { "user_id": "1" }
    r = unauthorized_client.delete("/user/trial", json=body)
    
    #Should not be available
    assert r.status_code == 403
    assert r.json["error"]["errorMessage"] == "Only global admin has access to this endpoint"
    
def test_trial_period_timestamp(unauthorized_client, credentials):
    # Login as user with couch role
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    r = unauthorized_client.get("/user/info")
    
    # Timestamp shouldn't be here
    assert r.status_code == 200
    assert "trial_period_expire_date" not in r.json.keys()
    
    # Login as global admin
    admin_credentials = { "mail": "admin@fableplus.com", "password": "adminTest" }
    r = unauthorized_client.post("/user/login", json=admin_credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    # Set trial period for the first user
    body = { "user_id": "1", "in_the_past": False }
    r = unauthorized_client.put("/user/trial", json=body)
    
    assert r.status_code == 200
    
    # Login as the first user
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    r = unauthorized_client.get("/user/info")
    
    #Timestamp should be here
    assert r.status_code == 200
    assert "trial_period_expire_date" in r.json.keys()
    
def test_trial_period_not_expired(unauthorized_client, credentials):
    #Login as admin
    admin_credentials = { "mail": "admin@fableplus.com", "password": "adminTest" }
    r = unauthorized_client.post("/user/login", json=admin_credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    #Set trial period for the user to expire in the future
    body = { "user_id": "1", "in_the_past": False }
    r = unauthorized_client.put("/user/trial", json=body)
    
    assert r.status_code == 200
    
    #Login as the user
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    r = unauthorized_client.get("/user/info")
    
    #Should be no problem
    assert r.status_code == 200
    
def test_trial_period_expired(unauthorized_client, credentials):
    #Login as admin
    admin_credentials = { "mail": "admin@fableplus.com", "password": "adminTest" }
    r = unauthorized_client.post("/user/login", json=admin_credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    #Set trial period for the user to have already expired
    body = { "user_id": "1", "in_the_past": True }
    r = unauthorized_client.put("/user/trial", json=body)
    
    assert r.status_code == 200
    
    r = unauthorized_client.post("/user/login", json=credentials)
    
    token = r.json["token"]
    unauthorized_client.token = token
    
    r = unauthorized_client.get("/user/info")
    
    #Should not be successful
    assert r.status_code == 423
    assert r.json["error"]["errorCode"] == 1206
    assert r.json["error"]["errorMessage"] == "The trial period has expired"