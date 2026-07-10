import { ArrowRight, Search, Store } from "lucide-react";
import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { ProductCard } from "../../components/ProductCard";
import { catalogApi } from "../../services/marketplace";

export function LandingPage() {
  const [search, setSearch] = useState("");
  const categoriesQuery = useQuery({ queryKey: ["categories"], queryFn: catalogApi.categories });
  const productsQuery = useQuery({
    queryKey: ["products", "home"],
    queryFn: () => catalogApi.products({ page_size: 6 }),
  });

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    window.location.href = `/products?search=${encodeURIComponent(search)}`;
  };

  return (
    <div>
      <section className="bg-white">
        <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
              Marketplace
            </p>
            <h1 className="mt-4 max-w-2xl text-4xl font-bold leading-tight text-slate-950 sm:text-5xl">
              Atlas Commerce Platform
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-600">
              Browse categories, find products, save wishlist picks, and check out with
              inventory-backed cart validation.
            </p>
            <form onSubmit={handleSearch} className="mt-8 flex max-w-xl gap-2">
              <input
                className="field"
                placeholder="Search products"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <button type="submit" className="primary-button">
                <Search size={17} aria-hidden="true" />
                Search
              </button>
            </form>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link to="/products" className="primary-button">
                Browse products
                <ArrowRight size={17} aria-hidden="true" />
              </Link>
              <Link to="/seller" className="secondary-button">
                <Store size={17} aria-hidden="true" />
                Seller tools
              </Link>
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-[#fbfcfd] p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <div>
                <p className="text-sm font-semibold text-slate-950">Live catalog</p>
                <p className="mt-1 text-sm text-slate-500">Loaded from FastAPI</p>
              </div>
              <span className="rounded-md bg-teal-100 px-2.5 py-1 text-xs font-semibold text-teal-800">
                {productsQuery.data?.total ?? 0} products
              </span>
            </div>
            <div className="mt-5 grid gap-3">
              {categoriesQuery.data?.slice(0, 5).map((category) => (
                <Link
                  key={category.id}
                  to={`/products?category_id=${category.id}`}
                  className="rounded-md border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-900 hover:border-teal-300"
                >
                  {category.name}
                </Link>
              ))}
              {!categoriesQuery.data?.length && (
                <p className="rounded-md border border-slate-200 bg-white p-4 text-sm text-slate-600">
                  No categories yet.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-200 bg-[#eef6f5]">
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="mb-5 flex items-center justify-between gap-3">
            <h2 className="text-xl font-bold text-slate-950">Featured products</h2>
            <Link to="/products" className="text-sm font-semibold text-teal-700">
              View all
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {productsQuery.data?.items.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
            {!productsQuery.data?.items.length && (
              <p className="rounded-md border border-teal-100 bg-white p-4 text-sm text-slate-600">
                No products have been published yet.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
