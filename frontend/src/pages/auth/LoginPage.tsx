import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { LoginPayload } from "../../types/api";

export function LoginPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState<LoginPayload>({ email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const message =
    typeof location.state === "object" && location.state !== null && "message" in location.state
      ? String(location.state.message)
      : null;

  const mutation = useMutation({
    mutationFn: auth.login,
    onSuccess: () => navigate("/dashboard"),
    onError: () => setError("Login failed. Check your email and password."),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    mutation.mutate(form);
  };

  return (
    <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[0.85fr_1fr] lg:px-8">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
          Customer access
        </p>
        <h1 className="mt-4 text-3xl font-bold text-slate-950">Login</h1>
        <p className="mt-4 max-w-md text-sm leading-6 text-slate-600">
          Authentication uses JWT access tokens and persisted refresh tokens.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
        {message ? (
          <p className="mb-4 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800">
            {message}
          </p>
        ) : null}

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

        {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button type="submit" className="primary-button" disabled={mutation.isPending}>
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
