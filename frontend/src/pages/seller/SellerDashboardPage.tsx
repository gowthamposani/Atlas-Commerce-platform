import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PackagePlus, Store } from "lucide-react";
import { Link } from "react-router-dom";

import { catalogApi, inventoryApi, sellerApi } from "../../services/marketplace";
import { ProductPayload } from "../../types/api";
import { money } from "../../utils/money";
import {
  firstError,
  optionalText,
  trimmed,
  validateCode,
  validateNonNegativeDecimal,
  validateNonNegativeInteger,
  validateOptionalHttpUrl,
  validatePositiveDecimal,
  validateRequiredText,
  validateSku,
} from "../../utils/validation";

export function SellerDashboardPage() {
  const queryClient = useQueryClient();
  const [storeName, setStoreName] = useState("");
  const [storeDescription, setStoreDescription] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [categoryDescription, setCategoryDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
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
    onError: () => setError("Seller registration failed. Check the store details and try again."),
  });

  const createCategoryMutation = useMutation({
    mutationFn: catalogApi.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      setCategoryName("");
      setCategoryDescription("");
    },
    onError: () => setError("Category creation failed. Check the category details and try again."),
  });

  const createWarehouseMutation = useMutation({
    mutationFn: inventoryApi.createWarehouse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["seller", "warehouses"] });
      setWarehouse({ name: "", code: "", city: "", state: "", country: "US" });
    },
    onError: () => setError("Warehouse creation failed. Check the warehouse details and try again."),
  });

  const createProductMutation = useMutation({
    mutationFn: async () => {
      const variants: ProductPayload["variants"] =
        product.sku && product.variant_name
          ? [
              {
                sku: trimmed(product.sku).toUpperCase(),
                name: trimmed(product.variant_name),
                price_delta: Number(product.variant_price_delta) || 0,
                attributes: { option: trimmed(product.variant_name) },
                is_active: true,
              },
            ]
          : [];

      const created = await sellerApi.createProduct({
        category_id: product.category_id,
        name: trimmed(product.name),
        description: trimmed(product.description),
        base_price: Number(product.base_price),
        status: "active",
        images: product.image_url
          ? [{ url: trimmed(product.image_url), alt_text: trimmed(product.name), sort_order: 0, is_primary: true }]
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
    onError: () => setError("Product creation failed. Check category, SKU, price, and warehouse details."),
  });

  const handleSellerRegister = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (registerSellerMutation.isPending) return;
    const validationError = validateRequiredText(storeName, "Store name");
    if (validationError) {
      setError(validationError);
      return;
    }
    registerSellerMutation.mutate({
      store_name: trimmed(storeName),
      description: optionalText(storeDescription),
    });
  };

  const handleCategoryCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (createCategoryMutation.isPending) return;
    const validationError = validateRequiredText(categoryName, "Category name");
    if (validationError) {
      setError(validationError);
      return;
    }
    createCategoryMutation.mutate({
      name: trimmed(categoryName),
      description: optionalText(categoryDescription),
    });
  };

  const handleWarehouseCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (createWarehouseMutation.isPending) return;
    const validationError = firstError(
      validateRequiredText(warehouse.name, "Warehouse name"),
      validateCode(warehouse.code, "Warehouse code"),
      validateRequiredText(warehouse.city, "Warehouse city"),
      validateRequiredText(warehouse.state, "Warehouse state"),
      validateRequiredText(warehouse.country, "Warehouse country"),
    );
    if (validationError) {
      setError(validationError);
      return;
    }
    createWarehouseMutation.mutate({
      name: trimmed(warehouse.name),
      code: trimmed(warehouse.code).toUpperCase(),
      city: trimmed(warehouse.city),
      state: trimmed(warehouse.state),
      country: trimmed(warehouse.country).toUpperCase(),
    });
  };

  const handleProductCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (createProductMutation.isPending) return;
    const hasVariantInput = Boolean(trimmed(product.sku) || trimmed(product.variant_name));
    const validationError = firstError(
      validateRequiredText(product.category_id, "Category"),
      validateRequiredText(product.name, "Product name"),
      validateRequiredText(product.description, "Product description"),
      validatePositiveDecimal(product.base_price, "Base price"),
      validateOptionalHttpUrl(product.image_url, "Image URL"),
      validateSku(product.sku),
      hasVariantInput ? validateRequiredText(product.sku, "Variant SKU") : null,
      hasVariantInput ? validateRequiredText(product.variant_name, "Variant name") : null,
      validateNonNegativeDecimal(product.variant_price_delta, "Variant price delta"),
      product.warehouse_id ? validateNonNegativeInteger(product.stock_quantity, "Initial stock quantity") : null,
    );
    if (validationError) {
      setError(validationError);
      return;
    }
    createProductMutation.mutate();
  };

  if (dashboardQuery.isError) {
    return (
      <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-4xl items-center px-4 py-10 sm:px-6 lg:px-8">
        <form onSubmit={handleSellerRegister} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm" noValidate>
          <Store className="text-teal-700" size={28} aria-hidden="true" />
          <h1 className="mt-4 text-3xl font-bold text-slate-950">Register as a seller</h1>
          {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}
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
          <button type="submit" className="primary-button mt-6" disabled={registerSellerMutation.isPending}>Create seller profile</button>
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

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[
          ["Products", dashboard?.product_count ?? 0],
          ["Revenue", money(dashboard?.revenue ?? 0)],
          ["Orders", dashboard?.order_count ?? 0],
          ["Inventory", dashboard?.total_stock ?? 0],
          ["Low Stock", dashboard?.low_stock_count ?? 0],
        ].map(([label, value]) => (
          <div key={label} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-bold text-slate-950">{value}</p>
          </div>
        ))}
      </div>

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Recent orders</h2>
          <div className="mt-4 grid gap-3">
            {dashboard?.recent_orders.map((order) => (
              <div key={order.id} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold text-slate-950">{order.order_number}</p>
                    <p className="mt-1 text-sm text-slate-600">{order.status}</p>
                  </div>
                  <p className="font-bold text-slate-950">{money(order.total_amount)}</p>
                </div>
              </div>
            ))}
            {!dashboard?.recent_orders.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                No seller orders yet. Orders containing your products will appear here.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Top products</h2>
          <div className="mt-4 grid gap-3">
            {dashboard?.top_products.map((item) => (
              <div key={item.product_id} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold text-slate-950">{item.name}</p>
                    <p className="mt-1 text-sm text-slate-600">{item.units_sold} units sold</p>
                  </div>
                  <p className="font-bold text-slate-950">{money(item.revenue)}</p>
                </div>
              </div>
            ))}
            {!dashboard?.top_products.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                Top products will appear after customers place orders.
              </p>
            )}
          </div>
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {error ? <p className="text-sm font-medium text-red-700 lg:col-span-2">{error}</p> : null}
        <form onSubmit={handleCategoryCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm" noValidate>
          <h2 className="text-lg font-semibold text-slate-950">Create category</h2>
          <div className="mt-4 grid gap-3">
            <input className="field" placeholder="Category name" value={categoryName} onChange={(event) => setCategoryName(event.target.value)} required />
            <input className="field" placeholder="Description" value={categoryDescription} onChange={(event) => setCategoryDescription(event.target.value)} />
          </div>
          <button type="submit" className="primary-button mt-4" disabled={createCategoryMutation.isPending}>Save category</button>
        </form>

        <form onSubmit={handleWarehouseCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm" noValidate>
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
          <button type="submit" className="primary-button mt-4" disabled={createWarehouseMutation.isPending}>Save warehouse</button>
        </form>

        <form onSubmit={handleProductCreate} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2" noValidate>
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
            <input className="field" placeholder="Base price" value={product.base_price} onChange={(event) => setProduct((current) => ({ ...current, base_price: event.target.value }))} inputMode="decimal" required />
            <input className="field" placeholder="Image URL" value={product.image_url} onChange={(event) => setProduct((current) => ({ ...current, image_url: event.target.value }))} />
            <textarea className="field min-h-24 sm:col-span-2" placeholder="Description" value={product.description} onChange={(event) => setProduct((current) => ({ ...current, description: event.target.value }))} required />
            <input className="field" placeholder="Variant SKU" value={product.sku} onChange={(event) => setProduct((current) => ({ ...current, sku: event.target.value }))} />
            <input className="field" placeholder="Variant name" value={product.variant_name} onChange={(event) => setProduct((current) => ({ ...current, variant_name: event.target.value }))} />
            <input className="field" placeholder="Variant price delta" value={product.variant_price_delta} onChange={(event) => setProduct((current) => ({ ...current, variant_price_delta: event.target.value }))} inputMode="decimal" />
            <select className="field" value={product.warehouse_id} onChange={(event) => setProduct((current) => ({ ...current, warehouse_id: event.target.value }))}>
              <option value="">No initial stock</option>
              {warehousesQuery.data?.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
            <input className="field" placeholder="Initial stock quantity" value={product.stock_quantity} onChange={(event) => setProduct((current) => ({ ...current, stock_quantity: event.target.value }))} inputMode="numeric" />
          </div>
          <button type="submit" className="primary-button mt-5" disabled={createProductMutation.isPending}>Publish product</button>
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
          {!productsQuery.isLoading && !productsQuery.data?.length && (
            <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
              No products yet. Create a product above to populate your seller catalog.
            </p>
          )}
        </div>
      </section>
    </section>
  );
}
