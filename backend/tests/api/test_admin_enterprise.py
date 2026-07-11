from app.database.session import SessionLocal
from app.models.user import User, UserRole
from fastapi.testclient import TestClient


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client: TestClient, email: str) -> dict[str, object]:
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "S3curePass!",
            "first_name": "Admin",
            "last_name": "Tester",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "S3curePass!"},
    )
    assert login_response.status_code == 200
    return login_response.json()


def promote_to_admin(user_id: str) -> None:
    with SessionLocal() as db:
        user = db.get(User, user_id)
        assert user is not None
        user.role = UserRole.ADMIN
        db.commit()


def test_admin_moderation_reports_payments_and_ai(client: TestClient) -> None:
    admin_tokens = register_and_login(client, "admin@example.com")
    seller_tokens = register_and_login(client, "seller-admin-flow@example.com")
    promote_to_admin(str(admin_tokens["user"]["id"]))
    admin_headers = auth_headers(str(admin_tokens["access_token"]))
    seller_headers = auth_headers(str(seller_tokens["access_token"]))

    category_response = client.post(
        "/api/catalog/categories",
        headers=seller_headers,
        json={"name": "Admin Test Gear"},
    )
    assert category_response.status_code == 201

    seller_response = client.post(
        "/api/seller/profile",
        headers=seller_headers,
        json={"store_name": "Moderated Seller"},
    )
    assert seller_response.status_code == 201

    product_response = client.post(
        "/api/seller/products",
        headers=seller_headers,
        json={
            "category_id": category_response.json()["id"],
            "name": "Moderated Product",
            "description": "Product used for admin moderation",
            "brand": "Atlas",
            "base_price": 25.0,
            "status": "draft",
            "images": [],
            "variants": [],
        },
    )
    assert product_response.status_code == 201

    dashboard_response = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["stats"]["total_sellers"] == 1

    seller_moderation = client.patch(
        f"/api/admin/sellers/{seller_response.json()['id']}",
        headers=admin_headers,
        json={"status": "approved"},
    )
    assert seller_moderation.status_code == 200
    assert seller_moderation.json()["moderation_status"] == "approved"

    product_moderation = client.patch(
        f"/api/admin/products/{product_response.json()['id']}",
        headers=admin_headers,
        json={"status": "active", "is_visible": True, "is_featured": True},
    )
    assert product_moderation.status_code == 200
    assert product_moderation.json()["is_featured"] is True

    review_response = client.post(
        "/api/reviews",
        headers=seller_headers,
        json={
            "product_id": product_response.json()["id"],
            "rating": 5,
            "title": "Excellent",
            "body": "Strong marketplace quality.",
        },
    )
    assert review_response.status_code == 201

    review_moderation = client.patch(
        f"/api/admin/reviews/{review_response.json()['id']}",
        headers=admin_headers,
        json={"status": "approved"},
    )
    assert review_moderation.status_code == 200
    assert review_moderation.json()["status"] == "approved"

    report_response = client.get("/api/admin/reports/sellers", headers=admin_headers)
    assert report_response.status_code == 200
    assert report_response.json()["rows"][0]["status"] == "approved"

    ai_response = client.post(
        f"/api/admin/ai/products/{product_response.json()['id']}/description",
        headers=admin_headers,
    )
    assert ai_response.status_code == 200
    assert "Moderated Product" in ai_response.json()["description"]
