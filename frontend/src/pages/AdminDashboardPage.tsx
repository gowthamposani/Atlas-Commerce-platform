import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Ban,
  Bell,
  Bot,
  CheckCircle2,
  CreditCard,
  Download,
  EyeOff,
  FileText,
  PackageCheck,
  ShieldCheck,
  Star,
  Truck,
  Users,
  XCircle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import {
  createNotification,
  createPaymentIntent,
  createShipment,
  getAdminDashboard,
  getAdminOrders,
  getAdminProducts,
  getAdminReviews,
  getAdminSellers,
  getAdminUsers,
  getNotifications,
  getPayments,
  getProductDescription,
  getReport,
  moderateProduct,
  moderateReview,
  moderateSeller,
  refundOrder,
  setOrderStatus,
  setPaymentStatus,
  setUserActive,
} from "../services/admin";
import {
  Order,
  PaymentTransaction,
  ProductListItem,
  Review,
  Seller,
  AdminUser,
} from "../types/api";
import { money } from "../utils/money";

type AdminTab =
  | "overview"
  | "users"
  | "sellers"
  | "products"
  | "orders"
  | "reviews"
  | "reports"
  | "notifications"
  | "payments"
  | "ai";

const tabs: Array<{ id: AdminTab; label: string }> = [
  { id: "overview", label: "Overview" },
  { id: "users", label: "Users" },
  { id: "sellers", label: "Sellers" },
  { id: "products", label: "Products" },
  { id: "orders", label: "Orders" },
  { id: "reviews", label: "Reviews" },
  { id: "reports", label: "Reports" },
  { id: "notifications", label: "Notifications" },
  { id: "payments", label: "Payments" },
  { id: "ai", label: "AI" },
];

export function AdminDashboardPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<AdminTab>("overview");

  if (user?.role !== "admin") {
    return (
      <section className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-md border border-amber-200 bg-amber-50 p-6 text-amber-900">
          <ShieldCheck className="mb-3 h-6 w-6" />
          <h1 className="text-xl font-semibold">Admin access required</h1>
          <p className="mt-2 text-sm">Your account is authenticated but does not have admin RBAC.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6">
      <div className="flex flex-col gap-2 border-b border-slate-200 pb-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Admin</p>
          <h1 className="text-2xl font-semibold text-slate-950">Operations Dashboard</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              className={`rounded-md px-3 py-2 text-sm font-semibold ${
                activeTab === tab.id
                  ? "bg-slate-950 text-white"
                  : "border border-slate-200 bg-white text-slate-700"
              }`}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              type="button"
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      {activeTab === "overview" && <OverviewPanel />}
      {activeTab === "users" && <UsersPanel />}
      {activeTab === "sellers" && <SellersPanel />}
      {activeTab === "products" && <ProductsPanel />}
      {activeTab === "orders" && <OrdersPanel />}
      {activeTab === "reviews" && <ReviewsPanel />}
      {activeTab === "reports" && <ReportsPanel />}
      {activeTab === "notifications" && <NotificationsPanel />}
      {activeTab === "payments" && <PaymentsPanel />}
      {activeTab === "ai" && <AiPanel />}
    </section>
  );
}

