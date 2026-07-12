# Database Design

## Overview

Atlas Commerce Platform uses PostgreSQL as the transactional database. SQLAlchemy models define tables and relationships, while Alembic manages schema migrations. Most tables use string UUID primary keys and timestamp columns for auditability.

## Textual ER Diagram

```text
users
  1 -> 1 customer_profiles
  1 -> many addresses
  1 -> many refresh_tokens
  1 -> many wishlist_items
  1 -> many cart_items
  1 -> many orders
  1 -> many product_reviews
  1 -> many notifications
  1 -> many audit_logs as actor
  1 -> 0..1 seller_profiles

seller_profiles
  1 -> many products
  1 -> many warehouses
  1 -> many order_items

categories
  1 -> many products

products
  1 -> many product_images
  1 -> many product_variants
  1 -> many inventory_items
  1 -> many wishlist_items
  1 -> many cart_items
  1 -> many order_items
  1 -> many product_reviews

product_variants
  1 -> many inventory_items
  1 -> many wishlist_items
  1 -> many cart_items
  1 -> many order_items

warehouses
  1 -> many inventory_items

addresses
  1 -> many orders as shipping_address

orders
  1 -> many order_items
  1 -> many payment_transactions
  1 -> many shipments
```

## Tables

### users

- Purpose: account identity and RBAC role.
- Primary key: `id`.
- Important columns: `email`, `hashed_password`, `role`, `is_active`, `created_at`, `updated_at`.
- Unique/indexes: unique indexed `email`.
- Relationships: profile, addresses, refresh tokens, seller profile, shopping/order/review/notification ownership.

### customer_profiles

- Purpose: customer first name, last name, and phone.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id` with cascade delete.
- Unique/indexes: unique indexed `user_id`.

### addresses

- Purpose: customer shipping/billing address book.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id` with cascade delete.
- Important columns: `label`, `recipient_name`, `line1`, `line2`, `city`, `state`, `postal_code`, `country`, `phone`, `is_default_shipping`.
- Indexes: `user_id`.

### refresh_tokens

- Purpose: persisted refresh token hashes for rotation/logout.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id` with cascade delete.
- Unique/indexes: unique indexed `token_hash`, indexed `user_id`.
- Important columns: `expires_at`, `revoked_at`, `created_at`.

### categories

- Purpose: product classification.
- Primary key: `id`.
- Unique/indexes: unique indexed `slug`.
- Important columns: `name`, `description`, `is_active`.

### seller_profiles

- Purpose: seller store identity and moderation state.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id` with cascade delete.
- Unique/indexes: unique indexed `user_id`, unique indexed `slug`.
- Important columns: `store_name`, `description`, `moderation_status`, `is_active`.

### products

- Purpose: sellable catalog item.
- Primary key: `id`.
- Foreign keys: `seller_id -> seller_profiles.id`, `category_id -> categories.id`.
- Unique/indexes: unique indexed `slug`; indexed `seller_id`, `category_id`.
- Important columns: `name`, `description`, `brand`, `status`, `is_visible`, `is_featured`, `base_price`.

### product_images

- Purpose: product media assets.
- Primary key: `id`.
- Foreign keys: `product_id -> products.id` with cascade delete.
- Indexes: `product_id`.
- Important columns: `url`, `alt_text`, `sort_order`, `is_primary`.

### product_variants

- Purpose: product variants such as size/color/SKU.
- Primary key: `id`.
- Foreign keys: `product_id -> products.id` with cascade delete.
- Unique/indexes: unique indexed `sku`; indexed `product_id`.
- Important columns: `name`, `price_delta`, `attributes`, `is_active`.

### warehouses

- Purpose: seller fulfillment locations.
- Primary key: `id`.
- Foreign keys: `seller_id -> seller_profiles.id` with cascade delete.
- Unique/indexes: unique indexed `code`; indexed `seller_id`.
- Important columns: `name`, `city`, `state`, `country`, `is_active`.

### inventory_items

- Purpose: stock records per product/variant/warehouse.
- Primary key: `id`.
- Foreign keys: `product_id -> products.id`, `variant_id -> product_variants.id`, `warehouse_id -> warehouses.id`.
- Unique constraints: `uq_inventory_product_variant_warehouse`.
- Indexes: `product_id`, `variant_id`, `warehouse_id`.
- Important columns: `quantity`, `reserved_quantity`, `reorder_level`.

### wishlist_items

- Purpose: saved products per customer.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id`, `product_id -> products.id`, `variant_id -> product_variants.id`.
- Unique constraints: `uq_wishlist_user_product`.
- Indexes: `user_id`, `product_id`, `variant_id`.

### cart_items

- Purpose: cart products per customer.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id`, `product_id -> products.id`, `variant_id -> product_variants.id`.
- Unique constraints: `uq_cart_user_product`.
- Indexes: `user_id`, `product_id`, `variant_id`.
- Important columns: `quantity`.

