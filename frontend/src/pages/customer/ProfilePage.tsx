import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, MapPin, Plus, Star, Trash2 } from "lucide-react";

import { api } from "../../services/api";
import {
  Address,
  AddressPayload,
  CustomerProfile,
  ProfileUpdatePayload,
} from "../../types/api";

const emptyAddress: AddressPayload = {
  label: "",
  recipient_name: "",
  line1: "",
  line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "US",
  phone: "",
  is_default_shipping: true,
};

async function getProfile(): Promise<CustomerProfile> {
  const response = await api.get<CustomerProfile>("/customer/profile");
  return response.data;
}

async function updateProfile(payload: ProfileUpdatePayload): Promise<CustomerProfile> {
  const response = await api.put<CustomerProfile>("/customer/profile", payload);
  return response.data;
}

async function getAddresses(): Promise<Address[]> {
  const response = await api.get<Address[]>("/customer/addresses");
  return response.data;
}

async function createAddress(payload: AddressPayload): Promise<Address> {
  const response = await api.post<Address>("/customer/addresses", payload);
  return response.data;
}

async function setDefaultAddress(addressId: string): Promise<Address> {
  const response = await api.put<Address>(`/customer/addresses/${addressId}/default`);
  return response.data;
}

async function deleteAddress(addressId: string): Promise<void> {
  await api.delete(`/customer/addresses/${addressId}`);
}

