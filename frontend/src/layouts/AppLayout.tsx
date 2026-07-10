import { Heart, LogOut, Package, ShoppingBag, ShoppingCart, Store, UserRound } from "lucide-react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function AppLayout() {
  const auth = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await auth.logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#f7f8fb] text-slate-900">
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex min-h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="inline-flex items-center gap-2 font-semibold text-slate-950">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-teal-700 text-white">
              <ShoppingBag size={19} aria-hidden="true" />
            </span>
            <span>Atlas Commerce</span>
          </Link>

          <nav className="flex items-center gap-2">
            {auth.isAuthenticated ? (
              <>
                <NavLink
                  to="/categories"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Categories
                </NavLink>
                <NavLink
                  to="/products"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Products
                </NavLink>
                <NavLink
                  to="/dashboard"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Dashboard
                </NavLink>
                <NavLink
                  to="/profile"
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  <UserRound size={16} aria-hidden="true" />
                  Profile
                </NavLink>
                <NavLink
                  to="/wishlist"
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  <Heart size={16} aria-hidden="true" />
                  Wishlist
                </NavLink>
                <NavLink
                  to="/cart"
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  <ShoppingCart size={16} aria-hidden="true" />
                  Cart
                </NavLink>
                <NavLink
                  to="/orders"
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  <Package size={16} aria-hidden="true" />
                  Orders
                </NavLink>
                <NavLink
                  to="/seller"
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  <Store size={16} aria-hidden="true" />
                  Seller
                </NavLink>
                <button type="button" className="secondary-button" onClick={handleLogout}>
                  <LogOut size={16} aria-hidden="true" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink
                  to="/categories"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Categories
                </NavLink>
                <NavLink
                  to="/products"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Products
                </NavLink>
                <NavLink
                  to="/login"
                  className={({ isActive }) =>
                    `rounded-md px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100"
                    }`
                  }
                >
                  Login
                </NavLink>
                <Link to="/register" className="primary-button">
                  Create account
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
