from fastapi.testclient import TestClient


def register_customer(client: TestClient, email: str = "pat@example.com") -> dict[str, object]:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "S3curePass!",
            "first_name": "Pat",
            "last_name": "Rivera",
            "phone": "5550100100",
        },
    )
    assert response.status_code == 201
    return response.json()


def login_customer(client: TestClient, email: str = "pat@example.com") -> dict[str, object]:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "S3curePass!"},
    )
    assert response.status_code == 200
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_login_current_user_refresh_logout(client: TestClient) -> None:
    registered = register_customer(client)
    assert registered["email"] == "pat@example.com"
    assert registered["role"] == "customer"
    assert registered["profile"]["first_name"] == "Pat"

    duplicate = client.post(
        "/api/auth/register",
        json={
            "email": "pat@example.com",
            "password": "S3curePass!",
            "first_name": "Pat",
            "last_name": "Rivera",
        },
    )
    assert duplicate.status_code == 400

    tokens = login_customer(client)
    access_token = str(tokens["access_token"])
    refresh_token = str(tokens["refresh_token"])

    current = client.get("/api/auth/me", headers=auth_headers(access_token))
    assert current.status_code == 200
    assert current.json()["email"] == "pat@example.com"

    refreshed = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    rotated_refresh_token = refreshed.json()["refresh_token"]
    assert rotated_refresh_token != refresh_token

    old_refresh_reuse = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert old_refresh_reuse.status_code == 401

    logout = client.post("/api/auth/logout", json={"refresh_token": rotated_refresh_token})
    assert logout.status_code == 204

    refresh_after_logout = client.post(
        "/api/auth/refresh",
        json={"refresh_token": rotated_refresh_token},
    )
    assert refresh_after_logout.status_code == 401


def test_customer_profile_and_address_management(client: TestClient) -> None:
    register_customer(client, email="avery@example.com")
    tokens = login_customer(client, email="avery@example.com")
    headers = auth_headers(str(tokens["access_token"]))

    profile = client.get("/api/customer/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["last_name"] == "Rivera"

    updated_profile = client.put(
        "/api/customer/profile",
        headers=headers,
        json={"first_name": "Avery", "phone": "5550199000"},
    )
    assert updated_profile.status_code == 200
    assert updated_profile.json()["first_name"] == "Avery"
    assert updated_profile.json()["phone"] == "5550199000"

    first_address = client.post(
        "/api/customer/addresses",
        headers=headers,
        json={
            "label": "Home",
            "recipient_name": "Avery Rivera",
            "line1": "100 Market Street",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US",
            "is_default_shipping": True,
        },
    )
    assert first_address.status_code == 201
    first_address_id = first_address.json()["id"]
    assert first_address.json()["is_default_shipping"] is True

    second_address = client.post(
        "/api/customer/addresses",
        headers=headers,
        json={
            "label": "Office",
            "recipient_name": "Avery Rivera",
            "line1": "200 Commerce Avenue",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78702",
            "country": "US",
            "is_default_shipping": True,
        },
    )
    assert second_address.status_code == 201
    second_address_id = second_address.json()["id"]

    addresses = client.get("/api/customer/addresses", headers=headers)
    assert addresses.status_code == 200
    address_payload = addresses.json()
    assert len(address_payload) == 2
    assert sum(1 for address in address_payload if address["is_default_shipping"]) == 1
    assert address_payload[0]["id"] == second_address_id

    default_response = client.put(
        f"/api/customer/addresses/{first_address_id}/default",
        headers=headers,
    )
    assert default_response.status_code == 200
    assert default_response.json()["is_default_shipping"] is True

    delete_response = client.delete(
        f"/api/customer/addresses/{second_address_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    remaining = client.get("/api/customer/addresses", headers=headers)
    assert len(remaining.json()) == 1


def test_customer_validation_rejects_invalid_phone_password_and_names(
    client: TestClient,
) -> None:
    weak_password = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "password": "password",
            "first_name": "Pat",
            "last_name": "Rivera",
        },
    )
    assert weak_password.status_code == 422

    invalid_phone = client.post(
        "/api/auth/register",
        json={
            "email": "bad-phone@example.com",
            "password": "S3curePass!",
            "first_name": "Pat",
            "last_name": "Rivera",
            "phone": "555-ABCD",
        },
    )
    assert invalid_phone.status_code == 422

    invalid_name = client.post(
        "/api/auth/register",
        json={
            "email": "bad-name@example.com",
            "password": "S3curePass!",
            "first_name": "Pat2",
            "last_name": "Rivera",
        },
    )
    assert invalid_name.status_code == 422

    register_customer(client, email="validations@example.com")
    tokens = login_customer(client, email="validations@example.com")
    headers = auth_headers(str(tokens["access_token"]))

    invalid_profile_phone = client.put(
        "/api/customer/profile",
        headers=headers,
        json={"phone": "letters"},
    )
    assert invalid_profile_phone.status_code == 422

    invalid_address = client.post(
        "/api/customer/addresses",
        headers=headers,
        json={
            "label": "Home",
            "recipient_name": "Avery2 Rivera",
            "line1": "100 Market Street",
            "city": "Austin",
            "state": "TX",
            "postal_code": "ABC",
            "country": "US",
            "phone": "555 010 0100",
            "is_default_shipping": True,
        },
    )
    assert invalid_address.status_code == 422