function OverviewPanel() {
  const dashboardQuery = useQuery({ queryKey: ["admin", "dashboard"], queryFn: getAdminDashboard });
  const dashboard = dashboardQuery.data;
  const stats = dashboardQuery.data?.stats;
  const tiles: Array<[string, string | number, LucideIcon]> = [
    ["Customers", stats?.total_customers ?? 0, Users],
    ["Sellers", stats?.total_sellers ?? 0, ShieldCheck],
    ["Categories", stats?.total_categories ?? 0, FileText],
    ["Products", stats?.total_products ?? 0, PackageCheck],
    ["Orders", stats?.total_orders ?? 0, FileText],
    ["Revenue", money(stats?.revenue ?? stats?.revenue_summary ?? 0), CreditCard],
    ["Pending Orders", stats?.pending_orders ?? 0, Truck],
    ["Pending Sellers", stats?.pending_seller_approvals ?? 0, ShieldCheck],
    ["Pending Products", stats?.pending_products ?? dashboard?.pending_products ?? 0, EyeOff],
    ["Pending Reviews", stats?.pending_reviews ?? dashboard?.pending_reviews ?? 0, Star],
    ["Inventory Alerts", stats?.inventory_alerts ?? dashboard?.inventory_alerts ?? 0, PackageCheck],
  ];

  return (
    <div className="grid gap-6">
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
        {tiles.map(([label, value, Icon]) => (
          <div className="rounded-md border border-slate-200 bg-white p-4" key={label}>
            <Icon className="h-5 w-5 text-teal-700" />
            <p className="mt-3 text-sm text-slate-500">{label}</p>
            <p className="text-2xl font-semibold text-slate-950">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-semibold text-slate-950">Top Selling Products</h2>
          <div className="mt-4 grid gap-3">
            {dashboard?.top_selling_products.map((item) => (
              <div key={item.product_id} className="rounded-md border border-slate-200 p-3">
                <p className="font-semibold text-slate-950">{item.name}</p>
                <p className="mt-1 text-sm text-slate-600">
                  {item.units_sold} units · {money(item.revenue)}
                </p>
              </div>
            ))}
            {!dashboard?.top_selling_products.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                Top products appear after orders are placed.
              </p>
            )}
          </div>
        </div>

        <div className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-semibold text-slate-950">Top Sellers</h2>
          <div className="mt-4 grid gap-3">
            {dashboard?.top_sellers.map((seller) => (
              <div key={seller.seller_id} className="rounded-md border border-slate-200 p-3">
                <p className="font-semibold text-slate-950">{seller.store_name}</p>
                <p className="mt-1 text-sm text-slate-600">
                  {seller.orders} orders · {money(seller.revenue)}
                </p>
              </div>
            ))}
            {!dashboard?.top_sellers.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                Top sellers appear after marketplace orders are placed.
              </p>
            )}
          </div>
        </div>

        <div className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-semibold text-slate-950">Recent Orders</h2>
          <div className="mt-4 grid gap-3">
            {dashboard?.recent_orders.map((order) => (
              <div key={order.id} className="rounded-md border border-slate-200 p-3">
                <p className="font-semibold text-slate-950">{order.order_number}</p>
                <p className="mt-1 text-sm text-slate-600">
                  {order.status} · {money(order.total_amount)}
                </p>
              </div>
            ))}
            {!dashboard?.recent_orders.length && (
              <p className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600">
                Recent orders appear after checkout activity.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function UsersPanel() {
  const queryClient = useQueryClient();
  const usersQuery = useQuery({ queryKey: ["admin", "users"], queryFn: () => getAdminUsers() });
  const mutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) => setUserActive(id, active),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
  return (
    <DataTable
      columns={["Email", "Role", "Status", "Action"]}
      rows={(usersQuery.data ?? []).map((item: AdminUser) => [
        item.email,
        item.role,
        item.is_active ? "Active" : "Suspended",
        <button
          className={item.is_active ? "danger-button" : "secondary-button"}
          key={item.id}
          onClick={() => mutation.mutate({ id: item.id, active: !item.is_active })}
          type="button"
        >
          {item.is_active ? <Ban className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
          {item.is_active ? "Suspend" : "Activate"}
        </button>,
      ])}
    />
  );
}

function SellersPanel() {
  const queryClient = useQueryClient();
  const sellersQuery = useQuery({ queryKey: ["admin", "sellers"], queryFn: getAdminSellers });
  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: "approved" | "rejected" | "suspended" }) =>
      moderateSeller(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "sellers"] }),
  });
  return (
    <DataTable
      columns={["Store", "Status", "Active", "Actions"]}
      rows={(sellersQuery.data ?? []).map((seller: Seller) => [
        seller.store_name,
        seller.moderation_status,
        seller.is_active ? "Yes" : "No",
        <div className="flex flex-wrap gap-2" key={seller.id}>
          <button className="secondary-button" onClick={() => mutation.mutate({ id: seller.id, status: "approved" })} type="button">
            <CheckCircle2 className="h-4 w-4" /> Approve
          </button>
          <button className="danger-button" onClick={() => mutation.mutate({ id: seller.id, status: "rejected" })} type="button">
            <XCircle className="h-4 w-4" /> Reject
          </button>
        </div>,
      ])}
    />
  );
}

