import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useSearchParams } from "react-router-dom";

import { ProductCard } from "../../components/ProductCard";
import { useAuth } from "../../context/AuthContext";
import { cartApi, catalogApi, wishlistApi } from "../../services/marketplace";

export function ProductListingPage() {
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get("search") ?? "");
  const [categoryId, setCategoryId] = useState(params.get("category_id") ?? "");
  const [minPrice, setMinPrice] = useState(params.get("min_price") ?? "");
  const [maxPrice, setMaxPrice] = useState(params.get("max_price") ?? "");
  const auth = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const categoriesQuery = useQuery({ queryKey: ["categories"], queryFn: catalogApi.categories });
  const productsQuery = useQuery({
    queryKey: ["products", Object.fromEntries(params.entries())],
    queryFn: () =>
      catalogApi.products({
        search: params.get("search") ?? undefined,
        category_id: params.get("category_id") ?? undefined,
        min_price: params.get("min_price") ?? undefined,
        max_price: params.get("max_price") ?? undefined,
        page_size: 24,
      }),
  });

  const wishlistMutation = useMutation({
    mutationFn: (productId: string) => wishlistApi.add(productId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wishlist"] }),
  });
  const cartMutation = useMutation({
    mutationFn: (productId: string) => cartApi.add(productId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
  });

  const requireAuth = (action: () => void) => {
    if (!auth.isAuthenticated) {
      navigate("/login");
      return;
    }
    action();
  };

  const handleFilter = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const next = new URLSearchParams();
    if (search) next.set("search", search);
    if (categoryId) next.set("category_id", categoryId);
    if (minPrice) next.set("min_price", minPrice);
    if (maxPrice) next.set("max_price", maxPrice);
    setParams(next);
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Catalog</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">Product listing</h1>
      </div>

      <form onSubmit={handleFilter} className="mb-6 grid gap-3 rounded-md border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_180px_120px_120px_auto]">
        <input className="field" placeholder="Search products" value={search} onChange={(event) => setSearch(event.target.value)} />
        <select className="field" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
          <option value="">All categories</option>
          {categoriesQuery.data?.map((category) => (
            <option key={category.id} value={category.id}>{category.name}</option>
          ))}
        </select>
        <input className="field" placeholder="Min" value={minPrice} onChange={(event) => setMinPrice(event.target.value)} />
        <input className="field" placeholder="Max" value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} />
        <button type="submit" className="primary-button">Apply</button>
      </form>

      <div className="mb-4 text-sm text-slate-600">{productsQuery.data?.total ?? 0} products found</div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {productsQuery.data?.items.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onWishlist={(productId) => requireAuth(() => wishlistMutation.mutate(productId))}
            onCart={(productId) => requireAuth(() => cartMutation.mutate(productId))}
          />
        ))}
      </div>
    </section>
  );
}
