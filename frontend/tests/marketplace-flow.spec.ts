import { expect, request, test } from "@playwright/test";

const backendUrl = "http://127.0.0.1:8010";

test("login, browse, wishlist, cart, checkout, order history, logout", async ({ page }) => {
  const api = await request.newContext({ baseURL: backendUrl });
  const stamp = Date.now();
  const email = `market-${stamp}@example.com`;
  const password = "S3curePass!";
  const productName = `Trail Pack ${stamp}`;

  await api.post("/api/auth/register", {
    data: {
      email,
      password,
      first_name: "Market",
      last_name: "Buyer",
    },
  });
  const login = await api.post("/api/auth/login", { data: { email, password } });
  const tokens = await login.json();
  const headers = { Authorization: `Bearer ${tokens.access_token}` };

  const category = await api.post("/api/catalog/categories", {
    headers,
    data: { name: `Packs ${stamp}`, description: "Travel packs" },
  });
  const categoryPayload = await category.json();

  await api.post("/api/seller/profile", {
    headers,
    data: { store_name: `Atlas Gear ${stamp}`, description: "Trail goods" },
  });

  const product = await api.post("/api/seller/products", {
    headers,
    data: {
      category_id: categoryPayload.id,
      name: productName,
      description: "Durable pack with validated inventory",
      base_price: 64.5,
      status: "active",
      images: [
        {
          url: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
          alt_text: productName,
          is_primary: true,
        },
      ],
      variants: [],
    },
  });
  const productPayload = await product.json();

  const warehouse = await api.post("/api/inventory/warehouses", {
    headers,
    data: {
      name: `Warehouse ${stamp}`,
      code: `WH-${stamp}`,
      city: "Austin",
      state: "TX",
      country: "US",
    },
  });
  const warehousePayload = await warehouse.json();

  await api.post("/api/inventory/stock", {
    headers,
    data: {
      product_id: productPayload.id,
      warehouse_id: warehousePayload.id,
      quantity: 8,
      reserved_quantity: 0,
      reorder_level: 1,
    },
  });

  await api.post("/api/customer/addresses", {
    headers,
    data: {
      label: "Home",
      recipient_name: "Market Buyer",
      line1: "101 Commerce Street",
      city: "Austin",
      state: "TX",
      postal_code: "78701",
      country: "US",
      is_default_shipping: true,
    },
  });

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Login" }).click();
  await expect(page.getByRole("heading", { name: /Welcome, Market/ })).toBeVisible();

  await page.getByRole("link", { name: "Categories" }).click();
  await expect(page.getByRole("heading", { name: "Categories" })).toBeVisible();
  await page.getByRole("link", { name: categoryPayload.name }).click();

  await page.getByPlaceholder("Search products").fill(productName);
  await page.getByRole("button", { name: "Apply" }).click();
  await expect(page.getByText(productName)).toBeVisible();
  await page.getByRole("link", { name: productName }).last().click();

  await expect(page.getByRole("heading", { name: productName })).toBeVisible();
  await page.getByRole("button", { name: "Add to wishlist" }).click();

  await page.getByRole("link", { name: /Wishlist/ }).click();
  await expect(page.getByText(productName)).toBeVisible();
  await page.getByRole("button", { name: "Move to cart" }).click();

  await page.getByRole("link", { name: /Cart/ }).click();
  await expect(page.getByText(productName)).toBeVisible();
  await page.getByRole("spinbutton").fill("2");

  await page.getByRole("link", { name: "Checkout" }).click();
  await expect(page.getByRole("heading", { name: "Checkout" })).toBeVisible();
  await page.getByRole("button", { name: "Create order" }).click();

  await expect(page.getByRole("heading", { name: "Order created" })).toBeVisible();
  await page.getByRole("link", { name: "View order history" }).click();
  await expect(page.getByRole("heading", { name: "Order history" })).toBeVisible();
  await expect(page.getByText(productName)).toBeVisible();

  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();
});
