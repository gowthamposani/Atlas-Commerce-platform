import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { cartApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function CartPage() {
  const queryClient = useQueryClient();
  const cartQuery = useQuery({ queryKey: ["cart"], queryFn: cartApi.summary });
  const updateMutation = useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) => cartApi.update(itemId, quantity),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
  });
  const removeMutation = useMutation({
    mutationFn: cartApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
  });

  const cart = cartQuery.data;

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-950">Shopping cart</h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="grid gap-3">
          {cart?.items.map((item) => (
            <article key={item.id} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <Link to={`/products/${item.product_id}`} className="font-semibold text-slate-950 hover:text-teal-700">
                    {item.product.name}
                  </Link>
                  <p className="mt-1 text-sm text-slate-600">
                    {money(item.unit_price)} each · {money(item.line_total)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    className="field w-24"
                    type="number"
                    min={1}
                    step={1}
                    value={item.quantity}
                    onChange={(event) => {
                      const quantity = Number(event.target.value);
                      if (!Number.isInteger(quantity) || quantity < 1 || updateMutation.isPending) {
                        return;
                      }
                      updateMutation.mutate({ itemId: item.id, quantity });
                    }}
                  />
                  <button type="button" className="danger-button" onClick={() => removeMutation.mutate(item.id)}>
                    <Trash2 size={15} aria-hidden="true" />
                    Remove
                  </button>
                </div>
              </div>
            </article>
          ))}
          {!cart?.items.length && <p className="text-sm text-slate-600">Your cart is empty.</p>}
        </div>
        <aside className="h-fit rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Cart summary</h2>
          <div className="mt-4 flex justify-between text-sm">
            <span>Items</span>
            <span>{cart?.item_count ?? 0}</span>
          </div>
          <div className="mt-2 flex justify-between text-base font-bold">
            <span>Subtotal</span>
            <span>{money(cart?.subtotal ?? 0)}</span>
          </div>
          <Link to="/checkout" className="primary-button mt-5 w-full">
            Checkout
          </Link>
        </aside>
      </div>
    </section>
  );
}
