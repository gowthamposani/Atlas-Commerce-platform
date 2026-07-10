import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { orderApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function OrderConfirmationPage() {
  const { orderId } = useParams();
  const orderQuery = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => orderApi.detail(orderId ?? ""),
    enabled: Boolean(orderId),
  });
  const order = orderQuery.data;

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="rounded-md border border-emerald-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">Order confirmation</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">Order created</h1>
        {order && (
          <div className="mt-5 grid gap-2 text-sm text-slate-700">
            <p>Order number: <span className="font-semibold">{order.order_number}</span></p>
            <p>Status: <span className="font-semibold">{order.status}</span></p>
            <p>Total: <span className="font-semibold">{money(order.total_amount)}</span></p>
          </div>
        )}
        <div className="mt-6 flex gap-3">
          <Link to="/orders" className="primary-button">View order history</Link>
          <Link to="/products" className="secondary-button">Continue shopping</Link>
        </div>
      </div>
    </section>
  );
}
