# Functional Requirements Document

## Document Purpose

This FRD describes the functional behavior of Atlas Commerce Platform as implemented in the repository. Each module includes purpose, inputs, outputs, business rules, validations, and APIs used.

## Authentication

### Register

- Purpose: create a customer account and initial customer profile.
- Inputs: `email`, `password`, `first_name`, `last_name`, optional `phone`.
- Outputs: current user payload with profile.
- Business rules: email must be unique; new users default to customer role; password is hashed before persistence.
- Validations: email format and lowercase normalization; password length and complexity; names required and cannot contain numbers; phone may contain optional leading `+` and 10-15 digits by default.
- API used: `POST /api/auth/register`.

### Login

- Purpose: authenticate user credentials and issue access/refresh tokens.
- Inputs: `email`, `password`.
- Outputs: JWT access token, refresh token, token type, current user.
- Business rules: inactive users cannot authenticate; invalid credentials return unauthorized.
- Validations: email format; password present.
- API used: `POST /api/auth/login`.

### Refresh Token

- Purpose: rotate a valid refresh token and issue a new access/refresh pair.
- Inputs: `refresh_token`.
- Outputs: new access token, new refresh token, current user.
- Business rules: old refresh token is revoked; token hash is persisted; invalid/revoked/expired tokens are rejected.
- Validations: refresh token required.
- API used: `POST /api/auth/refresh`.

### Logout

- Purpose: revoke a refresh token.
- Inputs: `refresh_token`.
- Outputs: `204 No Content`.
- Business rules: persisted token is marked revoked.
- Validations: refresh token required.
- API used: `POST /api/auth/logout`.

### Current User

- Purpose: return authenticated user identity and profile.
- Inputs: bearer access token.
- Outputs: user id, email, role, active flag, profile.
- Business rules: token type must be `access`; inactive users are rejected.
- Validations: JWT decode and subject lookup.
- API used: `GET /api/auth/me`.

## Customer

### Customer Dashboard

- Purpose: show customer order, wishlist, cart, and recent order counts.
- Inputs: bearer token.
- Outputs: `total_orders`, `wishlist_items`, `cart_items`, `recent_orders`.
- Business rules: metrics are scoped to the authenticated user.
- Validations: authenticated customer/admin user.
- API used: `GET /api/customer/dashboard`.

### Profile

- Purpose: retrieve and update customer identity information.
- Inputs: optional `first_name`, `last_name`, `phone`.
- Outputs: customer profile.
- Business rules: user can only access their own profile.
- Validations: names length and character rules; phone 10-15 digits with optional leading `+`.
- APIs used: `GET /api/customer/profile`, `PUT /api/customer/profile`.

### Address Management

- Purpose: manage saved addresses and default shipping address.
- Inputs: label, recipient name, address lines, city, state, postal code, country, optional phone, default shipping flag.
- Outputs: address records.
- Business rules: users can manage only their own addresses; setting one default clears previous defaults.
- Validations: required address fields, recipient name, postal code by country, optional phone rules.
- APIs used: `GET /api/customer/addresses`, `POST /api/customer/addresses`, `PUT /api/customer/addresses/{address_id}`, `PUT /api/customer/addresses/{address_id}/default`, `DELETE /api/customer/addresses/{address_id}`.

## Marketplace

### Categories

- Purpose: organize product browsing.
- Inputs: name, optional description, active flag.
- Outputs: category list or category detail.
- Business rules: category slugs are generated from names; inactive categories may be excluded from customer browsing depending on service filtering.
- Validations: name required and trimmed; description sanitized.
- APIs used: `GET /api/catalog/categories`, `POST /api/catalog/categories`, `PUT /api/catalog/categories/{category_id}`, `DELETE /api/catalog/categories/{category_id}`.

### Product Listing, Search, Filters, Pagination

- Purpose: allow guests and users to browse catalog items.
- Inputs: optional `search`, `category_id`, `seller_id`, `min_price`, `max_price`, `page`, `page_size`.
- Outputs: paged product list with total count.
- Business rules: search text is trimmed; empty search is treated as no search; minimum price cannot exceed maximum price.
- Validations: max search length 120; page >= 1; page size between 1 and 100; price filters non-negative.
- API used: `GET /api/catalog/products`.

### Product Details

- Purpose: show full product detail, images, variants, seller, category, and available quantity.
- Inputs: product id.
- Outputs: product detail.
- Business rules: available quantity is calculated from inventory.
- Validations: product must exist.
- API used: `GET /api/catalog/products/{product_id}`.

### Seller Store Page

