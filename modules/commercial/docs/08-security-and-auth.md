# 08 — Security and authentication

Three mechanisms exist. The main UI uses **session**. APIs used by Angular after login also use that session (session is enabled on Web API). Token and header auth are extra.

## 1. Browser sign-in (primary)

| Item | Value |
|---|---|
| URL | `GET/POST /Security/ScUser/SignIn` |
| Controller | `src/ERPSolution/Areas/Security/Controllers/ScUserController.cs` |
| Service | `IScUserService` / `ScUserService` |
| Package | `pkg_security.sc_user_select` |
| Password | SHA256(UTF8(password + LOGIN_ID.ToUpper())) then Base64 |
| CAPTCHA | compared to `Session["multiCaptcha"]` |

On success the controller writes many `Session` keys, fetches an OAuth token via `getOauthToken`, clears user cache, then redirects to Home (or memorable-word flow if `IS_PWD_CNG_LOGON` is not `Y`).

Important session keys:

| Key | Meaning |
|---|---|
| `multiScUserId` | `SC_USER_ID` — used as “current user” almost everywhere |
| `multiLoginEmpId` | `HR_EMPLOYEE_ID` |
| `multiLoginEmpCompId` | company |
| `multiLoginDeptId` | department |
| `scRoleId` | role |
| `access_token` | OAuth token string stored in session |
| `multiLoginId` | login id |

Full trace: [features/security-signin.md](features/security-signin.md).

There is **no** `<authentication mode="Forms">` in `Web.config`. Session timeout is 14400 minutes.

## 2. MVC gate: `[SignInCheck]` + menu

`SignInCheckAttribute` (`src/ERPSolution/Common/SignInCheckAttribute.cs`):

- MVC `ActionFilterAttribute`, **not** global (`FilterConfig` only has `HandleErrorAttribute`)
- Applied per controller/action (e.g. `HomeController`, many Area MVC controllers)
- If `Session["multiLoginId"]` is empty → redirect `/Security/ScUser/SignIn`

`BaseController.IsMenuPermission()` (second gate, also not global):

- Reads route `controller` + `action`
- `ScUserId` from `Session["multiScUserId"]`
- `ScMenuModel.checkMenuPermission(...)`
- User id `1` is treated as always allowed

Do not assume every URL is locked.

## 3. OAuth resource owner (`/token`)

`Startup.ConfigureOAuth`:

- Path: `/token`
- Expiry: 1 day
- Provider: `SimpleAuthorizationServerProvider`
- Same password hash as MVC login
- Uses `ScUserPlainService().SignIn` (not Autofac)
- Puts `SC_USER_ID`, `USER_NAME_EN`, `USER_EMAIL` in token properties
- `AllowInsecureHttp = true`

Bearer middleware is registered. `_Layout.cshtml` injects `access_token` into Angular; data services send `Authorization: Bearer`. **Coverage is uneven:** many APIs have no `[Authorize]` and still work via session cookie. Garments and `DocumentsController` are examples that do use `[Authorize]`.

OAuth login path uses `new ScUserPlainService()` (not Autofac).

## 4. External header gate

`src/ERPSolution/Common/ExternalReqAuthorizeAttribute.cs`

- **Live use:** `[ExternalReqAuthorize]` on `ExternalApiController` (`api/ext`)
- Checks request header `_security_code`
- On failure: HTTP 403 `"Sorry!!! No Valid Security Code"`
- Also added to the **unused** OWIN `HttpConfiguration` in `Startup` — that does not apply to Global Web API

The shared secret is hardcoded. **Do not copy it into documentation.** Rotate it if `api/ext` is public.

## 5. CORS

`Startup`: `app.UseCors(CorsOptions.AllowAll)` and `config.EnableCors()`. Commented origin lists exist in `WebApiConfig`.

## 6. Security tables (convention)

| Table (inferred) | Model | Role |
|---|---|---|
| `SC_USER` | `ScUserModel` | Login account, link to `HR_EMPLOYEE_ID` |
| `SC_MENU` | `ScMenuModel` | Menu tree / URLs |
| `SC_ROLE` | `ScRoleModel` | Roles (legacy Active Record save on some models) |
| mapping tables | `SC_MAP_*` | user–buyer, user–floor, defect type, etc. |

Package: `PKG_SECURITY`, `PKG_MENU`.

## 7. What to do when adding an API

1. Prefer constructor-injected BLL (not `new` of services). `CoreContext` in `Infrastructure/Dependency` is unused.
2. MVC page: `[SignInCheck]` + `IsMenuPermission` as peers do.
3. JSON API: decide session-only vs `[Authorize]` bearer vs `[ExternalReqAuthorize]`.
4. Register new services in `IocConfig`, not `CoreContext`.
5. Never log raw passwords; hash is already `PASSWORD_HASH`.
