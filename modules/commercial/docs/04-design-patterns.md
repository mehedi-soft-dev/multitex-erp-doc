# 04 — Design patterns (as implemented)

This codebase is a **classic n-tier ERP with a stored-procedure façade**, not DDD. Patterns below are what the code actually does.

## Used

| Pattern | Where | Notes |
|---|---|---|
| **Layered architecture** | ERPSolution / BLL / Model / DAL | Layers leak: Model references DAL; BLL talks to Oracle |
| **MVC** | `Areas/*/Controllers`, `Views` | Page shells |
| **Web API resource controllers** | `Areas/*/Api` | Attribute routing |
| **SPA fragment** | AngularJS 1.3 under `Client/app` | Per-area, not a single modern SPA |
| **Service layer** | `IXxxService` / `XxxService` | One class per table or use-case |
| **Dependency injection** | Autofac in `IocConfig.cs` | Constructor injection, `InstancePerRequest` |
| **DTO / anemic model** | `{TABLE}Model` | Data + DataAnnotations; little behavior |
| **Stored-procedure wrapper** | `OraDatabase` | Single gateway to Oracle |
| **Façade (thin)** | BLL methods | Name the package, set `pOption`, map rows |
| **Strategy + factory** | `IFileStorageService` | Local vs S3 from `StorageProvider` |
| **Provider** | `IERPEmailProvider`, `IWebCacheProvider` | |
| **Hub / observer** | SignalR `DashBoardHub` | Notifications / dashboard |
| **Header–detail** | `*_H` / `*_D` tables and models | Nested `items` lists on header models |
| **Option dispatcher** | `pOption` on every package proc | Switchboard instead of many methods |
| **Active Record (legacy)** | Some Security models | `new OraDatabase()` inside model `Save()` |
| **Filter object** | `ERP.DAL.Filters` (`BaseSearchFilter`) | Paging / search bags |

## Weak or unused (do not assume they exist)

| Pattern | Status |
|---|---|
| **Repository** | Only documents (`IDocumentRepository`) |
| **Unit of Work / ambient transaction** | No; one connection per SP |
| **EF / generic repository** | Packages referenced; **no `DbContext` in source** |
| **Domain model / aggregates** | No |
| **CQRS** | No; same service does read and write |
| **Mediator** | No |
| **Specification** | No |
| **Hangfire recurring jobs** | Package present; `UseHangfire` not in `Startup` |
| **FluentScheduler** | `SchedulerRegistry` exists; `JobManager.Initialize` not called |

## Recurring code template (BLL)

Almost every service method is this algorithm:

1. Choose package procedure name (`pkg_merchandising.mc_buyer_insert`).
2. Build `List<CommandParameter>` with `p{Column}` + `pOption` + `pMsg`.
3. `ds = db.ExecuteStoredProcedure(...)`.
4. **Write:** walk `ds.Tables["OUTPARAM"]` and concatenate a JSON string.
5. **Read:** walk `ds.Tables[0].Rows`, `Convert.ToInt64` / `ToString` into a model.

That is the **Transaction Script** pattern (Fowler), with scripts in C# and rules in Oracle.

## Header / detail

Physical design:

- `MC_ORDER_H` header, `MC_ORDER_D` / related children
- `KNT_YRN_ISS_H` / `KNT_YRN_ISS_D`
- `HR_SAL_TRAN_H` / `HR_SAL_TRAN_D`

C# header models often expose `public List<ChildModel> items`. Save methods send XML or child collections into the package (`pXML` appears on some models).

## IoC registration style

`IocConfig.cs` is a **manual catalog**, not assembly scanning of BLL. New service = new `builder.RegisterType<X>().As<IX>().InstancePerRequest()`.

Exception: `IFileStorageService` is a lambda factory.

## Caching

`WebCacheProvider` wraps `HttpContext.Cache`. Keys are often user-scoped (`{key}::{multiScUserId}`). Login and logout call `_cacheProvider.Remove()`.

## Reports

RDLC + typed DataSets sit beside Areas. Controllers fill DataTables from BLL/Oracle, then ReportViewer. Separate from the JSON API path.

## How to name a change

When you add a screen, the existing pattern is:

1. Oracle package procedure (+ `pOption` branch)
2. `{TABLE}Model`
3. `I{TABLE}Service` / `{TABLE}Service`
4. Autofac line
5. Web API action under the Area
6. Angular client
7. Optional MVC Index view
