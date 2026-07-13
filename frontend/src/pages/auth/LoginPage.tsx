import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { api } from "../../services/api";
import { CurrentUser, LoginPayload, UserRole } from "../../types/api";
import { trimmed } from "../../utils/validation";

type LoginMode = "customer" | "admin";

const portalConfig: Record<
  LoginMode,
  {
    title: string;
    formTitle: string;
    description: string;
    buttonLabel: string;
    role: UserRole;
  }
> = {
  customer: {
    title: "Customer Login",
    formTitle: "Customer Login",
    description: "Browse products, manage wishlist, cart, orders and profile.",
    buttonLabel: "Continue as Customer",
    role: "customer",
  },
  admin: {
    title: "Administrator Login",
    formTitle: "Administrator Login",
    description: "Manage users, products, reports, orders and platform operations.",
    buttonLabel: "Continue as Admin",
    role: "admin",
  },
};

export function LoginPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState<LoginPayload>({ email: "", password: "" });
  const [mode, setMode] = useState<LoginMode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const message =
    typeof location.state === "object" && location.state !== null && "message" in location.state
      ? String(location.state.message)
      : null;

  const mutation = useMutation({
    mutationFn: async (payload: LoginPayload) => {
      await auth.login(payload);
      const response = await api.get<CurrentUser>("/auth/me");
      return response.data;
    },
    onSuccess: async (user: CurrentUser) => {
      if (mode === "customer" && user.role !== "customer") {
        await auth.logout();
        setSuccess(null);
        setError(
          "You are trying to login through the wrong portal. Please choose Administrator Login.",
        );
        return;
      }
      if (mode === "admin" && user.role !== "admin") {
        await auth.logout();
        setSuccess(null);
        setError("This account is not authorized for Administrator access.");
        return;
      }

      setError(null);
      setSuccess("Login successful. Redirecting...");
      navigate(user.role === "admin" ? "/admin" : "/dashboard");
    },
    onError: () => setError("Login failed. Check your email and password."),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (mutation.isPending) return;
    if (mode === null) {
      setError("Please select a login portal before continuing.");
      return;
    }
    if (!trimmed(form.email)) {
      setError("Email is required.");
      return;
    }
    if (!form.password) {
      setError("Password is required.");
      return;
    }
    mutation.mutate({ email: trimmed(form.email).toLowerCase(), password: form.password });
  };

  const selectMode = (selectedMode: LoginMode) => {
    setMode(selectedMode);
    setError(null);
    setSuccess(null);
  };

  if (mode === null) {
    return (
      <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl content-center gap-8 px-4 py-10 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
            Secure access
          </p>
          <h1 className="mt-4 text-3xl font-bold text-slate-950">Select Login Type</h1>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            Choose the correct portal for your Atlas Commerce account. The same secure JWT
            authentication flow is used for both experiences.
          </p>
        </div>

        {message ? <p className="toast-success mx-auto w-full max-w-3xl">{message}</p> : null}
        {error ? <p className="toast-error mx-auto w-full max-w-3xl">{error}</p> : null}

        <div className="grid gap-5 md:grid-cols-2">
          <LoginPortalCard
            description={portalConfig.customer.description}
            icon="customer"
            label={portalConfig.customer.buttonLabel}
            onClick={() => selectMode("customer")}
            title={portalConfig.customer.title}
          />
          <LoginPortalCard
            description={portalConfig.admin.description}
            icon="admin"
            label={portalConfig.admin.buttonLabel}
            onClick={() => selectMode("admin")}
            title={portalConfig.admin.title}
          />
        </div>

        <p className="text-center text-sm text-slate-600">
          New customer?{" "}
          <Link to="/register" className="font-semibold text-teal-700 hover:text-teal-800">
            Create account
          </Link>
        </p>
      </section>
    );
  }

  const selectedPortal = portalConfig[mode];
  const PortalIcon = mode === "admin" ? ShieldCheck : UserRound;

  return (
    <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[0.85fr_1fr] lg:px-8">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
          {mode === "admin" ? "Administrator access" : "Customer access"}
        </p>
        <h1 className="mt-4 flex items-center gap-3 text-3xl font-bold text-slate-950">
          <span className="inline-flex h-12 w-12 items-center justify-center rounded-md bg-teal-50 text-teal-700">
            <PortalIcon className="h-6 w-6" aria-hidden="true" />
          </span>
          {selectedPortal.formTitle}
        </h1>
        <p className="mt-4 max-w-md text-sm leading-6 text-slate-600">
          {selectedPortal.description}
        </p>
        <button
          type="button"
          className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-teal-700 transition hover:text-teal-800"
          onClick={() => selectMode(mode === "admin" ? "customer" : "admin")}
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Use {mode === "admin" ? "customer" : "admin"} portal
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-lg border border-slate-200 bg-white p-6 shadow-lg shadow-slate-200/60 transition"
      >
        {message ? (
          <p className="toast-success mb-4">{message}</p>
        ) : null}
        {success ? <p className="toast-success mb-4">{success}</p> : null}

        <div className="grid gap-4">
          <label className="grid gap-1">
            <span className="label">Email</span>
            <input
              className="field"
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm((current) => ({ ...current, email: event.target.value }))
              }
              required
            />
          </label>
          <label className="grid gap-1">
            <span className="label">Password</span>
            <input
              className="field"
              type="password"
              value={form.password}
              onChange={(event) =>
                setForm((current) => ({ ...current, password: event.target.value }))
              }
              required
            />
          </label>
        </div>

        {error ? <p className="toast-error mt-4">{error}</p> : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button type="submit" className="primary-button" disabled={mutation.isPending}>
            {mutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            )}
            Login
          </button>
          <Link to="/register" className="text-sm font-semibold text-teal-700 hover:text-teal-800">
            Create account
          </Link>
        </div>
      </form>
    </section>
  );
}

function LoginPortalCard({
  description,
  icon,
  label,
  onClick,
  title,
}: {
  description: string;
  icon: LoginMode;
  label: string;
  onClick: () => void;
  title: string;
}) {
  const Icon = icon === "admin" ? ShieldCheck : UserRound;

  return (
    <article className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/70 transition duration-200 hover:-translate-y-1 hover:border-teal-300 hover:shadow-xl hover:shadow-slate-200 focus-within:border-teal-500 focus-within:ring-2 focus-within:ring-teal-100">
      <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-teal-50 text-teal-700 transition group-hover:bg-teal-700 group-hover:text-white">
        <Icon className="h-7 w-7" aria-hidden="true" />
      </div>
      <h2 className="mt-5 text-xl font-semibold text-slate-950">{title}</h2>
      <p className="mt-3 min-h-16 text-sm leading-6 text-slate-600">{description}</p>
      <button
        type="button"
        className="secondary-button mt-6 w-full justify-between group-hover:border-teal-600 group-hover:text-teal-700"
        onClick={onClick}
      >
        {label}
        <ArrowRight className="h-4 w-4" aria-hidden="true" />
      </button>
    </article>
  );
}
