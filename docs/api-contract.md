# API Documentation

## Base URL

Local Docker Compose backend:

```text
http://localhost:8001/api
```

Swagger UI:

```text
http://localhost:8001/docs
```

## Authentication

Protected APIs use:

```text
Authorization: Bearer <access_token>
```

Auth levels used below:

- Public: no token required.
- Authenticated: valid active user access token required.
- Customer/Admin: user must have customer or admin role.
- Admin: user must have admin role.

## Authentication APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/auth/register` | Register customer account | Public | `email`, `password`, `first_name`, `last_name`, optional `phone` | `CurrentUserResponse` |
| POST | `/api/auth/login` | Login and issue tokens | Public | `email`, `password` | `TokenResponse` |
| POST | `/api/auth/refresh` | Rotate refresh token | Public | `refresh_token` | `TokenResponse` |
| POST | `/api/auth/logout` | Revoke refresh token | Public | `refresh_token` | `204 No Content` |
| GET | `/api/auth/me` | Return current user | Authenticated | none | `CurrentUserResponse` |

## Customer APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/customer/profile` | Get customer profile | Customer/Admin | none | `CustomerProfileResponse` |
| PUT | `/api/customer/profile` | Update customer profile | Customer/Admin | optional `first_name`, `last_name`, `phone` | `CustomerProfileResponse` |
| GET | `/api/customer/dashboard` | Customer metrics and recent orders | Customer/Admin | none | `CustomerDashboardResponse` |
| GET | `/api/customer/addresses` | List addresses | Customer/Admin | none | `AddressResponse[]` |
| POST | `/api/customer/addresses` | Create address | Customer/Admin | address payload | `AddressResponse` |
| PUT | `/api/customer/addresses/{address_id}` | Update address | Customer/Admin | partial address payload | `AddressResponse` |
| PUT | `/api/customer/addresses/{address_id}/default` | Set default shipping address | Customer/Admin | none | `AddressResponse` |
| DELETE | `/api/customer/addresses/{address_id}` | Delete address | Customer/Admin | none | `204 No Content` |

## Catalog APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/catalog/categories` | List categories | Public | none | `CategoryResponse[]` |
| POST | `/api/catalog/categories` | Create category | Authenticated | `name`, optional `description`, `is_active` | `CategoryResponse` |
| PUT | `/api/catalog/categories/{category_id}` | Update category | Authenticated | partial category payload | `CategoryResponse` |
| DELETE | `/api/catalog/categories/{category_id}` | Delete category | Authenticated | none | `204 No Content` |
| GET | `/api/catalog/products` | Search/filter/paginate products | Public | query: `search`, `category_id`, `seller_id`, `min_price`, `max_price`, `page`, `page_size` | `ProductPageResponse` |
| GET | `/api/catalog/products/{product_id}` | Product detail | Public | none | `ProductDetailResponse` |

## Seller APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/seller/profile` | Register seller profile | Authenticated | `store_name`, optional `description` | `SellerResponse` |
| GET | `/api/seller/profile` | Get own seller profile | Authenticated seller | none | `SellerResponse` |
| PUT | `/api/seller/profile` | Update seller profile | Authenticated seller | optional `store_name`, `description`, `is_active` | `SellerResponse` |
| GET | `/api/seller/dashboard` | Seller metrics | Authenticated seller | none | `SellerDashboardResponse` |
| GET | `/api/seller/stores/{seller_id}` | Public seller store | Public | none | `SellerResponse` |
| GET | `/api/seller/products` | List own seller products | Authenticated seller | none | `ProductListResponse[]` |
| POST | `/api/seller/products` | Create seller product | Authenticated seller | product payload | `ProductDetailResponse` |
| PUT | `/api/seller/products/{product_id}` | Update seller product | Authenticated seller owner | product update payload | `ProductDetailResponse` |
| DELETE | `/api/seller/products/{product_id}` | Delete seller product | Authenticated seller owner | none | `204 No Content` |

## Inventory APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/inventory/warehouses` | List seller warehouses | Authenticated seller | none | `WarehouseResponse[]` |
| POST | `/api/inventory/warehouses` | Create warehouse | Authenticated seller | warehouse payload | `WarehouseResponse` |
| PUT | `/api/inventory/warehouses/{warehouse_id}` | Update warehouse | Authenticated seller owner | warehouse update payload | `WarehouseResponse` |
| GET | `/api/inventory/stock` | List seller stock | Authenticated seller | none | `InventoryResponse[]` |
| POST | `/api/inventory/stock` | Upsert stock | Authenticated seller owner | stock payload | `InventoryResponse` |
| POST | `/api/inventory/validate` | Validate product stock | Public | `product_id`, optional `variant_id`, `quantity` | `InventoryValidationResponse` |

## Wishlist APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/wishlist` | List wishlist | Authenticated | none | `WishlistItemResponse[]` |
| POST | `/api/wishlist` | Add product to wishlist | Authenticated | `product_id`, optional `variant_id` | `WishlistItemResponse` |
| DELETE | `/api/wishlist/{item_id}` | Remove wishlist item | Authenticated owner | none | `204 No Content` |
| POST | `/api/wishlist/{item_id}/move-to-cart` | Move wishlist item to cart | Authenticated owner | none | `CartSummaryResponse` |

## Cart APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/cart` | Get cart summary | Authenticated | none | `CartSummaryResponse` |
| POST | `/api/cart/items` | Add item to cart | Authenticated | `product_id`, optional `variant_id`, `quantity` | `CartSummaryResponse` |
| PUT | `/api/cart/items/{item_id}` | Update cart quantity | Authenticated owner | `quantity` | `CartSummaryResponse` |
| DELETE | `/api/cart/items/{item_id}` | Remove cart item | Authenticated owner | none | `CartSummaryResponse` |

