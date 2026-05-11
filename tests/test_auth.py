def test_signup_and_login(client):
    signup_response = client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "password1234", "name": "tester"},
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password1234"},
    )
    assert login_response.status_code == 200
    data = login_response.get_json()["data"]
    assert "access_token" in data

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me_response.status_code == 200