- Purpose: show public seller profile and products by seller.
- Inputs: seller id.
- Outputs: seller profile and product listing filtered by seller.
- Business rules: seller store lookup does not require authentication.
- Validations: seller must exist.
- APIs used: `GET /api/seller/stores/{seller_id}`, `GET /api/catalog/products?seller_id=...`.

## Seller

### Seller Registration and Profile

- Purpose: let authenticated users create and update a seller profile.
- Inputs: store name, optional description, active flag on update.
- Outputs: seller profile.
- Business rules: one seller profile per user; new sellers begin with moderation status from the service/model defaults.
- Validations: store name length and trimming; description sanitized.
- APIs used: `POST /api/seller/profile`, `GET /api/seller/profile`, `PUT /api/seller/profile`.

### Seller Dashboard

- Purpose: summarize seller products, revenue, orders, stock, low stock, recent orders, and top products.
- Inputs: bearer token for seller account.
- Outputs: seller metrics.
- Business rules: all metrics are scoped to the authenticated seller profile.
- Validations: seller profile must exist.
- API used: `GET /api/seller/dashboard`.

### Seller Product Management

- Purpose: create, update, list, and delete seller-owned products.
- Inputs: category id, name, description, brand, base price, status, images, variants.
- Outputs: product records.
- Business rules: seller can manage only products owned by their seller profile; product slugs are generated; variant SKUs must be unique in payload and database.
- Validations: required product fields; positive price; valid image URLs; SKU format; non-negative variant price delta.
- APIs used: `GET /api/seller/products`, `POST /api/seller/products`, `PUT /api/seller/products/{product_id}`, `DELETE /api/seller/products/{product_id}`.

## Inventory

### Warehouse Management

- Purpose: manage seller fulfillment locations.
- Inputs: name, code, city, state, country, active flag on update.
- Outputs: warehouse records.
- Business rules: warehouse codes are unique; warehouses are scoped to seller profile.
- Validations: code format; required location fields; country uppercasing.
- APIs used: `GET /api/inventory/warehouses`, `POST /api/inventory/warehouses`, `PUT /api/inventory/warehouses/{warehouse_id}`.

### Stock Management and Validation

- Purpose: track quantity, reserved quantity, reorder level, and available stock.
- Inputs: product id, optional variant id, warehouse id, quantity, reserved quantity, reorder level.
- Outputs: inventory records or validation result.
- Business rules: reserved quantity cannot exceed total quantity; inventory is unique per product/variant/warehouse; validation endpoint may be used before cart/checkout.
- Validations: quantity and reorder fields non-negative; requested validation quantity > 0.
- APIs used: `GET /api/inventory/stock`, `POST /api/inventory/stock`, `POST /api/inventory/validate`.

## Wishlist

- Purpose: let customers save products for later and move items into cart.
- Inputs: product id, optional variant id, wishlist item id for remove/move.
- Outputs: wishlist item list or cart summary.
- Business rules: a user cannot duplicate the same product/variant in wishlist; move-to-cart removes or transitions saved interest into cart behavior through service logic.
- Validations: authenticated user; product must exist.
- APIs used: `GET /api/wishlist`, `POST /api/wishlist`, `DELETE /api/wishlist/{item_id}`, `POST /api/wishlist/{item_id}/move-to-cart`.

## Cart

- Purpose: maintain customer purchase intent.
- Inputs: product id, optional variant id, quantity, cart item id.
- Outputs: cart summary with subtotal, item count, and inventory-valid flag.
- Business rules: same product/variant is unique per user cart; quantities must be positive; cart total is calculated from product base price and variant delta.
- Validations: authenticated user; product exists; quantity > 0.
- APIs used: `GET /api/cart`, `POST /api/cart/items`, `PUT /api/cart/items/{item_id}`, `DELETE /api/cart/items/{item_id}`.

## Checkout

- Purpose: convert cart items into an order.
- Inputs: shipping address id, billing address, optional coupon code, payment method.
- Outputs: created order.
- Business rules: checkout validates inventory, calculates subtotal, tax, shipping charge, discount, and total; payment method defaults to placeholder.
- Validations: authenticated user; selected shipping address belongs to user; required billing fields; postal code; valid coupon code format.
- API used: `POST /api/orders`.

## Orders

- Purpose: track purchase history and fulfillment status.
- Inputs: order id, status update payload for supported status endpoints.
- Outputs: order list or order detail.
- Business rules: customers can access only their own orders; cancellation changes order state through service logic; order status values include pending, confirmed, packed, shipped, delivered, cancelled, refunded.
- Validations: authenticated user; order ownership; valid status enum.
- APIs used: `GET /api/orders`, `GET /api/orders/{order_id}`, `POST /api/orders/{order_id}/cancel`, `PUT /api/orders/{order_id}/status`.

## Admin

### Dashboard and Stats

