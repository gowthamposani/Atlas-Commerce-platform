import { ArrowRight, LockKeyhole, MapPin, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <div>
      <section className="bg-white">
        <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
              Customer portal
            </p>
            <h1 className="mt-4 max-w-2xl text-4xl font-bold leading-tight text-slate-950 sm:text-5xl">
              Atlas Commerce Platform
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-600">
              Create a customer account, manage profile details, and maintain shipping
              addresses with secure token-based access.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="primary-button">
                Create account
                <ArrowRight size={17} aria-hidden="true" />
              </Link>
              <Link to="/login" className="secondary-button">
                Login
              </Link>
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-[#fbfcfd] p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <div>
                <p className="text-sm font-semibold text-slate-950">Customer dashboard</p>
                <p className="mt-1 text-sm text-slate-500">Profile and shipping status</p>
              </div>
              <span className="rounded-md bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">
                Active
              </span>
            </div>
            <div className="mt-5 grid gap-3">
              <div className="flex items-start gap-3 rounded-md border border-slate-200 bg-white p-4">
                <ShieldCheck className="mt-0.5 text-teal-700" size={20} aria-hidden="true" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">RBAC protected account</p>
                  <p className="mt-1 text-sm text-slate-500">Customer access is resolved by JWT role.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-md border border-slate-200 bg-white p-4">
                <MapPin className="mt-0.5 text-amber-600" size={20} aria-hidden="true" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">Default shipping address</p>
                  <p className="mt-1 text-sm text-slate-500">Only one saved address is selected by default.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-md border border-slate-200 bg-white p-4">
                <LockKeyhole className="mt-0.5 text-slate-700" size={20} aria-hidden="true" />
                <div>
                  <p className="text-sm font-semibold text-slate-900">Refresh-token logout</p>
                  <p className="mt-1 text-sm text-slate-500">Session revocation is persisted server-side.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-200 bg-[#eef6f5]">
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="grid gap-4 sm:grid-cols-3">
            {["Register", "Login", "Profile"].map((item) => (
              <div key={item} className="rounded-md border border-teal-100 bg-white p-4">
                <p className="text-sm font-semibold text-slate-950">{item}</p>
                <div className="mt-3 h-2 rounded-full bg-teal-100">
                  <div className="h-2 w-2/3 rounded-full bg-teal-700" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
