import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PackagePlus, Store } from "lucide-react";
import { Link } from "react-router-dom";

import { catalogApi, inventoryApi, sellerApi } from "../../services/marketplace";
import { ProductPayload } from "../../types/api";
import { money } from "../../utils/money";

export function SellerDashboardPage() {
  const queryClient = useQueryClient();
  const [storeName, setStoreName] = useState("");
  const [storeDescription, setStoreDescription] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [categoryDescription, setCategoryDescription] = useState("");
  const [warehouse, setWarehouse] = useState({
    name: "",
    code: "",
    city: "",
    state: "",
    country: "US",
  });
  const [product, setProduct] = useState({
    category_id: "",
    name: "",
    description: "",
    base_price: "",
    image_url: "",
    sku: "",
    variant_name: "",
    variant_price_delta: "0",
    warehouse_id: "",
    stock_quantity: "10",
  });

  const dashboardQuery = useQuery({
    queryKey: ["seller", "dashboard"],
    queryFn: sellerApi.dashboard,
    retry: false,
  });
  const categoriesQuery = useQuery({ queryKey: ["categories"], queryFn: catalogApi.categories });
  const warehousesQuery = useQuery({
    queryKey: ["seller", "warehouses"],
    queryFn: inventoryApi.warehouses,
    retry: false,
  });
  const productsQuery = useQuery({
    queryKey: ["seller", "products"],
    queryFn: sellerApi.products,
    retry: false,
  });

  const registerSellerMutation = useMutation({
    mutationFn: sellerApi.register,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["seller"] });
      setStoreName("");
      setStoreDescription("");
    },
  });

  const createCategoryMutation = useMutation({
    mutationFn: catalogApi.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      setCategoryName("");
      setCategoryDescription("");
    },
  });

  const createWarehouseMutation = useMutation({
    mutationFn: inventoryApi.createWarehouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["seller", "warehouses"] });
      setWarehouse({ name: "", code: "", city: "", state: "", country: "US" });
    },
  });

  const createProductMutation = useMutation({
    mutationFn: async () => {
      const variants: ProductPayload["variants"] =
        product.sku && product.variant_name
          ? [
              {
                sku: product.sku,
                name: product.variant_name,
                price_delta: Number(product.variant_price_delta) || 0,
                attributes: { option: product.variant_name },
                is_active: true,
              },
            ]
          : [];

      const created = await sellerApi.createProduct({
        category_id: product.category_id,
        name: product.name,
        description: product.description,
        base_price: Number(product.base_price),
        status: "active",
        images: product.image_url
          ? [{ url: product.image_url, alt_text: product.name, sort_order: 0, is_primary: true }]
          : [],
        variants,
      });

      if (product.warehouse_id) {
        await inventoryApi.upsertStock({
          product_id: created.id,
          variant_id: created.variants[0]?.id,
          warehouse_id: product.warehouse_id,
          quantity: Number(product.stock_quantity),
          reserved_quantity: 0,
          reorder_level: 1,
        });
      }
      return created;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["seller"] });
      queryClient.invalidateQueries({ queryKey: ["products"] });
      setProduct({
        category_id: "",
        name: "",
        description: "",
        base_price: "",
        image_url: "",
        sku: "",
        variant_name: "",
        variant_price_delta: "0",
        warehouse_id: "",
        stock_quantity: "10",
      });
    },
  });

  const handleSellerRegister = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    registerSellerMutation.mutate({
      store_name: storeName,
      description: storeDescription || undefined,
    });
  };

  const handleCategoryCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    createCategoryMutation.mutate({
      name: categoryName,
      description: categoryDescription || undefined,
    });
  };

  const handleWarehouseCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    createWarehouseMutation.mutate(warehouse);
  };

  const handleProductCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    createProductMutation.mutate();
  };

  if (dashboardQuery.isError) {
    return (
      <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-4xl items-center px-4 py-10 sm:px-6 lg:px-8">
        <form onSubmit={handleSellerRegister} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <Store className="text-teal-700" size={28} aria-hidden="true" />
          <h1 className="mt-4 text-3xl font-bold text-slate-950">Register as a seller</h1>
          <div className="mt-5 grid gap-4">
            <label className="grid gap-1">
              <span className="label">Store name</span>
              <input className="field" value={storeName} onChange={(event) => setStoreName(event.target.value)} required />
            </label>
            <label className="grid gap-1">
              <span className="label">Description</span>
              <textarea className="field min-h-24" value={storeDescription} onChange={(event) => setStoreDescription(event.target.value)} />
            </label>
          </div>
          <button type="submit" className="primary-button mt-6">Create seller profile</button>
        </form>
      </section>
    );
  }

  const dashboard = dashboardQuery.data;

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Seller dashboard</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">{dashboard?.seller.store_name}</h1>
        </div>
        {dashboard && <Link to={`/stores/${dashboard.seller.id}`} className="secondary-button">View store</Link>}
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        {[
          ["Products", dashboard?.product_count ?? 0],
          ["Active", dashboard?.active_product_count ?? 0],
          ["Stock", dashboard?.total_stock ?? 0],
          ["Orders", dashboard?.order_count ?? 0],
        ].map(([label, value]) => (
          <div key={label} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-bold text-slate-950">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={handleCategoryCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Create category</h2>
          <div className="mt-4 grid gap-3">
            <input className="field" placeholder="Category name" value={categoryName} onChange={(event) => setCategoryName(event.target.value)} required />
            <input className="field" placeholder="Description" value={categoryDescription} onChange={(event) => setCategoryDescription(event.target.value)} />
          </div>
          <button type="submit" className="primary-button mt-4">Save category</button>
        </form>

        <form onSubmit={handleWarehouseCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Create warehouse</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {(["name", "code", "city", "state", "country"] as const).map((field) => (
              <input
                key={field}
                className="field"
                placeholder={field.replace("_", " ")}
                value={warehouse[field]}
                onChange={(event) => setWarehouse((current) => ({ ...current, [field]: event.target.value }))}
                required
              />
            ))}
          </div>
          <button type="submit" className="primary-button mt-4">Save warehouse</button>
        </form>

        <form onSubmit={handleProductCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center gap-2">
            <PackagePlus size={20} className="text-teal-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-slate-950">Create product</h2>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <select className="field" value={product.category_id} onChange={(event) => setProduct((current) => ({ ...current, category_id: event.target.value }))} required>
              <option value="">Select category</option>
              {categoriesQuery.data?.map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
            <input className="field" placeholder="Product name" value={product.name} onChange={(event) => setProduct((current) => ({ ...current, name: event.target.value }))} required />
            <input className="field" placeholder="Base price" value={product.base_price} onChange={(event) => setProduct((current) => ({ ...current, base_price: event.target.value }))} required />
            <input className="field" placeholder="Image URL" value={product.image_url} onChange={(event) => setProduct((current) => ({ ...current, image_url: event.target.value }))} />
            <textarea className="field min-h-24 sm:col-span-2" placeholder="Description" value={product.description} onChange={(event) => setProduct((current) => ({ ...current, description: event.target.value }))} required />
            <input className="field" placeholder="Variant SKU" value={product.sku} onChange={(event) => setProduct((current) => ({ ...current, sku: event.target.value }))} />
            <input className="field" placeholder="Variant name" value={product.variant_name} onChange={(event) => setProduct((current) => ({ ...current, variant_name: event.target.value }))} />
            <input className="field" placeholder="Variant price delta" value={product.variant_price_delta} onChange={(event) => setProduct((current) => ({ ...current, variant_price_delta: event.target.value }))} />
            <select className="field" value={product.warehouse_id} onChange={(event) => setProduct((current) => ({ ...current, warehouse_id: event.target.value }))}>
              <option value="">No initial stock</option>
              {warehousesQuery.data?.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
            <input className="field" placeholder="Initial stock quantity" value={product.stock_quantity} onChange={(event) => setProduct((current) => ({ ...current, stock_quantity: event.target.value }))} />
          </div>
          {createProductMutation.isError && <p className="mt-3 text-sm font-medium text-red-700">Product creation failed. Check category, SKU, and warehouse details.</p>}
          <button type="submit" className="primary-button mt-5">Publish product</button>
        </form>
      </div>

      <section className="mt-8 rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-950">Seller product management</h2>
        <div className="mt-4 grid gap-3">
          {productsQuery.data?.map((item) => (
            <div key={item.id} className="flex flex-col gap-2 rounded-md border border-slate-200 p-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold text-slate-950">{item.name}</p>
                <p className="text-sm text-slate-600">{item.status} · {money(item.base_price)}</p>
              </div>
              <Link to={`/products/${item.id}`} className="secondary-button">View</Link>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
