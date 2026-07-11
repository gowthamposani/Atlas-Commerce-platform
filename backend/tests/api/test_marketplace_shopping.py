from fastapi.testclient import TestClient


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client: TestClient, email: str) -> dict[str, object]:
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "S3curePass!",
            "first_name": "Market",
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


def test_marketplace_shopping_order_flow(client: TestClient) -> None:
    tokens = register_and_login(client, "market@example.com")
    headers = auth_headers(str(tokens["access_token"]))

    category_response = client.post(
        "/api/catalog/categories",
        headers=headers,
        json={"name": "Footwear", "description": "Shoes and boots"},
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    seller_response = client.post(
        "/api/seller/profile",
        headers=headers,
        json={"store_name": "Atlas Test Store", "description": "Integration seller"},
    )
    assert seller_response.status_code == 201

    product_response = client.post(
        "/api/seller/products",
        headers=headers,
        json={
            "category_id": category_id,
            "name": "Trail Runner",
            "description": "Inventory-backed trail running shoe",
            "base_price": 49.99,
            "status": "active",
            "images": [
                {
                    "url": "https://example.com/trail-runner.jpg",
                    "alt_text": "Trail Runner",
                    "is_primary": True,
                },
            ],
            "variants": [
                {
                    "sku": "TRAIL-BASE",
                    "name": "Standard",
                    "price_delta": 0,
                    "attributes": {"size": "standard"},
                    "is_active": True,
                },
            ],
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]
    assert product_response.json()["variants"][0]["sku"] == "TRAIL-BASE"

    warehouse_response = client.post(
        "/api/inventory/warehouses",
        headers=headers,
        json={
            "name": "Primary Warehouse",
            "code": "WH-MARKET-1",
            "city": "Austin",
            "state": "TX",
            "country": "US",
        },
    )
    assert warehouse_response.status_code == 201

    stock_response = client.post(
        "/api/inventory/stock",
        headers=headers,
        json={
            "product_id": product_id,
            "warehouse_id": warehouse_response.json()["id"],
            "quantity": 5,
            "reserved_quantity": 0,
            "reorder_level": 1,
        },
    )
    assert stock_response.status_code == 201

    search_response = client.get("/api/catalog/products", params={"search": "trail"})
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1

    detail_response = client.get(f"/api/catalog/products/{product_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["available_quantity"] == 5

    wishlist_response = client.post(
        "/api/wishlist",
        headers=headers,
        json={"product_id": product_id},
    )
    assert wishlist_response.status_code == 201

    move_response = client.post(
        f"/api/wishlist/{wishlist_response.json()['id']}/move-to-cart",
        headers=headers,
    )
    assert move_response.status_code == 200
    assert move_response.json()["item_count"] == 1
    cart_item_id = move_response.json()["items"][0]["id"]

    cart_update_response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers=headers,
        json={"quantity": 2},
    )
    assert cart_update_response.status_code == 200
    assert cart_update_response.json()["item_count"] == 2

    address_response = client.post(
        "/api/customer/addresses",
        headers=headers,
        json={
            "label": "Home",
            "recipient_name": "Market Tester",
            "line1": "100 Commerce Street",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US",
            "is_default_shipping": True,
        },
    )
    assert address_response.status_code == 201

    order_response = client.post(
        "/api/orders",
        headers=headers,
        json={
            "shipping_address_id": address_response.json()["id"],
            "billing_address": {
                "recipient_name": "Market Tester",
                "line1": "100 Commerce Street",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country": "US",
            },
            "payment_method": "placeholder",
        },
    )
    assert order_response.status_code == 201
    assert order_response.json()["status"] == "pending"
    assert order_response.json()["items"][0]["quantity"] == 2

    history_response = client.get("/api/orders", headers=headers)
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1

    cart_after_order = client.get("/api/cart", headers=headers)
    assert cart_after_order.status_code == 200
    assert cart_after_order.json()["item_count"] == 0

    cancel_response = client.post(
        f"/api/orders/{order_response.json()['id']}/cancel",
        headers=headers,
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
