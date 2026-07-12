import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { RegisterPayload } from "../../types/api";
import {
  PHONE_MESSAGE,
  firstError,
  optionalText,
  trimmed,
  validatePassword,
  validatePersonName,
  validatePhone,
} from "../../utils/validation";

const initialForm: RegisterPayload = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone: "",
};

export function RegisterPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: auth.register,
    onSuccess: () => {
      navigate("/login", {
        state: { message: "Account created. Sign in to continue." },
      });
    },
    onError: () => {
      setError("Registration failed. Check the details and try again.");
    },
  });

  const updateField = (field: keyof RegisterPayload, value: string) => {
    setError(null);
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (mutation.isPending) return;
    const validationError = firstError(
      validatePersonName(form.first_name, "First name"),
      validatePersonName(form.last_name, "Last name"),
      validatePassword(form.password),
      validatePhone(form.phone),
    );
    if (validationError) {
      setError(validationError);
      return;
    }
    const payload = {
      email: trimmed(form.email).toLowerCase(),
      password: form.password,
      first_name: trimmed(form.first_name),
      last_name: trimmed(form.last_name),
      phone: optionalText(form.phone),
    };
    mutation.mutate(payload);
  };

  return (
    <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[0.85fr_1fr] lg:px-8">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
          New customer
        </p>
        <h1 className="mt-4 text-3xl font-bold text-slate-950">Create your account</h1>
        <p className="mt-4 max-w-md text-sm leading-6 text-slate-600">
          Your profile is created in the backend as soon as registration succeeds.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm" noValidate>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-1">
            <span className="label">First name</span>
            <input
              className="field"
              name="first_name"
              value={form.first_name}
              onChange={(event) => updateField("first_name", event.target.value)}
              required
            />
          </label>
          <label className="grid gap-1">
            <span className="label">Last name</span>
            <input
              className="field"
              name="last_name"
              value={form.last_name}
              onChange={(event) => updateField("last_name", event.target.value)}
              required
            />
          </label>
          <label className="grid gap-1 sm:col-span-2">
            <span className="label">Email</span>
            <input
              className="field"
              name="email"
              type="email"
              value={form.email}
              onChange={(event) => updateField("email", event.target.value)}
              required
            />
          </label>
          <label className="grid gap-1 sm:col-span-2">
            <span className="label">Password</span>
            <input
              className="field"
              name="password"
              type="password"
              value={form.password}
              onChange={(event) => updateField("password", event.target.value)}
              minLength={8}
              required
            />
          </label>
          <label className="grid gap-1 sm:col-span-2">
            <span className="label">Phone</span>
            <input
              className="field"
              name="phone"
              value={form.phone}
              onChange={(event) => updateField("phone", event.target.value)}
              inputMode="tel"
              pattern="^\+?\d{10,15}$"
              title={PHONE_MESSAGE}
            />
          </label>
        </div>

        {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button type="submit" className="primary-button" disabled={mutation.isPending}>
            Register
          </button>
          <Link to="/login" className="text-sm font-semibold text-teal-700 hover:text-teal-800">
            Already have an account?
          </Link>
        </div>
      </form>
    </section>
  );
}
