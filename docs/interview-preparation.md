# Interview Preparation

## 100 Likely Questions and Answers

1. Q: What is Atlas Commerce Platform?
   A: It is a full-stack enterprise marketplace with customer shopping, seller operations, admin governance, PostgreSQL persistence, Docker deployment, and automated tests.

2. Q: What architecture pattern does the backend follow?
   A: Router -> Service -> Repository -> Database. Routers handle HTTP, services handle business rules, repositories/data queries handle persistence.

3. Q: Why use FastAPI for this project?
   A: FastAPI provides strong typing, dependency injection, Pydantic validation, OpenAPI docs, high performance, and clean REST endpoint definitions.

4. Q: Why use React with TypeScript?
   A: React supports component-based UI and TypeScript adds compile-time safety for API contracts, props, and form state.

5. Q: How does the frontend communicate with the backend?
   A: Pages call service functions, service functions use a shared Axios client, and React Query manages loading, caching, mutations, and invalidation.

6. Q: What is the persistence layer?
   A: PostgreSQL is the database, SQLAlchemy 2 is the ORM, and Alembic manages migrations.

7. Q: How is authentication implemented?
   A: Users login with email/password, passwords are hashed with Passlib, backend issues JWT access tokens and persisted refresh tokens.

8. Q: What is refresh-token rotation?
   A: Each refresh request revokes the old refresh token and issues a new refresh token, reducing replay risk.

9. Q: Where are refresh tokens stored?
   A: Only refresh token hashes are persisted in the `refresh_tokens` table.

10. Q: What is RBAC?
    A: Role-based access control. Atlas uses persisted roles such as `customer` and `admin`, with FastAPI dependencies enforcing role requirements.

11. Q: How are admin endpoints protected?
    A: They use `require_roles(UserRole.ADMIN)` so only active authenticated admin users can access them.

12. Q: How is seller authorization handled?
    A: Seller ability is tied to the authenticated user's seller profile and service-level ownership checks.

13. Q: What is the role of Pydantic schemas?
    A: They define request/response contracts, validate inputs, normalize values, and support OpenAPI schema generation.

14. Q: How are validation errors returned?
    A: FastAPI returns `422 Unprocessable Entity` for schema validation failures.

15. Q: How are business rule errors returned?
    A: Services raise standardized HTTP exceptions such as bad request, unauthorized, forbidden, or not found.

16. Q: How is phone validation handled?
    A: Backend validation accepts optional leading `+` and numeric digits only, with configurable default length of 10-15 digits.

17. Q: How is password strength validated?
    A: Passwords require minimum length plus uppercase, lowercase, number, and special character checks.

18. Q: How does product search work?
    A: `GET /api/catalog/products` accepts search, category, seller, price, page, and page size filters and returns a paged response.

19. Q: What happens with empty search text?
    A: Search input is trimmed; an empty string is treated as no search filter.

20. Q: How is product inventory represented?
    A: `inventory_items` track quantity, reserved quantity, reorder level, product, variant, and warehouse.

21. Q: How is stock validated?
    A: `POST /api/inventory/validate` checks requested quantity against available inventory.

22. Q: What is a product variant?
    A: A sellable variation of a product with SKU, name, price delta, attributes, and active flag.

23. Q: How is SKU uniqueness enforced?
    A: Product variant `sku` has a unique database index and schemas validate SKU format.

24. Q: What is the cart uniqueness rule?
    A: A user can have only one cart row for the same product and variant combination.

25. Q: What is the wishlist uniqueness rule?
    A: A user can have only one wishlist row for the same product and variant combination.

26. Q: How are order totals calculated?
    A: The order service calculates subtotal, tax, shipping charge, discount, and total during checkout.

27. Q: Why snapshot product information in order items?
    A: Order items keep product name, variant name, SKU, unit price, and line total so historical orders remain stable even if products change.

28. Q: What order statuses are supported?
    A: Pending, confirmed, packed, shipped, delivered, cancelled, and refunded.

29. Q: What payment integration exists?
    A: A sandbox payment transaction module exists; it persists payment records but does not call a real payment gateway.

30. Q: What notification capability exists?
    A: Notifications are persisted in the database for order, seller, admin, and payment types; no external delivery service is integrated.

31. Q: What AI functionality exists?
    A: Internal deterministic admin helpers for recommendations, product descriptions, and review summaries. No external AI provider is integrated.