function ProductsPanel() {
  const queryClient = useQueryClient();
  const productsQuery = useQuery({ queryKey: ["admin", "products"], queryFn: () => getAdminProducts() });
  const mutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Parameters<typeof moderateProduct>[1] }) =>
      moderateProduct(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "products"] }),
  });
  return (
    <DataTable
      columns={["Product", "Status", "Visible", "Featured", "Actions"]}
      rows={(productsQuery.data ?? []).map((product: ProductListItem) => [
        product.name,
        product.status,
        product.is_visible ? "Yes" : "No",
        product.is_featured ? "Yes" : "No",
        <div className="flex flex-wrap gap-2" key={product.id}>
          <button className="secondary-button" onClick={() => mutation.mutate({ id: product.id, payload: { status: "active", is_visible: true } })} type="button">
            <CheckCircle2 className="h-4 w-4" /> Approve
          </button>
          <button className="secondary-button" onClick={() => mutation.mutate({ id: product.id, payload: { is_featured: !product.is_featured } })} type="button">
            <Star className="h-4 w-4" /> Feature
          </button>
          <button className="danger-button" onClick={() => mutation.mutate({ id: product.id, payload: { is_visible: false } })} type="button">
            <EyeOff className="h-4 w-4" /> Hide
          </button>
        </div>,
      ])}
    />
  );
}

