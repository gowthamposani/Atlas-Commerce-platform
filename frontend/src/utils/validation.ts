const phonePattern = /^\+?\d+$/;
const personNamePattern = /^[A-Za-z][A-Za-z' -]*$/;
const postalCodePattern = /^[A-Za-z0-9][A-Za-z0-9 -]{1,18}[A-Za-z0-9]$/;
const usZipPattern = /^\d{5}(?:-\d{4})?$/;
const skuPattern = /^[A-Z0-9][A-Z0-9._-]{1,79}$/;

export const PHONE_MESSAGE = "Phone number must contain 10 to 15 digits and may start with +.";
export const PASSWORD_MESSAGE =
  "Password must include uppercase, lowercase, number, and special character.";

export function trimmed(value: string | undefined | null) {
  return value?.trim() ?? "";
}

export function optionalText(value: string | undefined | null) {
  const clean = trimmed(value);
  return clean || undefined;
}

export function validateRequiredText(value: string, label: string) {
  return trimmed(value) ? null : `${label} is required.`;
}

export function validatePersonName(value: string, label: string) {
  const clean = trimmed(value);
  if (!clean) return `${label} is required.`;
  if (!personNamePattern.test(clean)) {
    return `${label} may contain letters, spaces, hyphens, and apostrophes only.`;
  }
  return null;
}

export function validatePhone(value: string | undefined | null) {
  const clean = trimmed(value);
  if (!clean) return null;
  const digitCount = clean.startsWith("+") ? clean.length - 1 : clean.length;
  if (!phonePattern.test(clean) || digitCount < 10 || digitCount > 15) {
    return PHONE_MESSAGE;
  }
  return null;
}

export function validatePassword(value: string) {
  if (value.length < 8) return "Password must be at least 8 characters.";
  if (!/[A-Z]/.test(value) || !/[a-z]/.test(value) || !/\d/.test(value) || !/[^A-Za-z0-9]/.test(value)) {
    return PASSWORD_MESSAGE;
  }
  return null;
}

export function validatePositiveDecimal(value: string, label: string) {
  const clean = trimmed(value);
  const numberValue = Number(clean);
  if (!clean || Number.isNaN(numberValue)) return `${label} must be a valid number.`;
  if (!Number.isFinite(numberValue) || numberValue <= 0) return `${label} must be greater than 0.`;
  return null;
}

export function validateNonNegativeDecimal(value: string, label: string) {
  const clean = trimmed(value);
  const numberValue = Number(clean);
  if (!clean || Number.isNaN(numberValue)) return `${label} must be a valid number.`;
  if (!Number.isFinite(numberValue) || numberValue < 0) return `${label} cannot be negative.`;
  return null;
}

export function validateNonNegativeInteger(value: string, label: string) {
  const clean = trimmed(value);
  const numberValue = Number(clean);
  if (!clean || !Number.isInteger(numberValue)) return `${label} must be a whole number.`;
  if (numberValue < 0) return `${label} cannot be negative.`;
  return null;
}

export function validatePositiveInteger(value: string, label: string) {
  const integerError = validateNonNegativeInteger(value, label);
  if (integerError) return integerError;
  if (Number(trimmed(value)) < 1) return `${label} must be at least 1.`;
  return null;
}

export function validatePostalCode(value: string, country = "US") {
  const clean = trimmed(value);
  if (!clean) return "Postal code is required.";
  if (country.trim().toUpperCase() === "US") {
    return usZipPattern.test(clean) ? null : "US ZIP code must be 5 digits or ZIP+4 format.";
  }
  return postalCodePattern.test(clean) ? null : "Postal code contains invalid characters.";
}

export function validateSku(value: string) {
  const clean = trimmed(value).toUpperCase();
  if (!clean) return null;
  return skuPattern.test(clean)
    ? null
    : "SKU may contain uppercase letters, numbers, dots, hyphens, and underscores.";
}

export function validateOptionalHttpUrl(value: string, label: string) {
  const clean = trimmed(value);
  if (!clean) return null;
  if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
    return `${label} must start with http:// or https://.`;
  }
  if (/\s/.test(clean)) return `${label} cannot contain whitespace.`;
  try {
    new URL(clean);
  } catch {
    return `${label} must be a valid URL.`;
  }
  return null;
}

export function validateCode(value: string, label: string) {
  const clean = trimmed(value).toUpperCase();
  if (!clean) return `${label} is required.`;
  return skuPattern.test(clean)
    ? null
    : `${label} may contain uppercase letters, numbers, dots, hyphens, and underscores.`;
}

export function firstError(...errors: Array<string | null>) {
  return errors.find((error): error is string => Boolean(error)) ?? null;
}