### coupons

- Purpose: checkout discount codes.
- Primary key: `id`.
- Unique/indexes: unique indexed `code`.
- Important columns: `discount_type`, `discount_value`, `is_active`.

### orders

- Purpose: customer order header and financial summary.
- Primary key: `id`.
- Foreign keys: `user_id -> users.id`, `shipping_address_id -> addresses.id`.
- Unique/indexes: unique indexed `order_number`; indexed `user_id`.
- Important columns: `billing_address`, `status`, `subtotal`, `tax_amount`, `shipping_charge`, `discount_amount`, `total_amount`, `coupon_code`, `payment_method`, `payment_status`, `shipment_status`, `tracking_number`.

### order_items

- Purpose: immutable line items captured at checkout.
- Primary key: `id`.
- Foreign keys: `order_id -> orders.id`, `product_id -> products.id`, `variant_id -> product_variants.id`, `seller_id -> seller_profiles.id`.
- Indexes: `order_id`.
- Important columns: `product_name`, `variant_name`, `sku`, `unit_price`, `quantity`, `line_total`.

### product_reviews

- Purpose: customer product reviews and moderation state.
- Primary key: `id`.
- Foreign keys: `product_id -> products.id`, `user_id -> users.id`.
- Indexes: `product_id`, `user_id`.
- Important columns: `rating`, `title`, `body`, `status`, `report_reason`.

### notifications

- Purpose: persisted notifications for customer, seller, admin, and payment events.
- Primary key: `id`.
- Foreign keys: optional `user_id -> users.id`.
- Indexes: `user_id`.
- Important columns: `type`, `title`, `message`, `is_read`.

### payment_transactions

- Purpose: sandbox payment transaction records.
- Primary key: `id`.
- Foreign keys: `order_id -> orders.id`.
- Unique/indexes: unique `provider_reference`; indexed `order_id`.
- Important columns: `provider`, `amount`, `currency`, `status`, `raw_response`.

### shipments

- Purpose: shipment labels/tracking records.
- Primary key: `id`.
- Foreign keys: `order_id -> orders.id`.
- Indexes: `order_id`.
- Important columns: `provider`, `label_url`, `tracking_number`, `status`.

### audit_logs

- Purpose: administrative action audit trail.
- Primary key: `id`.
- Foreign keys: optional `actor_user_id -> users.id`.
- Indexes: `actor_user_id`.
- Important columns: `action`, `entity_type`, `entity_id`, `metadata_json`.

## Enumerations

- `user_role`: `customer`, `admin`.
- `product_status`: `draft`, `active`, `inactive`, `archived`, `rejected`.
- `order_status`: `pending`, `confirmed`, `packed`, `shipped`, `delivered`, `cancelled`, `refunded`.
- `seller_moderation_status`: `pending`, `approved`, `rejected`, `suspended`.
- `review_status`: `pending`, `approved`, `reported`, `deleted`.
- `notification_type`: `order`, `seller`, `admin`, `payment`.
- `payment_status`: `pending`, `succeeded`, `failed`, `refunded`.
- `shipment_status`: `pending`, `label_created`, `in_transit`, `delivered`, `failed`.
- `discount_type`: `percent`, `fixed`.

## Primary Keys

All application tables use string UUID-style `id` primary keys except enum types, which are database enum definitions.

## Foreign Keys

Foreign keys enforce:

- User ownership of profiles, addresses, tokens, carts, wishlists, orders, reviews, notifications, seller profiles, and audit logs.
- Seller ownership of products and warehouses.
- Category membership for products.
- Product membership for images, variants, inventory, cart, wishlist, order items, and reviews.
- Order ownership of order items, payments, and shipments.

## Indexes and Unique Constraints

- `users.email`: unique index.
- `refresh_tokens.token_hash`: unique index.
- `categories.slug`: unique index.
- `seller_profiles.user_id`: unique index.
- `seller_profiles.slug`: unique index.
- `products.slug`: unique index.
- `product_variants.sku`: unique index.
- `warehouses.code`: unique index.
- `inventory_items(product_id, variant_id, warehouse_id)`: unique constraint.
- `wishlist_items(user_id, product_id, variant_id)`: unique constraint.
- `cart_items(user_id, product_id, variant_id)`: unique constraint.
- `coupons.code`: unique index.
- `orders.order_number`: unique index.
- `payment_transactions.provider_reference`: unique.

## Data Integrity Rules

- Deleting a user cascades profile, addresses, refresh tokens, cart, wishlist, notifications, and seller profile where configured.
- Product deletion cascades images, variants, inventory, wishlist, and cart records.
- Orders preserve historical product and seller values through order item snapshot fields.
- Inventory reserved quantity must not exceed quantity at schema/service validation.
- Order totals are calculated by service logic and persisted as order header values.
