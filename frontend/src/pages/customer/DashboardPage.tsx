import { Link } from "react-router-dom";
import { Heart, MapPin, PackageCheck, ShoppingCart, UserRound } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { useAuth } from "../../context/AuthContext";
import { customerApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function DashboardPage() {
  const { user } = useAuth();
  const profile = user?.profile;
  const dashboardQuery = useQuery({
    queryKey: ["customer", "dashboard"],
    queryFn: customerApi.dashboard,
  });
  const dashboard = dashboardQuery.data;

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
            Dashboard
          </p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">
            Welcome{profile ? `, ${profile.first_name}` : ""}
          </h1>
        </div>
        <Link to="/profile" className="primary-button">
          <UserRound size={17} aria-hidden="true" />
          Profile
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <PackageCheck className="text-teal-700" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Total Orders</h2>
          <p className="mt-2 text-2xl font-bold text-slate-950">
            {dashboard?.total_orders ?? 0}
          </p>
        </section>
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <Heart className="text-rose-600" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Wishlist Items</h2>
          <p className="mt-2 text-2xl font-bold text-slate-950">
            {dashboard?.wishlist_items ?? 0}
          </p>
        </section>
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <ShoppingCart className="text-slate-700" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Cart Items</h2>
          <p className="mt-2 text-2xl font-bold text-slate-950">
            {dashboard?.cart_items ?? 0}
          </p>
        </section>
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <MapPin className="text-amber-600" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Shipping</h2>
          <p className="mt-2 text-sm text-slate-600">Manage saved addresses from Profile.</p>
        </section>
      </div>

      <section className="mt-8 rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">Recent Orders</h2>
            <p className="mt-1 text-sm text-slate-600">
              Latest purchases and fulfillment statuses from your account.
            </p>
          </div>
          <Link to="/orders" className="secondary-button">View all</Link>
        </div>
        <div className="mt-5 grid gap-3">
          {dashboard?.recent_orders.map((order) => (
            <Link
              className="rounded-md border border-slate-200 p-4 hover:border-teal-300"
              key={order.id}
              to={`/orders/${order.id}`}
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-950">{order.order_number}</p>
                  <p className="mt-1 text-sm text-slate-600">
                    {order.items.map((item) => item.product_name).join(", ")}
                  </p>
                </div>
                <div className="text-sm sm:text-right">
                  <p className="font-bold text-slate-950">{money(order.total_amount)}</p>
                  <p className="mt-1 rounded-full bg-slate-100 px-2 py-1 font-semibold uppercase text-slate-600">
                    {order.status}
                  </p>
                </div>
              </div>
            </Link>
          ))}
          {!dashboardQuery.isLoading && !dashboard?.recent_orders.length && (
            <div className="rounded-md border border-dashed border-slate-300 p-6 text-sm text-slate-600">
              No orders yet. Browse the catalog and place an order to see it here.
            </div>
          )}
        </div>
      </section>
    </section>
  );
}
