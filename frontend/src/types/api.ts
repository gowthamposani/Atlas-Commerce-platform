export type UserRole = "customer" | "admin";
export type ProductStatus = "draft" | "active" | "inactive" | "archived" | "rejected";
export type OrderStatus =
  | "pending"
  | "confirmed"
  | "packed"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded";
export type SellerModerationStatus = "pending" | "approved" | "rejected" | "suspended";
export type ReviewStatus = "pending" | "approved" | "reported" | "deleted";
export type PaymentStatus = "pending" | "succeeded" | "failed" | "refunded";
export type ShipmentStatus =
  | "pending"
  | "label_created"
  | "in_transit"
  | "delivered"
  | "failed";

export interface CustomerProfile {
  id: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  profile: CustomerProfile;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  user: CurrentUser;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ProfileUpdatePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
}

export interface Address {
  id: string;
  label: string;
  recipient_name: string;
  line1: string;
  line2: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string | null;
  is_default_shipping: boolean;
  created_at: string;
  updated_at: string;
}

export interface AddressPayload {
  label: string;
  recipient_name: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
  is_default_shipping: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Seller {
  id: string;
  user_id: string;
  store_name: string;
  slug: string;
  description: string | null;
  moderation_status: SellerModerationStatus;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductImage {
  id: string;
  url: string;
  alt_text: string | null;
  sort_order: number;
  is_primary: boolean;
}

export interface ProductVariant {
  id: string;
  sku: string;
  name: string;
  price_delta: number;
  attributes: Record<string, string>;
  is_active: boolean;
}

export interface ProductListItem {
  id: string;
  seller_id: string;
  category_id: string;
  name: string;
  slug: string;
  description: string;
  brand: string | null;
  status: ProductStatus;
  is_visible: boolean;
  is_featured: boolean;
  base_price: number;
  created_at: string;
  updated_at: string;
  category: Category;
  seller: Seller;
  images: ProductImage[];
}

export interface ProductDetail extends ProductListItem {
  variants: ProductVariant[];
  available_quantity: number;
}

export interface ProductPage {
  items: ProductListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProductPayload {
  category_id: string;
  name: string;
  description: string;
  base_price: number;
  status: ProductStatus;
  images: Array<{
    url: string;
    alt_text?: string;
    sort_order?: number;
    is_primary?: boolean;
  }>;
  variants: Array<{
    sku: string;
    name: string;
    price_delta: number;
    attributes: Record<string, string>;
    is_active: boolean;
  }>;
}

export interface SellerDashboard {
  seller: Seller;
  product_count: number;
  active_product_count: number;
  total_stock: number;
  order_count: number;
}

export interface Warehouse {
  id: string;
  seller_id: string;
  name: string;
  code: string;
  city: string;
  state: string;
  country: string;
  is_active: boolean;
  created_at: string;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  variant_id: string | null;
  warehouse_id: string;
  quantity: number;
  reserved_quantity: number;
  reorder_level: number;
  updated_at: string;
}

export interface WishlistItem {
  id: string;
  product_id: string;
  variant_id: string | null;
  created_at: string;
  product: ProductListItem;
}

export interface CartItem {
  id: string;
  product_id: string;
  variant_id: string | null;
  quantity: number;
  unit_price: number;
  line_total: number;
  product: ProductListItem;
  variant: ProductVariant | null;
}

export interface CartSummary {
  items: CartItem[];
  subtotal: number;
  item_count: number;
  is_inventory_valid: boolean;
}

export interface CheckoutPayload {
  shipping_address_id: string;
  billing_address: {
    recipient_name: string;
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  };
  coupon_code?: string;
  payment_method: string;
}

export interface OrderItem {
  id: string;
  product_id: string;
  variant_id: string | null;
  seller_id: string;
  product_name: string;
  variant_name: string | null;
  sku: string | null;
  unit_price: number;
  quantity: number;
  line_total: number;
}

export interface Order {
  id: string;
  order_number: string;
  user_id: string;
  shipping_address_id: string;
  billing_address: Record<string, string | null>;
  status: OrderStatus;
  subtotal: number;
  tax_amount: number;
  shipping_charge: number;
  discount_amount: number;
  total_amount: number;
  coupon_code: string | null;
  payment_method: string;
  payment_status: string;
  shipment_status: string;
  tracking_number: string | null;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface AdminStats {
  total_customers: number;
  total_sellers: number;
  total_products: number;
  total_orders: number;
  revenue_summary: number;
  pending_orders: number;
  pending_seller_approvals: number;
}

export interface AdminDashboard {
  stats: AdminStats;
  recent_orders: Order[];
  pending_sellers: number;
  pending_products: number;
}

export interface AdminUser {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  rating: number;
  title: string | null;
  body: string;
  status: ReviewStatus;
  report_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface Report {
  name: string;
  generated_at: string;
  rows: Array<Record<string, string | number | null>>;
}

export interface NotificationItem {
  id: string;
  user_id: string | null;
  type: "order" | "seller" | "admin" | "payment";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface PaymentTransaction {
  id: string;
  order_id: string;
  provider: string;
  provider_reference: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  raw_response: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface Shipment {
  id: string;
  order_id: string;
  provider: string;
  label_url: string | null;
  tracking_number: string | null;
  status: ShipmentStatus;
  created_at: string;
  updated_at: string;
}