- Purpose: provide operational overview.
- Inputs: admin bearer token.
- Outputs: platform metrics, recent orders, pending counts, inventory alerts, top products, top sellers.
- Business rules: admin-only RBAC.
- Validations: user role must be admin.
- APIs used: `GET /api/admin/dashboard`, `GET /api/admin/stats`.

### User Management

- Purpose: list, search, suspend, activate, and soft-delete users.
- Inputs: optional search query; active flag; user id.
- Outputs: user records or no content.
- Business rules: admin-only; delete marks inactive rather than hard-deleting.
- Validations: target user must exist.
- APIs used: `GET /api/admin/users`, `PATCH /api/admin/users/{user_id}`, `DELETE /api/admin/users/{user_id}`.

### Seller Management

- Purpose: moderate sellers and review seller analytics.
- Inputs: seller id, moderation status.
- Outputs: seller records or analytics object.
- Business rules: moderation status controls seller active flag.
- Validations: valid moderation enum; seller must exist.
- APIs used: `GET /api/admin/sellers`, `PATCH /api/admin/sellers/{seller_id}`, `GET /api/admin/sellers/{seller_id}/analytics`.

### Product Management

- Purpose: moderate products, visibility, featured state, and brand.
- Inputs: product id, status, visibility flag, featured flag, brand.
- Outputs: product records.
- Business rules: admin can change catalog governance fields.
- Validations: valid status enum; brand trimmed.
- APIs used: `GET /api/admin/products`, `PATCH /api/admin/products/{product_id}`, `PATCH /api/admin/products/{product_id}/brand`, `GET /api/admin/catalog`.

### Coupons

- Purpose: create discount codes for checkout.
- Inputs: code, discount type, discount value, active flag.
- Outputs: coupon record.
- Business rules: percent discounts cannot exceed 100; coupon code uppercased.
- Validations: code format; discount value > 0.
- API used: `POST /api/admin/coupons`.

### Admin Orders and Shipments

- Purpose: manage marketplace orders, refunds, and shipment records.
- Inputs: order id, order status, shipment provider/label/tracking/status.
- Outputs: order or shipment records.
- Business rules: admin can update operational order status; refund sets refunded flow; shipment creation updates order shipment fields.
- Validations: valid order/shipment status enum; order must exist.
- APIs used: `GET /api/admin/orders`, `PATCH /api/admin/orders/{order_id}/status`, `POST /api/admin/orders/{order_id}/refund`, `POST /api/admin/orders/{order_id}/shipments`, `GET /api/admin/shipments`.

### Review Moderation

- Purpose: create and moderate product reviews.
- Inputs: review rating/title/body; moderation status and optional report reason.
- Outputs: review records.
- Business rules: authenticated users can create reviews; admins moderate review status.
- Validations: rating 1-5; body required; valid moderation status.
- APIs used: `POST /api/reviews`, `GET /api/admin/reviews`, `PATCH /api/admin/reviews/{review_id}`.

### Reports

- Purpose: provide admin data extracts.
- Inputs: report name, format.
- Outputs: JSON report, CSV, or PDF placeholder bytes.
- Business rules: supported report names include sales, inventory, sellers, and a default user-style report for other names.
- Validations: admin-only.
- APIs used: `GET /api/admin/reports/{name}`, `GET /api/admin/reports/{name}.csv`, `GET /api/admin/reports/{name}.pdf`.

### Notifications

- Purpose: persist admin/customer/seller/payment notifications.
- Inputs: optional user id, type, title, message.
- Outputs: notification records.
- Business rules: persisted notifications are not externally delivered in this release.
- Validations: title and message required; valid notification type enum.
- APIs used: `GET /api/admin/notifications`, `POST /api/admin/notifications`.

### Payments

- Purpose: demonstrate payment administration through sandbox transactions.
- Inputs: order id, optional provider reference, payment status update.
- Outputs: payment transaction records.
- Business rules: provider defaults to `stripe_sandbox`; no real payment gateway call is made; payment status updates sync to order payment status.
- Validations: order exists; valid payment status enum.
- APIs used: `GET /api/admin/payments`, `POST /api/admin/payments/stripe-sandbox`, `PATCH /api/admin/payments/{payment_id}`.

### AI

- Purpose: provide internal demo helpers for recommendations, product description, and review summaries.
- Inputs: product id.
- Outputs: recommended product list, generated description text, review summary.
- Business rules: deterministic internal logic; no external AI provider is integrated.
- Validations: product must exist; admin-only.
- APIs used: `GET /api/admin/ai/products/{product_id}/recommendations`, `POST /api/admin/ai/products/{product_id}/description`, `GET /api/admin/ai/products/{product_id}/reviews`.
