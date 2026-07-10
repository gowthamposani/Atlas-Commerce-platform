import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { orderApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function OrdersPage() {
  const ordersQuery = useQuery({ queryKey: ["orders"], queryFn: orderApi.list });

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-950">Order history</h1>
      <div className="mt-6 grid gap-3">
        {ordersQuery.data?.map((order) => (
          <Link key={order.id} to={`/orders/${order.id}`} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm hover:border-teal-300">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold text-slate-950">{order.order_number}</p>
                <p className="mt-1 text-sm text-slate-600">
                  {order.items.map((item) => item.product_name).join(", ")}
                </p>
                <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {order.items.length} item(s) · {order.status}
                </p>
              </div>
              <p className="text-lg font-bold text-slate-950">{money(order.total_amount)}</p>
            </div>
          </Link>
        ))}
        {!ordersQuery.data?.length && <p className="text-sm text-slate-600">No orders yet.</p>}
      </div>
    </section>
  );
}
