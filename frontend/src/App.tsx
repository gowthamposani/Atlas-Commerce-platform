import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./layouts/AppLayout";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { DashboardPage } from "./pages/customer/DashboardPage";
import { ProfilePage } from "./pages/customer/ProfilePage";
import { LandingPage } from "./pages/shared/LandingPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
