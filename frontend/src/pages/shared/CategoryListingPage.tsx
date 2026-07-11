import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { catalogApi } from "../../services/marketplace";

export function CategoryListingPage() {
  const categoriesQuery = useQuery({ queryKey: ["categories"], queryFn: catalogApi.categories });

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-950">Categories</h1>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categoriesQuery.data?.map((category) => (
          <Link
            key={category.id}
            to={`/products?category_id=${category.id}`}
            className="rounded-md border border-slate-200 bg-white p-5 shadow-sm hover:border-teal-300"
          >
            <h2 className="text-lg font-semibold text-slate-950">{category.name}</h2>
            <p className="mt-2 text-sm text-slate-600">{category.description ?? "Browse products"}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
