import { expect, test } from "@playwright/test";

test("landing to register, login, profile update, and logout", async ({ page }) => {
  const email = `customer-${Date.now()}@example.com`;

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Atlas Commerce Platform" })).toBeVisible();

  await page.getByRole("link", { name: /Create account/i }).first().click();
  await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();

  await page.getByLabel("First name").fill("Jordan");
  await page.getByLabel("Last name").fill("Morgan");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("S3curePass!");
  await page.getByLabel("Phone").fill("phone-number");
  await page.getByRole("button", { name: "Register" }).click();
  await expect(page.getByText("Phone number must contain 10 to 15 digits")).toBeVisible();
  await page.getByLabel("Phone").fill("5550123456");
  await page.getByRole("button", { name: "Register" }).click();

  await expect(page.getByRole("heading", { name: "Select Login Type" })).toBeVisible();
  await expect(page.getByText("Account created. Sign in to continue.")).toBeVisible();
  await page.getByRole("button", { name: "Continue as Customer" }).click();
  await expect(page.getByRole("heading", { name: "Customer Login", exact: true })).toBeVisible();

  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("S3curePass!");
  await page.getByRole("button", { name: "Login", exact: true }).click();

  await expect(page.getByRole("heading", { name: /Welcome, Jordan/ })).toBeVisible();
  await page.getByRole("main").getByRole("link", { name: "Profile" }).click();

  await expect(page.getByRole("heading", { name: "Customer profile" })).toBeVisible();
  await page.getByLabel("First name").fill("Jordyn");
  await page.getByLabel("Phone").fill("5550198000");
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByText("Profile updated.")).toBeVisible();

  await page.getByLabel("Label").fill("Home");
  await page.getByLabel("Recipient").fill("Jordyn Morgan");
  await page.getByLabel("Address line 1").fill("41 Commerce Way");
  await page.getByLabel("City").fill("Denver");
  await page.getByLabel("State").fill("CO");
  await page.getByLabel("Postal code").fill("80202");
  await page.getByRole("button", { name: /Save address/i }).click();
  await expect(page.getByText("Address saved.")).toBeVisible();
  await expect(page.getByText("Home")).toBeVisible();

  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page.getByRole("heading", { name: "Select Login Type" })).toBeVisible();
});
