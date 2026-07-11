import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

import { cartApi, customerApi, orderApi } from "../../services/marketplace";
import { CheckoutPayload } from "../../types/api";
import { money } from "../../utils/money";
import {
  firstError,
  optionalText,
  trimmed,
  validatePersonName,
  validatePostalCode,
  validateRequiredText,
} from "../../utils/validation";

export function CheckoutPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const cartQuery = useQuery({ queryKey: ["cart"], queryFn: cartApi.summary });
  const addressesQuery = useQuery({ queryKey: ["customer", "addresses"], queryFn: customerApi.addresses });
  const [shippingAddressId, setShippingAddressId] = useState("");
  const [couponCode, setCouponCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [billing, setBilling] = useState<CheckoutPayload["billing_address"]>({
    recipient_name: "",
    line1: "",
    line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "US",
  });

  useEffect(() => {
    const defaultAddress = addressesQuery.data?.find((address) => address.is_default_shipping) ?? addressesQuery.data?.[0];
    if (defaultAddress && !shippingAddressId) {
      setShippingAddressId(defaultAddress.id);
      setBilling({
        recipient_name: defaultAddress.recipient_name,
        line1: defaultAddress.line1,
        line2: defaultAddress.line2 ?? "",
        city: defaultAddress.city,
        state: defaultAddress.state,
        postal_code: defaultAddress.postal_code,
        country: defaultAddress.country,
      });
    }
  }, [addressesQuery.data, shippingAddressId]);

  const orderMutation = useMutation({
    mutationFn: orderApi.create,
    onSuccess: (order) => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      navigate(`/orders/${order.id}/confirmation`);
    },
    onError: () => setError("Checkout failed. Check inventory and address details."),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (orderMutation.isPending) return;
    const validationError = firstError(
      validateRequiredText(shippingAddressId, "Shipping address"),
      validatePersonName(billing.recipient_name, "Billing recipient"),
      validateRequiredText(billing.line1, "Billing address line 1"),
      validateRequiredText(billing.city, "Billing city"),
      validateRequiredText(billing.state, "Billing state"),
      validatePostalCode(billing.postal_code, billing.country),
      validateRequiredText(billing.country, "Billing country"),
    );
    if (validationError) {
      setError(validationError);
      return;
    }
    orderMutation.mutate({
      shipping_address_id: shippingAddressId,
      billing_address: {
        recipient_name: trimmed(billing.recipient_name),
        line1: trimmed(billing.line1),
        line2: optionalText(billing.line2),
        city: trimmed(billing.city),
        state: trimmed(billing.state),
        postal_code: trimmed(billing.postal_code),
        country: trimmed(billing.country).toUpperCase(),
      },
      coupon_code: optionalText(couponCode)?.toUpperCase(),
      payment_method: "placeholder",
    });
  };

  const cart = cartQuery.data;
  const estimatedTax = (cart?.subtotal ?? 0) * 0.08;
  const shipping = (cart?.subtotal ?? 0) >= 75 ? 0 : 8.99;

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-slate-950">Checkout</h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
        <form onSubmit={handleSubmit} className="rounded-md border border-slate-200 bg-white p-6 shadow-sm" noValidate>
          <h2 className="text-lg font-semibold text-slate-950">Shipping address</h2>
          {addressesQuery.data?.length ? (
            <select className="field mt-4" value={shippingAddressId} onChange={(event) => setShippingAddressId(event.target.value)} required>
              {addressesQuery.data.map((address) => (
                <option key={address.id} value={address.id}>
                  {address.label} · {address.line1}, {address.city}
                </option>
              ))}
            </select>
          ) : (
            <p className="mt-4 text-sm text-slate-600">
              Add an address from <Link to="/profile" className="font-semibold text-teal-700">Profile</Link> before checkout.
            </p>
          )}

          <h2 className="mt-8 text-lg font-semibold text-slate-950">Billing address</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {[
              ["recipient_name", "Recipient"],
              ["line1", "Address line 1"],
              ["line2", "Address line 2"],
              ["city", "City"],
              ["state", "State"],
              ["postal_code", "Postal code"],
              ["country", "Country"],
            ].map(([field, label]) => (
              <label key={field} className="grid gap-1">
                <span className="label">{label}</span>
                <input
                  className="field"
                  value={billing[field as keyof typeof billing] ?? ""}
                  onChange={(event) => setBilling((current) => ({ ...current, [field]: event.target.value }))}
                  required={field !== "line2"}
                />
              </label>
            ))}
          </div>

          <label className="mt-5 grid gap-1">
            <span className="label">Coupon code</span>
            <input className="field" value={couponCode} onChange={(event) => setCouponCode(event.target.value)} />
          </label>

          {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}

          <button type="submit" className="primary-button mt-6" disabled={!cart?.items.length || !addressesQuery.data?.length || orderMutation.isPending}>
            Create order
          </button>
        </form>

        <aside className="h-fit rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Order summary</h2>
          <div className="mt-4 grid gap-2 text-sm text-slate-700">
            <div className="flex justify-between"><span>Subtotal</span><span>{money(cart?.subtotal ?? 0)}</span></div>
            <div className="flex justify-between"><span>Tax</span><span>{money(estimatedTax)}</span></div>
            <div className="flex justify-between"><span>Shipping</span><span>{money(shipping)}</span></div>
            <div className="flex justify-between border-t border-slate-200 pt-3 text-base font-bold text-slate-950">
              <span>Total</span><span>{money((cart?.subtotal ?? 0) + estimatedTax + shipping)}</span>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
