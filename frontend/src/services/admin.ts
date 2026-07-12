import { api } from "./api";
import {
  AdminDashboard,
  AdminUser,
  NotificationItem,
  Order,
  PaymentStatus,
  PaymentTransaction,
  ProductListItem,
  ProductStatus,
  RecommendationResponse,
  Report,
  Review,
  ReviewStatus,
  Seller,
  SellerModerationStatus,
  Shipment,
  ShipmentStatus,
} from "../types/api";

export async function getAdminDashboard() {
  const response = await api.get<AdminDashboard>("/admin/dashboard");
  return response.data;
}

export async function getAdminUsers(search?: string) {
  const response = await api.get<AdminUser[]>("/admin/users", { params: { search } });
  return response.data;
}

export async function setUserActive(userId: string, isActive: boolean) {
  const response = await api.patch<AdminUser>(`/admin/users/${userId}`, { is_active: isActive });
  return response.data;
}

export async function getAdminSellers() {
  const response = await api.get<Seller[]>("/admin/sellers");
  return response.data;
}

export async function moderateSeller(sellerId: string, status: SellerModerationStatus) {
  const response = await api.patch<Seller>(`/admin/sellers/${sellerId}`, { status });
  return response.data;
}

export async function getAdminProducts(statusFilter?: ProductStatus) {
  const response = await api.get<ProductListItem[]>("/admin/products", {
    params: { status_filter: statusFilter },
  });
  return response.data;
}

export async function moderateProduct(
  productId: string,
  payload: Partial<{
    status: ProductStatus;
    is_visible: boolean;
    is_featured: boolean;
    brand: string;
  }>,
) {
  const response = await api.patch<ProductListItem>(`/admin/products/${productId}`, payload);
  return response.data;
}

export async function getAdminOrders() {
  const response = await api.get<Order[]>("/admin/orders");
  return response.data;
}

export async function setOrderStatus(orderId: string, status: string) {
  const response = await api.patch<Order>(`/admin/orders/${orderId}/status`, { status });
  return response.data;
}

export async function refundOrder(orderId: string) {
  const response = await api.post<Order>(`/admin/orders/${orderId}/refund`);
  return response.data;
}

export async function createShipment(orderId: string, trackingNumber: string) {
  const response = await api.post<Shipment>(`/admin/orders/${orderId}/shipments`, {
    provider: "manual",
    tracking_number: trackingNumber,
    status: "label_created" satisfies ShipmentStatus,
  });
  return response.data;
}

export async function getAdminReviews() {
  const response = await api.get<Review[]>("/admin/reviews");
  return response.data;
}

export async function moderateReview(reviewId: string, status: ReviewStatus) {
  const response = await api.patch<Review>(`/admin/reviews/${reviewId}`, { status });
  return response.data;
}

export async function getReport(name: string) {
  const response = await api.get<Report>(`/admin/reports/${name}`);
  return response.data;
}

export async function getReportCsv(name: string) {
  const response = await api.get<string>(`/admin/reports/${name}.csv`, {
    responseType: "text",
  });
  return response.data;
}

export async function getNotifications() {
  const response = await api.get<NotificationItem[]>("/admin/notifications");
  return response.data;
}

export async function createNotification(title: string, message: string) {
  const response = await api.post<NotificationItem>("/admin/notifications", {
    title,
    message,
    type: "admin",
  });
  return response.data;
}

export async function getPayments() {
  const response = await api.get<PaymentTransaction[]>("/admin/payments");
  return response.data;
}

export async function setPaymentStatus(paymentId: string, status: PaymentStatus) {
  const response = await api.patch<PaymentTransaction>(`/admin/payments/${paymentId}`, { status });
  return response.data;
}

export async function createPaymentIntent(orderId: string) {
  const response = await api.post<PaymentTransaction>("/admin/payments/stripe-sandbox", {
    order_id: orderId,
  });
  return response.data;
}

export async function getProductDescription(productId: string) {
  const response = await api.post<{ product_id: string; description: string }>(
    `/admin/ai/products/${productId}/description`,
  );
  return response.data;
}

export async function getProductRecommendations(productId: string) {
  const response = await api.get<RecommendationResponse>(
    `/admin/ai/products/${productId}/recommendations`,
  );
  return response.data;
}