function OrdersPanel() {
  const queryClient = useQueryClient();
  const ordersQuery = useQuery({ queryKey: ["admin", "orders"], queryFn: getAdminOrders });
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => setOrderStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "orders"] }),
  });
  const refundMutation = useMutation({
    mutationFn: refundOrder,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "orders"] }),
  });
  const shipmentMutation = useMutation({
    mutationFn: ({ id }: { id: string }) => createShipment(id, `TRK-${id.slice(0, 8).toUpperCase()}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "orders"] }),
  });
  return (
    <DataTable
      columns={["Order", "Status", "Total", "Shipment", "Actions"]}
      rows={(ordersQuery.data ?? []).map((order: Order) => [
        order.order_number,
        order.status,
        money(order.total_amount),
        order.tracking_number ?? order.shipment_status,
        <div className="flex flex-wrap gap-2" key={order.id}>
          <button className="secondary-button" onClick={() => statusMutation.mutate({ id: order.id, status: "shipped" })} type="button">
            <Truck className="h-4 w-4" /> Ship
          </button>
          <button className="secondary-button" onClick={() => shipmentMutation.mutate({ id: order.id })} type="button">
            <PackageCheck className="h-4 w-4" /> Label
          </button>
          <button className="danger-button" onClick={() => refundMutation.mutate(order.id)} type="button">
            Refund
          </button>
        </div>,
      ])}
    />
  );
}

function ReviewsPanel() {
  const queryClient = useQueryClient();
  const reviewsQuery = useQuery({ queryKey: ["admin", "reviews"], queryFn: getAdminReviews });
  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: "approved" | "deleted" }) =>
      moderateReview(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "reviews"] }),
  });
  return (
    <DataTable
      columns={["Rating", "Review", "Status", "Actions"]}
      rows={(reviewsQuery.data ?? []).map((review: Review) => [
        review.rating,
        review.title ?? review.body,
        review.status,
        <div className="flex gap-2" key={review.id}>
          <button className="secondary-button" onClick={() => mutation.mutate({ id: review.id, status: "approved" })} type="button">
            Approve
          </button>
          <button className="danger-button" onClick={() => mutation.mutate({ id: review.id, status: "deleted" })} type="button">
            Delete
          </button>
        </div>,
      ])}
    />
  );
}

function ReportsPanel() {
  const [name, setName] = useState("sales");
  const reportQuery = useQuery({ queryKey: ["admin", "report", name], queryFn: () => getReport(name) });
  const rows = reportQuery.data?.rows ?? [];
  const columns = useMemo(() => (rows[0] ? Object.keys(rows[0]) : ["Report"]), [rows]);
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {["sales", "revenue", "customers", "sellers", "inventory"].map((report) => (
          <button className="secondary-button" key={report} onClick={() => setName(report)} type="button">
            <FileText className="h-4 w-4" /> {report}
          </button>
        ))}
        <a className="secondary-button" href={`/api/admin/reports/${name}.csv`}>
          <Download className="h-4 w-4" /> CSV
        </a>
      </div>
      <DataTable columns={columns} rows={rows.map((row) => columns.map((column) => String(row[column] ?? "")))} />
    </div>
  );
}

function NotificationsPanel() {
  const queryClient = useQueryClient();
  const notificationsQuery = useQuery({ queryKey: ["admin", "notifications"], queryFn: getNotifications });
  const mutation = useMutation({
    mutationFn: () => createNotification("Admin broadcast", "Operational update from Atlas admin."),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "notifications"] }),
  });
  return (
    <div className="space-y-4">
      <button className="primary-button" onClick={() => mutation.mutate()} type="button">
        <Bell className="h-4 w-4" /> Send Broadcast
      </button>
      <DataTable
        columns={["Title", "Type", "Message"]}
        rows={(notificationsQuery.data ?? []).map((item) => [item.title, item.type, item.message])}
      />
    </div>
  );
}

function PaymentsPanel() {
  const queryClient = useQueryClient();
  const ordersQuery = useQuery({ queryKey: ["admin", "orders"], queryFn: getAdminOrders });
  const paymentsQuery = useQuery({ queryKey: ["admin", "payments"], queryFn: getPayments });
  const createMutation = useMutation({
    mutationFn: createPaymentIntent,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "payments"] }),
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: "succeeded" | "failed" | "refunded" }) =>
      setPaymentStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "payments"] }),
  });
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {(ordersQuery.data ?? []).slice(0, 3).map((order) => (
          <button className="secondary-button" key={order.id} onClick={() => createMutation.mutate(order.id)} type="button">
            <CreditCard className="h-4 w-4" /> Intent {order.order_number}
          </button>
        ))}
      </div>
      <DataTable
        columns={["Reference", "Amount", "Status", "Actions"]}
        rows={(paymentsQuery.data ?? []).map((payment: PaymentTransaction) => [
          payment.provider_reference,
          money(payment.amount),
          payment.status,
          <button className="secondary-button" key={payment.id} onClick={() => updateMutation.mutate({ id: payment.id, status: "succeeded" })} type="button">
            Mark Success
          </button>,
        ])}
      />
    </div>
  );
}

function AiPanel() {
  const [description, setDescription] = useState("");
  const productsQuery = useQuery({ queryKey: ["admin", "products"], queryFn: () => getAdminProducts() });
  const mutation = useMutation({
    mutationFn: getProductDescription,
    onSuccess: (data) => setDescription(data.description),
  });
  return (
    <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
      <div className="rounded-md border border-slate-200 bg-white p-4">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Bot className="h-5 w-5 text-teal-700" /> Product AI
        </h2>
        <div className="mt-4 space-y-2">
          {(productsQuery.data ?? []).slice(0, 8).map((product) => (
            <button className="secondary-button w-full justify-start" key={product.id} onClick={() => mutation.mutate(product.id)} type="button">
              {product.name}
            </button>
          ))}
        </div>
      </div>
      <div className="rounded-md border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700">
        {description || "Choose a product to generate an enterprise-ready product description."}
      </div>
    </div>
  );
}

function DataTable({ columns, rows }: { columns: string[]; rows: Array<Array<ReactNode>> }) {
  return (
    <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              {columns.map((column) => (
                <th className="border-b border-slate-200 px-4 py-3 font-semibold" key={column}>
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr className="border-b border-slate-100 last:border-0" key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td className="px-4 py-3 align-top text-slate-700" key={`${rowIndex}-${cellIndex}`}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={columns.length}>
                  No records available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
