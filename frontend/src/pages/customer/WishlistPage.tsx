import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ShoppingCart, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { wishlistApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function WishlistPage() {
  const queryClient = useQueryClient();
  const wishlistQuery = useQuery({ queryKey: ["wishlist"], queryFn: wishlistApi.list });
  const moveMutation = useMutation({
    mutationFn: wishlistApi.moveToCart,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wishlist"] });
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });
  const removeMutation = useMutation({
    mutationFn: wishlistApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wishlist"] }),
  });

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-950">Wishlist</h1>
      <div className="mt-6 grid gap-3">
        {wishlistQuery.data?.map((item) => (
          <article key={item.id} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <Link to={`/products/${item.product_id}`} className="font-semibold text-slate-950 hover:text-teal-700">
                  {item.product.name}
                </Link>
                <p className="mt-1 text-sm text-slate-600">{money(item.product.base_price)}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="primary-button" onClick={() => moveMutation.mutate(item.id)}>
                  <ShoppingCart size={15} aria-hidden="true" />
                  Move to cart
                </button>
                <button type="button" className="danger-button" onClick={() => removeMutation.mutate(item.id)}>
                  <Trash2 size={15} aria-hidden="true" />
                  Remove
                </button>
              </div>
            </div>
          </article>
        ))}
        {!wishlistQuery.data?.length && <p className="text-sm text-slate-600">Your wishlist is empty.</p>}
      </div>
    </section>
  );
}
