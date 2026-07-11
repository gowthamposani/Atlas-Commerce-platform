import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, Heart, PackageCheck, ShoppingCart, Sparkles, Store } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ProductCard } from "../../components/ProductCard";
import { useAuth } from "../../context/AuthContext";
import { getProductDescription, getProductRecommendations } from "../../services/admin";
import { cartApi, catalogApi, wishlistApi } from "../../services/marketplace";
import { money } from "../../utils/money";

export function ProductDetailsPage() {
  const { productId } = useParams();
  const auth = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isAdmin = auth.user?.role === "admin";

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
  const recommendationsQuery = useQuery({
    queryKey: ["admin", "product", productId, "recommendations"],
    queryFn: () => getProductRecommendations(productId ?? ""),
    enabled: Boolean(productId) && isAdmin,
    retry: false,
  });
  const summaryMutation = useMutation({
    mutationFn: () => getProductDescription(productId ?? ""),
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
  const recommendations = recommendationsQuery.data?.recommendations ?? [];

  if (productQuery.isLoading) {
    return (
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-10 text-sm text-slate-600">
        <span className="loading-spinner" aria-hidden="true" />
        Loading product...
      </div>
    );
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="empty-state">Product not found.</div>
      </div>
    );
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
      <div className="grid gap-4">
        <div className="surface-card overflow-hidden p-0">
          {primaryImage ? (
            <img
              src={primaryImage.url}
              alt={primaryImage.alt_text ?? product.name}
              className="aspect-[4/3] w-full object-cover"
            />
          ) : (
            <div className="flex aspect-[4/3] items-center justify-center bg-slate-100 text-slate-500">
              Product image
            </div>
          )}
        </div>
        <div className="surface-card flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Availability
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-950">
              {product.available_quantity} units ready
            </p>
          </div>
          <span className={product.available_quantity > 0 ? "status-badge status-success" : "status-badge status-danger"}>
            {product.available_quantity > 0 ? "In stock" : "Out of stock"}
          </span>
        </div>
      </div>
      <div className="grid content-start gap-5">
        {wishlistMutation.isSuccess ? (
          <p className="toast-success">Product added to wishlist.</p>
        ) : null}
        {cartMutation.isSuccess ? <p className="toast-success">Product added to cart.</p> : null}
        {(wishlistMutation.isError || cartMutation.isError) ? (
          <p className="toast-error">Action failed. Please check your session and inventory.</p>
        ) : null}

        <div className="surface-card">
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
          <button
            type="button"
            className="secondary-button"
            disabled={wishlistMutation.isPending}
            onClick={() => requireAuth(() => wishlistMutation.mutate())}
          >
            <Heart size={16} aria-hidden="true" />
            {wishlistMutation.isPending ? "Saving..." : "Add to wishlist"}
          </button>
          <button
            type="button"
            className="primary-button"
            disabled={cartMutation.isPending || product.available_quantity < 1}
            onClick={() => requireAuth(() => cartMutation.mutate())}
          >
            <ShoppingCart size={16} aria-hidden="true" />
            {cartMutation.isPending ? "Adding..." : "Add to cart"}
          </button>
        </div>
        </div>

        {isAdmin ? (
          <div className="surface-card">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-950">
                  <Bot className="h-5 w-5 text-teal-700" />
                  AI Summary
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Generated by the existing Atlas admin AI endpoint.
                </p>
              </div>
              <button
                className="secondary-button"
                disabled={summaryMutation.isPending}
                onClick={() => summaryMutation.mutate()}
                type="button"
              >
                {summaryMutation.isPending ? (
                  <span className="loading-spinner" aria-hidden="true" />
                ) : (
                  <Sparkles className="h-4 w-4" aria-hidden="true" />
                )}
                {summaryMutation.isPending ? "Generating..." : "AI Summary"}
              </button>
            </div>
            {summaryMutation.data?.description ? (
              <p className="mt-4 rounded-md border border-teal-100 bg-teal-50 p-4 text-sm leading-6 text-slate-700">
                {summaryMutation.data.description}
              </p>
            ) : null}
            {summaryMutation.isError ? (
              <p className="toast-error mt-4">AI summary is unavailable for this product.</p>
            ) : null}
          </div>
        ) : null}

        {isAdmin ? (
          <div className="surface-card">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-950">
              <PackageCheck className="h-5 w-5 text-teal-700" />
              Recommended Products
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              Recommendations come from the existing admin recommendation API.
            </p>
            {recommendationsQuery.isLoading ? (
              <div className="mt-4 flex items-center gap-3 text-sm text-slate-600">
                <span className="loading-spinner" aria-hidden="true" />
                Loading recommendations...
              </div>
            ) : recommendations.length ? (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {recommendations.slice(0, 2).map((item) => (
                  <ProductCard key={item.id} product={item} />
                ))}
              </div>
            ) : (
              <div className="empty-state mt-4">
                No recommendations are available for this product yet.
              </div>
            )}
          </div>
        ) : null}
      </div>
    </section>
  );
}
