import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ProductCard } from "../../components/ProductCard";
import { catalogApi, sellerApi } from "../../services/marketplace";

export function SellerStorePage() {
  const { sellerId } = useParams();
  const sellerQuery = useQuery({
    queryKey: ["seller-store", sellerId],
    queryFn: () => sellerApi.store(sellerId ?? ""),
    enabled: Boolean(sellerId),
  });
  const productsQuery = useQuery({
    queryKey: ["products", "seller", sellerId],
    queryFn: () => catalogApi.products({ seller_id: sellerId, page_size: 24 }),
    enabled: Boolean(sellerId),
  });

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Seller store</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">{sellerQuery.data?.store_name ?? "Store"}</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-600">{sellerQuery.data?.description ?? "Seller products"}</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {productsQuery.data?.items.map((product) => <ProductCard key={product.id} product={product} />)}
      </div>
    </section>
  );
}
