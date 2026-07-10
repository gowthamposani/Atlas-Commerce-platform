import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Heart, ShoppingCart, Store } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { cartApi, catalogApi, wishlistApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function ProductDetailsPage() {
  const { productId } = useParams();
  const auth = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const productQuery = useQuery({
    queryKey: ["product", productId],
    queryFn: () => catalogApi.product(productId ?? ""),
    enabled: Boolean(productId),
  });

  const wishlistMutation = useMutation({
    mutationFn: () => wishlistApi.add(productId ?? ""),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wishlist"] }),
  });
  const cartMutation = useMutation({
    mutationFn: () => cartApi.add(productId ?? ""),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
  });

  const requireAuth = (action: () => void) => {
    if (!auth.isAuthenticated) {
      navigate("/login");
      return;
    }
    action();
  };

  const product = productQuery.data;
  const primaryImage = product?.images.find((image) => image.is_primary) ?? product?.images[0];

  if (productQuery.isLoading) {
    return <div className="mx-auto max-w-6xl px-4 py-10 text-sm text-slate-600">Loading product...</div>;
  }

  if (!product) {
    return <div className="mx-auto max-w-6xl px-4 py-10 text-sm text-slate-600">Product not found.</div>;
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
      <div>
        {primaryImage ? (
          <img
            src={primaryImage.url}
            alt={primaryImage.alt_text ?? product.name}
            className="aspect-[4/3] w-full rounded-md border border-slate-200 object-cover"
          />
        ) : (
          <div className="flex aspect-[4/3] items-center justify-center rounded-md border border-slate-200 bg-slate-100 text-slate-500">
            Product image
          </div>
        )}
      </div>
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">{product.category.name}</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">{product.name}</h1>
        <Link
          to={`/stores/${product.seller_id}`}
          className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700"
        >
          <Store size={16} aria-hidden="true" />
          {product.seller.store_name}
        </Link>
        <p className="mt-5 text-3xl font-bold text-slate-950">{money(product.base_price)}</p>
        <p className="mt-5 leading-7 text-slate-600">{product.description}</p>
        <p className="mt-4 text-sm font-medium text-slate-700">
          Available stock: {product.available_quantity}
        </p>

        {product.variants.length > 0 && (
          <div className="mt-5 grid gap-2">
            <p className="text-sm font-semibold text-slate-950">Variants</p>
            {product.variants.map((variant) => (
              <div key={variant.id} className="rounded-md border border-slate-200 bg-white p-3 text-sm text-slate-700">
                {variant.name} · SKU {variant.sku} · +{money(variant.price_delta)}
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 flex flex-wrap gap-3">
          <button type="button" className="secondary-button" onClick={() => requireAuth(() => wishlistMutation.mutate())}>
            <Heart size={16} aria-hidden="true" />
            Add to wishlist
          </button>
          <button type="button" className="primary-button" onClick={() => requireAuth(() => cartMutation.mutate())}>
            <ShoppingCart size={16} aria-hidden="true" />
            Add to cart
          </button>
        </div>
      </div>
    </section>
  );
}
