export type UserRole = "customer" | "admin";

export interface CustomerProfile {
  id: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  profile: CustomerProfile;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  user: CurrentUser;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ProfileUpdatePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
}

export interface Address {
  id: string;
  label: string;
  recipient_name: string;
  line1: string;
  line2: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string | null;
  is_default_shipping: boolean;
  created_at: string;
  updated_at: string;
}

export interface AddressPayload {
  label: string;
  recipient_name: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
  is_default_shipping: boolean;
}
