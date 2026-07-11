import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { orderApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function OrderDetailsPage() {
  const { orderId } = useParams();
  const queryClient = useQueryClient();
  const orderQuery = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => orderApi.detail(orderId ?? ""),
    enabled: Boolean(orderId),
  });
  const cancelMutation = useMutation({
    mutationFn: () => orderApi.cancel(orderId ?? ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
  });
  const order = orderQuery.data;

  if (!order) {
    return <div className="mx-auto max-w-6xl px-4 py-10 text-sm text-slate-600">Loading order...</div>;
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <Link to="/orders" className="text-sm font-semibold text-teal-700">Back to orders</Link>
      <div className="mt-4 rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">{order.order_number}</h1>
            <p className="mt-2 text-sm text-slate-600">Status: {order.status}</p>
          </div>
          <p className="text-2xl font-bold text-slate-950">{money(order.total_amount)}</p>
        </div>
        <div className="mt-6 grid gap-3">
          {order.items.map((item) => (
            <div key={item.id} className="flex justify-between rounded-md border border-slate-200 p-3 text-sm">
              <span>{item.product_name} x {item.quantity}</span>
              <span className="font-semibold">{money(item.line_total)}</span>
            </div>
          ))}
        </div>
        {(order.status === "pending" || order.status === "confirmed") && (
          <button type="button" className="danger-button mt-6" onClick={() => cancelMutation.mutate()}>
            Cancel order
          </button>
        )}
      </div>
    </section>
  );
}
