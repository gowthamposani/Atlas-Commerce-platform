import { api } from "./api";
import {
  Address,
  CartSummary,
  Category,
  CheckoutPayload,
  CustomerDashboard,
  InventoryItem,
  Order,
  ProductDetail,
  ProductPage,
  ProductPayload,
  ProductListItem,
  Seller,
  SellerDashboard,
  Warehouse,
  WishlistItem,
} from "../types/api";

export interface ProductSearchParams {
  search?: string;
  category_id?: string;
  seller_id?: string;
  min_price?: string;
  max_price?: string;
  page?: number;
  page_size?: number;
}

export const catalogApi = {
  async categories(): Promise<Category[]> {
    const response = await api.get<Category[]>("/catalog/categories");
    return response.data;
  },
  async createCategory(payload: { name: string; description?: string }): Promise<Category> {
    const response = await api.post<Category>("/catalog/categories", payload);
    return response.data;
  },
  async products(params: ProductSearchParams = {}): Promise<ProductPage> {
    const response = await api.get<ProductPage>("/catalog/products", { params });
    return response.data;
  },
  async product(productId: string): Promise<ProductDetail> {
    const response = await api.get<ProductDetail>(`/catalog/products/${productId}`);
    return response.data;
  },
};

export const sellerApi = {
  async register(payload: { store_name: string; description?: string }): Promise<Seller> {
    const response = await api.post<Seller>("/seller/profile", payload);
    return response.data;
  },
  async profile(): Promise<Seller> {
    const response = await api.get<Seller>("/seller/profile");
    return response.data;
  },
  async dashboard(): Promise<SellerDashboard> {
    const response = await api.get<SellerDashboard>("/seller/dashboard");
    return response.data;
  },
  async store(sellerId: string): Promise<Seller> {
    const response = await api.get<Seller>(`/seller/stores/${sellerId}`);
    return response.data;
  },
  async products(): Promise<ProductListItem[]> {
    const response = await api.get<ProductListItem[]>("/seller/products");
    return response.data;
  },
  async createProduct(payload: ProductPayload): Promise<ProductDetail> {
    const response = await api.post<ProductDetail>("/seller/products", payload);
    return response.data;
  },
};

export const inventoryApi = {
  async warehouses(): Promise<Warehouse[]> {
    const response = await api.get<Warehouse[]>("/inventory/warehouses");
    return response.data;
  },
  async createWarehouse(payload: {
    name: string;
    code: string;
    city: string;
    state: string;
    country: string;
  }): Promise<Warehouse> {
    const response = await api.post<Warehouse>("/inventory/warehouses", payload);
    return response.data;
  },
  async stock(): Promise<InventoryItem[]> {
    const response = await api.get<InventoryItem[]>("/inventory/stock");
    return response.data;
  },
  async upsertStock(payload: {
    product_id: string;
    variant_id?: string;
    warehouse_id: string;
    quantity: number;
    reserved_quantity?: number;
    reorder_level?: number;
  }): Promise<InventoryItem> {
    const response = await api.post<InventoryItem>("/inventory/stock", payload);
    return response.data;
  },
};

export const wishlistApi = {
  async list(): Promise<WishlistItem[]> {
    const response = await api.get<WishlistItem[]>("/wishlist");
    return response.data;
  },
  async add(productId: string, variantId?: string): Promise<WishlistItem> {
    const response = await api.post<WishlistItem>("/wishlist", {
      product_id: productId,
      variant_id: variantId,
    });
    return response.data;
  },
  async remove(itemId: string): Promise<void> {
    await api.delete(`/wishlist/${itemId}`);
  },
  async moveToCart(itemId: string): Promise<CartSummary> {
    const response = await api.post<CartSummary>(`/wishlist/${itemId}/move-to-cart`);
    return response.data;
  },
};

export const cartApi = {
  async summary(): Promise<CartSummary> {
    const response = await api.get<CartSummary>("/cart");
    return response.data;
  },
  async add(productId: string, quantity = 1, variantId?: string): Promise<CartSummary> {
    const response = await api.post<CartSummary>("/cart/items", {
      product_id: productId,
      variant_id: variantId,
      quantity,
    });
    return response.data;
  },
  async update(itemId: string, quantity: number): Promise<CartSummary> {
    const response = await api.put<CartSummary>(`/cart/items/${itemId}`, { quantity });
    return response.data;
  },
  async remove(itemId: string): Promise<CartSummary> {
    const response = await api.delete<CartSummary>(`/cart/items/${itemId}`);
    return response.data;
  },
};

export const customerApi = {
  async dashboard(): Promise<CustomerDashboard> {
    const response = await api.get<CustomerDashboard>("/customer/dashboard");
    return response.data;
  },
  async addresses(): Promise<Address[]> {
    const response = await api.get<Address[]>("/customer/addresses");
    return response.data;
  },
};

export const orderApi = {
  async create(payload: CheckoutPayload): Promise<Order> {
    const response = await api.post<Order>("/orders", payload);
    return response.data;
  },
  async list(): Promise<Order[]> {
    const response = await api.get<Order[]>("/orders");
    return response.data;
  },
  async detail(orderId: string): Promise<Order> {
    const response = await api.get<Order>(`/orders/${orderId}`);
    return response.data;
  },
  async cancel(orderId: string): Promise<Order> {
    const response = await api.post<Order>(`/orders/${orderId}/cancel`);
    return response.data;
  },
};