32. Q: Why document AI as internal helpers?
    A: Because the code generates responses from local data/rules and does not call OpenAI, Claude, Gemini, LangChain, RAG, or a vector database.

33. Q: What is the purpose of the admin dashboard?
    A: It shows platform metrics such as customers, sellers, products, categories, orders, revenue, pending moderation, inventory alerts, top products, and top sellers.

34. Q: How does admin user management work?
    A: Admins can list/search users, activate or suspend users, and soft-delete users by marking them inactive.

35. Q: How does seller moderation work?
    A: Admins set seller moderation status to approved, rejected, or suspended; the service updates seller active state accordingly.

36. Q: How does product moderation work?
    A: Admins can update product status, visibility, featured flag, and brand.

37. Q: What reporting formats are supported?
    A: JSON reports, CSV reports, and PDF-placeholder bytes.

38. Q: What are examples of report names?
    A: Sales, inventory, sellers, and default user-style reports for other names.

39. Q: What is an audit log?
    A: A persisted record of admin actions, including actor, action, entity type, entity id, and metadata.

40. Q: What is Alembic used for?
    A: Alembic manages database schema migrations and validates schema evolution in CI.

41. Q: How does SQLAlchemy help?
    A: It maps Python models to database tables and provides sessions, relationships, transactions, and query composition.

42. Q: What is a SQLAlchemy session?
    A: A unit-of-work object used to query, add, update, delete, commit, and refresh ORM objects.

43. Q: Why use PostgreSQL instead of only SQLite?
    A: PostgreSQL provides production-grade relational behavior, constraints, concurrency, and deployment suitability.

44. Q: Why might tests use SQLite?
    A: SQLite can provide fast isolated tests, but CI and production should still validate PostgreSQL-oriented migrations/behavior.

45. Q: What is Docker Compose used for?
    A: It runs PostgreSQL, backend, and frontend together for local demo and integration validation.

46. Q: What services are in Compose?
    A: `db`, `backend`, and `frontend`.

47. Q: What ports are exposed locally?
    A: Frontend on `3000` and backend on `8001`.

48. Q: What is the health endpoint?
    A: `GET /health` returns a basic success payload indicating backend availability.

49. Q: How are frontend assets served in Docker?
    A: The React app is built with Vite and served by Nginx.

50. Q: How is the backend served in Docker?
    A: The backend container runs the FastAPI application, typically through Uvicorn startup.

51. Q: What does frontend CI run?
    A: npm install/ci, TypeScript lint/typecheck, production build, Playwright browser tests.

52. Q: What does backend CI run?
    A: dependency install, compileall, Ruff, Alembic upgrade validation, and Pytest.

53. Q: What does Playwright test?
    A: Browser journeys such as auth/profile and marketplace checkout/order flows.

54. Q: What does Pytest test?
    A: Backend APIs including auth/customer validation, marketplace shopping, and admin enterprise features.

55. Q: What is the benefit of React Query?
    A: It standardizes server state, loading states, caching, mutation handling, and cache invalidation.

56. Q: What is the benefit of Axios service modules?
    A: They centralize API calls and keep route components cleaner.

57. Q: How are protected frontend routes implemented?
    A: Protected route wrappers check auth state and redirect unauthenticated users to login.

58. Q: What is CORS?
    A: Cross-Origin Resource Sharing; the backend config allows configured frontend origins to call APIs.

59. Q: Why are environment variables important?
    A: They separate deployment-specific values like database URL, JWT secret, token lifetimes, phone length, and CORS origins.

60. Q: What should change for production secrets?
    A: Replace default JWT and database secrets with values from a secure secret manager.

61. Q: How is duplicate email handled?
    A: The user table has a unique email constraint and auth service checks for existing users.

62. Q: How is duplicate SKU handled?
    A: Payload-level duplicate variants are rejected and the database enforces unique SKU globally.

63. Q: How is duplicate coupon handled?
    A: Coupon code has a unique database index.

64. Q: How does checkout ensure address ownership?
    A: The order service validates that the selected shipping address belongs to the authenticated user.

65. Q: How are product slugs generated?
    A: A slug utility converts names/store names/categories into URL-friendly slug values.

66. Q: What is the purpose of `is_visible` on products?
    A: It allows admin or seller workflows to hide products from customer-facing catalog views.

67. Q: What is the purpose of `is_featured` on products?
    A: It marks products for promotional or dashboard presentation.

