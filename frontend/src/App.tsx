import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./layouts/AppLayout";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { CartPage } from "./pages/customer/CartPage";
import { DashboardPage } from "./pages/customer/DashboardPage";
import { CheckoutPage } from "./pages/customer/CheckoutPage";
import { OrderConfirmationPage } from "./pages/customer/OrderConfirmationPage";
import { OrderDetailsPage } from "./pages/customer/OrderDetailsPage";
import { OrdersPage } from "./pages/customer/OrdersPage";
import { ProfilePage } from "./pages/customer/ProfilePage";
import { WishlistPage } from "./pages/customer/WishlistPage";
import { SellerDashboardPage } from "./pages/seller/SellerDashboardPage";
import { CategoryListingPage } from "./pages/shared/CategoryListingPage";
import { LandingPage } from "./pages/shared/LandingPage";
import { ProductDetailsPage } from "./pages/shared/ProductDetailsPage";
import { ProductListingPage } from "./pages/shared/ProductListingPage";
import { SellerStorePage } from "./pages/shared/SellerStorePage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="/categories" element={<CategoryListingPage />} />
        <Route path="/products" element={<ProductListingPage />} />
        <Route path="/products/:productId" element={<ProductDetailsPage />} />
        <Route path="/stores/:sellerId" element={<SellerStorePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/wishlist" element={<WishlistPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/:orderId" element={<OrderDetailsPage />} />
          <Route path="/orders/:orderId/confirmation" element={<OrderConfirmationPage />} />
          <Route path="/seller" element={<SellerDashboardPage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
