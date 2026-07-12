# User Flow Document

## Customer Journey

### 1. Guest Discovery

1. User opens `/`.
2. User browses featured marketplace entry points.
3. User opens `/categories` or `/products`.
4. User searches, filters by category/seller/price, and paginates products.
5. User opens `/products/{productId}`.
6. User can view product details, images, seller, variants, price, and stock.

### 2. Registration and Login

1. User opens `/register`.
2. User enters email, password, first name, last name, and optional phone.
3. Frontend validates form fields.
4. Frontend calls `POST /api/auth/register`.
5. Backend creates user/profile and returns user.
6. User opens `/login`.
7. Frontend calls `POST /api/auth/login`.
8. Backend returns access and refresh tokens.
9. User is routed to `/dashboard`.

### 3. Profile and Address Setup

1. User opens `/profile`.
2. Frontend calls `GET /api/customer/profile` and `GET /api/customer/addresses`.
3. User updates name/phone.
4. Frontend calls `PUT /api/customer/profile`.
5. User creates address.
6. Frontend calls `POST /api/customer/addresses`.
7. User marks address as default shipping.
8. Frontend calls `PUT /api/customer/addresses/{addressId}/default`.

### 4. Wishlist and Cart

1. User browses product listing or product detail.
2. User adds product to wishlist.
3. Frontend calls `POST /api/wishlist`.
4. User opens `/wishlist`.
5. Frontend calls `GET /api/wishlist`.
6. User moves item to cart.
7. Frontend calls `POST /api/wishlist/{itemId}/move-to-cart`.
8. User opens `/cart`.
9. Frontend calls `GET /api/cart`.
10. User updates quantity.
11. Frontend calls `PUT /api/cart/items/{itemId}`.

### 5. Checkout and Orders

1. User opens `/checkout`.
2. Frontend loads cart and saved addresses.
3. User selects shipping address and enters billing address.
4. Frontend calls `POST /api/orders`.
5. Backend validates inventory, calculates totals, creates order, and persists order items.
6. User is routed to order confirmation.
7. User opens `/orders`.
8. Frontend calls `GET /api/orders`.
9. User opens order detail.
10. Frontend calls `GET /api/orders/{orderId}`.

## Seller Journey

### 1. Seller Registration

1. Authenticated user opens `/seller`.
2. If no seller profile exists, user submits store name and description.
3. Frontend calls `POST /api/seller/profile`.
4. Backend creates seller profile.
5. Seller dashboard becomes available.

### 2. Seller Dashboard

1. Seller opens `/seller`.
2. Frontend calls `GET /api/seller/dashboard`.
3. Dashboard displays product count, active products, stock, orders, revenue, low stock, recent orders, and top products.

### 3. Product Management

1. Seller creates product with category, name, description, price, images, and variants.
2. Frontend calls `POST /api/seller/products`.
3. Seller edits product.
4. Frontend calls `PUT /api/seller/products/{productId}`.
5. Seller deletes product.
6. Frontend calls `DELETE /api/seller/products/{productId}`.

### 4. Inventory Management

1. Seller creates warehouse.
2. Frontend calls `POST /api/inventory/warehouses`.
3. Seller creates or updates stock.
4. Frontend calls `POST /api/inventory/stock`.
5. Dashboard and product availability use persisted inventory values.

## Admin Journey

### 1. Admin Login

1. Admin opens `/login`.
2. Admin submits credentials.
3. Frontend calls `POST /api/auth/login`.
4. Admin opens `/admin`.
5. Protected route and backend RBAC require admin role.

### 2. Dashboard

1. Admin opens Overview tab.
2. Frontend calls `GET /api/admin/dashboard`.
3. Admin views customers, sellers, categories, products, orders, revenue, pending sellers/products/reviews, inventory alerts, top products, top sellers, and recent orders.

### 3. User Management

1. Admin opens Users tab.
2. Frontend calls `GET /api/admin/users`.
3. Admin suspends or activates user.
4. Frontend calls `PATCH /api/admin/users/{userId}`.

### 4. Seller Moderation

1. Admin opens Sellers tab.
2. Frontend calls `GET /api/admin/sellers`.
3. Admin approves or rejects seller.
4. Frontend calls `PATCH /api/admin/sellers/{sellerId}`.

### 5. Product Moderation

1. Admin opens Products tab.
2. Frontend calls `GET /api/admin/products`.
3. Admin approves, hides, or features product.
4. Frontend calls `PATCH /api/admin/products/{productId}`.

### 6. Orders, Shipments, and Payments

1. Admin opens Orders tab.
2. Frontend calls `GET /api/admin/orders`.
3. Admin updates order status, creates shipment label, or refunds order.
4. Frontend calls admin order/shipment/refund endpoints.
5. Admin opens Payments tab.
6. Frontend calls `GET /api/admin/payments`.
7. Admin creates sandbox intent or updates payment status.

### 7. Reviews, Reports, Notifications, AI

1. Admin moderates reviews through Reviews tab.
2. Admin generates JSON/CSV/PDF-placeholder reports through Reports tab.
3. Admin sends persisted notifications through Notifications tab.
4. Admin uses AI tab or Product Details admin AI actions for recommendations, generated descriptions, and review summaries.

## Key Validation Checkpoints

- Register: duplicate email, weak password, invalid phone, invalid names.
- Profile/address: invalid phone, missing address fields, invalid postal code.
- Product: missing category/name/description, invalid image URL, invalid SKU, non-positive price.
- Inventory: negative quantity, reserved quantity greater than quantity.
- Cart: zero or negative quantity.
- Checkout: missing shipping address, invalid billing address, invalid coupon format.
- Admin: invalid status enum, invalid discount, empty notifications.