export function ProfilePage() {
  const queryClient = useQueryClient();
  const [profileForm, setProfileForm] = useState<ProfileUpdatePayload>({
    first_name: "",
    last_name: "",
    phone: "",
  });
  const [addressForm, setAddressForm] = useState<AddressPayload>(emptyAddress);
  const [notice, setNotice] = useState<string | null>(null);

  const profileQuery = useQuery({ queryKey: ["customer", "profile"], queryFn: getProfile });
  const addressesQuery = useQuery({
    queryKey: ["customer", "addresses"],
    queryFn: getAddresses,
  });

  useEffect(() => {
    if (profileQuery.data) {
      setProfileForm({
        first_name: profileQuery.data.first_name,
        last_name: profileQuery.data.last_name,
        phone: profileQuery.data.phone ?? "",
      });
    }
  }, [profileQuery.data]);

  const updateProfileMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: (profile) => {
      queryClient.setQueryData(["customer", "profile"], profile);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      setNotice("Profile updated.");
    },
  });

  const createAddressMutation = useMutation({
    mutationFn: createAddress,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer", "addresses"] });
      setAddressForm(emptyAddress);
      setNotice("Address saved.");
    },
  });

  const setDefaultMutation = useMutation({
    mutationFn: setDefaultAddress,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer", "addresses"] });
      setNotice("Default shipping address updated.");
    },
  });

  const deleteAddressMutation = useMutation({
    mutationFn: deleteAddress,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer", "addresses"] });
      setNotice("Address removed.");
    },
  });

  const handleProfileSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNotice(null);
    updateProfileMutation.mutate({
      first_name: profileForm.first_name,
      last_name: profileForm.last_name,
      phone: profileForm.phone?.trim() || undefined,
    });
  };

  const handleAddressSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNotice(null);
    createAddressMutation.mutate({
      ...addressForm,
      line2: addressForm.line2?.trim() || undefined,
      phone: addressForm.phone?.trim() || undefined,
    });
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Profile</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">Customer profile</h1>
      </div>

      {notice ? (
        <p className="mb-5 inline-flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800">
          <Check size={16} aria-hidden="true" />
          {notice}
        </p>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <form
          onSubmit={handleProfileSubmit}
          className="rounded-md border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h2 className="text-lg font-semibold text-slate-950">Profile details</h2>
          <div className="mt-5 grid gap-4">
            <label className="grid gap-1">
              <span className="label">First name</span>
              <input
                className="field"
                value={profileForm.first_name}
                onChange={(event) =>
                  setProfileForm((current) => ({
                    ...current,
                    first_name: event.target.value,
                  }))
                }
                required
              />
            </label>
            <label className="grid gap-1">
              <span className="label">Last name</span>
              <input
                className="field"
                value={profileForm.last_name}
                onChange={(event) =>
                  setProfileForm((current) => ({
                    ...current,
                    last_name: event.target.value,
                  }))
                }
                required
              />
            </label>
            <label className="grid gap-1">
              <span className="label">Phone</span>
              <input
                className="field"
                value={profileForm.phone ?? ""}
                onChange={(event) =>
                  setProfileForm((current) => ({ ...current, phone: event.target.value }))
                }
              />
            </label>
          </div>
          <button type="submit" className="primary-button mt-6" disabled={updateProfileMutation.isPending}>
            Save profile
          </button>
        </form>

        <div className="grid gap-6">
          <form
            onSubmit={handleAddressSubmit}
            className="rounded-md border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div className="flex items-center gap-2">
              <MapPin size={20} className="text-amber-600" aria-hidden="true" />
              <h2 className="text-lg font-semibold text-slate-950">Address management</h2>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="grid gap-1">
                <span className="label">Label</span>
                <input
                  className="field"
                  value={addressForm.label}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, label: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1">
                <span className="label">Recipient</span>
                <input
                  className="field"
                  value={addressForm.recipient_name}
                  onChange={(event) =>
                    setAddressForm((current) => ({
                      ...current,
                      recipient_name: event.target.value,
                    }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1 sm:col-span-2">
                <span className="label">Address line 1</span>
                <input
                  className="field"
                  value={addressForm.line1}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, line1: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1 sm:col-span-2">
                <span className="label">Address line 2</span>
                <input
                  className="field"
                  value={addressForm.line2 ?? ""}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, line2: event.target.value }))
                  }
                />
              </label>
              <label className="grid gap-1">
                <span className="label">City</span>
                <input
                  className="field"
                  value={addressForm.city}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, city: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1">
                <span className="label">State</span>
                <input
                  className="field"
                  value={addressForm.state}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, state: event.target.value }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1">
                <span className="label">Postal code</span>
                <input
                  className="field"
                  value={addressForm.postal_code}
                  onChange={(event) =>
                    setAddressForm((current) => ({
                      ...current,
                      postal_code: event.target.value,
                    }))
                  }
                  required
                />
              </label>
              <label className="grid gap-1">
                <span className="label">Country</span>
                <input
                  className="field"
                  value={addressForm.country}
                  onChange={(event) =>
                    setAddressForm((current) => ({ ...current, country: event.target.value }))
                  }
                  required
                />
              </label>
            </div>
            <label className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={addressForm.is_default_shipping}
                onChange={(event) =>
                  setAddressForm((current) => ({
                    ...current,
                    is_default_shipping: event.target.checked,
                  }))
                }
              />
              Default shipping address
            </label>
            <button type="submit" className="primary-button mt-5" disabled={createAddressMutation.isPending}>
              <Plus size={16} aria-hidden="true" />
              Save address
            </button>
          </form>

          <section className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-950">Saved addresses</h2>
            <div className="mt-5 grid gap-3">
              {addressesQuery.data?.length ? (
                addressesQuery.data.map((address) => (
                  <article key={address.id} className="rounded-md border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">{address.label}</p>
                        <p className="mt-1 text-sm text-slate-600">
                          {address.recipient_name}, {address.line1}, {address.city},{" "}
                          {address.state} {address.postal_code}
                        </p>
                        {address.is_default_shipping ? (
                          <p className="mt-2 inline-flex items-center gap-1 rounded-md bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">
                            <Star size={13} aria-hidden="true" />
                            Default shipping
                          </p>
                        ) : null}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => setDefaultMutation.mutate(address.id)}
                          disabled={address.is_default_shipping}
                        >
                          <Star size={15} aria-hidden="true" />
                          Set default
                        </button>
                        <button
                          type="button"
                          className="danger-button"
                          onClick={() => deleteAddressMutation.mutate(address.id)}
                        >
                          <Trash2 size={15} aria-hidden="true" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                <p className="text-sm text-slate-600">
                  {addressesQuery.isLoading ? "Loading addresses..." : "No saved addresses yet."}
                </p>
              )}
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