68. Q: What is the purpose of `moderation_status` on sellers?
    A: It tracks pending, approved, rejected, or suspended seller governance state.

69. Q: How are low-stock alerts calculated?
    A: Inventory items where quantity is less than or equal to reorder level count as alerts.

70. Q: What is the difference between cart and order?
    A: Cart is mutable purchase intent; order is the persisted checkout result with immutable line snapshots.

71. Q: What is the difference between access and refresh tokens?
    A: Access tokens authorize API calls and are short-lived; refresh tokens obtain new token pairs and are persisted/revoked.

72. Q: Why should access tokens be short-lived?
    A: Short lifetimes reduce risk if a token is exposed.

73. Q: How does logout work?
    A: The backend revokes the submitted refresh token so it cannot be used again.

74. Q: What happens if a user is inactive?
    A: Authentication dependencies reject inactive users.

75. Q: What is the OpenAPI benefit?
    A: FastAPI generates interactive API documentation and schemas at `/docs`.

76. Q: What is a Pydantic response model?
    A: A schema that controls response serialization and documents output shape.

77. Q: How does the app prevent SQL injection?
    A: SQLAlchemy parameterized queries and ORM query construction avoid manual SQL string interpolation.

78. Q: How does the app reduce XSS risk?
    A: React escapes rendered text by default, and backend validation trims/sanitizes text inputs.

79. Q: What is an example of service-layer ownership enforcement?
    A: Users can update only their own addresses, cart items, wishlist items, orders, seller products, and inventory.

80. Q: What is an example of business validation?
    A: Minimum price cannot exceed maximum price in product search.

81. Q: What is an example of model-level integrity?
    A: `inventory_items` has a unique constraint across product, variant, and warehouse.

82. Q: What is the purpose of `billing_address` as JSON?
    A: It snapshots billing details at checkout without requiring a separate billing address table.

83. Q: What is the purpose of `raw_response` on payments?
    A: It stores sandbox provider response metadata and can later support real provider responses.

84. Q: What are the main customer pages?
    A: Dashboard, profile, wishlist, cart, checkout, orders, and order detail.

85. Q: What are the main seller pages?
    A: Seller dashboard and seller product/inventory management areas.

86. Q: What are the main admin tabs?
    A: Overview, Users, Sellers, Products, Orders, Reviews, Reports, Notifications, Payments, and AI.

87. Q: What does the product details page show?
    A: Image, category, name, seller, price, description, stock, variants, wishlist/cart actions, and admin-only AI helpers where authorized.

88. Q: What is a demo-data seed script?
    A: An idempotent script that creates realistic users, sellers, categories, products, orders, reviews, notifications, and admin demo data.

89. Q: Why must seed scripts be idempotent?
    A: So repeated runs do not create duplicate records or corrupt demo data.

90. Q: What is the purpose of empty states?
    A: They communicate that data is absent and guide users without implying an error.

91. Q: What is the purpose of loading states?
    A: They show that API requests are in progress and improve perceived reliability.

92. Q: What should be disclosed during a demo?
    A: Payments are sandbox-only, notifications are persisted only, and AI helpers are internal deterministic endpoints.

93. Q: What should be improved before real production?
    A: Secret management, stricter authorization review, real payments, real notification delivery, monitoring, backups, and performance testing.

94. Q: Why use migrations instead of manual database changes?
    A: Migrations provide repeatable, versioned schema changes across environments.

95. Q: Why split backend and frontend CI?
    A: It keeps concerns independent, makes failures easier to diagnose, and allows language-specific tooling.

96. Q: What is a common cause of Docker startup failure?
    A: Database health, port conflicts, invalid environment variables, or image build errors.

97. Q: How would you debug a failed API call from the UI?
    A: Check browser network tab, API response body/status, backend logs, Axios service, route auth, and database state.

98. Q: How would you add a new marketplace feature safely?
    A: Add schema, model/migration if needed, repository/service logic, router endpoint, frontend service/page integration, and tests.

99. Q: How would you protect a new admin endpoint?
    A: Add `require_roles(UserRole.ADMIN)` dependency and service-level validation/audit logging.

100. Q: Is Atlas Commerce Platform ready for external production traffic as-is?
     A: It is a strong enterprise demo/foundation, but production should add real secrets, managed infrastructure, monitoring, stricter authorization review, real payment/notification integrations, backups, and performance/security testing.
