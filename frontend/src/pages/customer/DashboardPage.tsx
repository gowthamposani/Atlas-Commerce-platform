import { Link } from "react-router-dom";
import { MapPin, ShieldCheck, UserRound } from "lucide-react";

import { useAuth } from "../../context/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();
  const profile = user?.profile;

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
            Dashboard
          </p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">
            Welcome{profile ? `, ${profile.first_name}` : ""}
          </h1>
        </div>
        <Link to="/profile" className="primary-button">
          <UserRound size={17} aria-hidden="true" />
          Profile
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <ShieldCheck className="text-teal-700" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Role</h2>
          <p className="mt-2 text-sm text-slate-600">{user?.role ?? "customer"}</p>
        </section>
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <UserRound className="text-slate-700" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Account</h2>
          <p className="mt-2 break-all text-sm text-slate-600">{user?.email}</p>
        </section>
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <MapPin className="text-amber-600" size={24} aria-hidden="true" />
          <h2 className="mt-4 text-base font-semibold text-slate-950">Shipping</h2>
          <p className="mt-2 text-sm text-slate-600">Manage saved addresses from Profile.</p>
        </section>
      </div>
    </section>
  );
}