## Order APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/orders` | Create order from checkout | Authenticated | `shipping_address_id`, `billing_address`, optional `coupon_code`, `payment_method` | `OrderResponse` |
| GET | `/api/orders` | List own order history | Authenticated | none | `OrderResponse[]` |
| GET | `/api/orders/{order_id}` | Get own order detail | Authenticated owner | none | `OrderResponse` |
| POST | `/api/orders/{order_id}/cancel` | Cancel own order | Authenticated owner | none | `OrderResponse` |
| PUT | `/api/orders/{order_id}/status` | Update own order status endpoint | Authenticated owner | `status` | `OrderResponse` |

## Review APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/reviews` | Create product review | Authenticated | `product_id`, `rating`, optional `title`, `body` | `ReviewResponse` |

## Admin APIs

| Method | URL | Purpose | Auth | Request | Response |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/admin/dashboard` | Admin dashboard metrics | Admin | none | `AdminDashboardResponse` |
| GET | `/api/admin/stats` | Admin aggregate stats | Admin | none | `AdminStatsResponse` |
| GET | `/api/admin/users` | List/search users | Admin | query: optional `search` | `AdminUserResponse[]` |
| PATCH | `/api/admin/users/{user_id}` | Activate/suspend user | Admin | `is_active` | `AdminUserResponse` |
| DELETE | `/api/admin/users/{user_id}` | Soft-delete user | Admin | none | `204 No Content` |
| GET | `/api/admin/sellers` | List sellers | Admin | none | `SellerResponse[]` |
| PATCH | `/api/admin/sellers/{seller_id}` | Moderate seller | Admin | `status` | `SellerResponse` |
| GET | `/api/admin/sellers/{seller_id}/analytics` | Seller analytics | Admin | none | analytics object |
| GET | `/api/admin/products` | List products for moderation | Admin | optional `status_filter` | `ProductListResponse[]` |
| PATCH | `/api/admin/products/{product_id}` | Moderate product | Admin | status/visibility/featured/brand fields | `ProductListResponse` |
| PATCH | `/api/admin/products/{product_id}/brand` | Update product brand | Admin | `brand` | `ProductListResponse` |
| GET | `/api/admin/catalog` | Admin catalog reference | Admin | none | `CatalogAdminResponse` |
| POST | `/api/admin/coupons` | Create coupon | Admin | code/type/value/active | `CouponResponse` |
| GET | `/api/admin/orders` | List all orders | Admin | none | `OrderResponse[]` |
| PATCH | `/api/admin/orders/{order_id}/status` | Update order status | Admin | `status` | `OrderResponse` |
| POST | `/api/admin/orders/{order_id}/refund` | Refund order | Admin | none | `OrderResponse` |
| POST | `/api/admin/orders/{order_id}/shipments` | Create shipment | Admin | shipment payload | `ShipmentResponse` |
| GET | `/api/admin/shipments` | List shipments | Admin | none | `ShipmentResponse[]` |
| GET | `/api/admin/reviews` | List reviews | Admin | none | `ReviewResponse[]` |
| PATCH | `/api/admin/reviews/{review_id}` | Moderate review | Admin | `status`, optional `report_reason` | `ReviewResponse` |
| GET | `/api/admin/reports/{name}` | JSON report | Admin | report name | `ReportResponse` |
| GET | `/api/admin/reports/{name}.csv` | CSV report | Admin | report name | `text/csv` |
| GET | `/api/admin/reports/{name}.pdf` | PDF placeholder report | Admin | report name | `application/pdf` bytes |
| GET | `/api/admin/notifications` | List notifications | Admin | none | `NotificationResponse[]` |
| POST | `/api/admin/notifications` | Create notification | Admin | optional user, type, title, message | `NotificationResponse` |
| GET | `/api/admin/payments` | List payments | Admin | none | `PaymentResponse[]` |
| POST | `/api/admin/payments/stripe-sandbox` | Create sandbox payment intent | Admin | `order_id`, optional `provider_reference` | `PaymentResponse` |
| PATCH | `/api/admin/payments/{payment_id}` | Update payment status | Admin | `status` | `PaymentResponse` |
| GET | `/api/admin/ai/products/{product_id}/recommendations` | Internal recommendation helper | Admin | product id | `RecommendationResponse` |
| POST | `/api/admin/ai/products/{product_id}/description` | Internal description generator | Admin | product id | `GeneratedDescriptionResponse` |
| GET | `/api/admin/ai/products/{product_id}/reviews` | Internal review summary helper | Admin | product id | `ReviewSummaryResponse` |

## Important Request Shapes

### Product Payload

```json
{
  "category_id": "category-id",
  "name": "Product Name",
  "description": "Description",
  "brand": "Brand",
  "base_price": 99.99,
  "status": "active",
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "alt_text": "Image alt",
      "sort_order": 0,
      "is_primary": true
    }
  ],
  "variants": [
    {
      "sku": "SKU-001",
      "name": "Default",
      "price_delta": 0,
      "attributes": {},
      "is_active": true
    }
  ]
}
```

### Checkout Payload

```json
{
  "shipping_address_id": "address-id",
  "billing_address": {
    "recipient_name": "Demo Customer",
    "line1": "123 Market Street",
    "line2": null,
    "city": "Austin",
    "state": "TX",
    "postal_code": "78701",
    "country": "US"
  },
  "coupon_code": null,
  "payment_method": "placeholder"
}
```

## Standard Error Behavior

- `401`: missing, expired, invalid, or wrong token type.
- `403`: authenticated user lacks required role.
- `404`: requested resource not found.
- `400`: business rule violation.
- `422`: request validation failure.
