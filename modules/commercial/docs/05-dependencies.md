# 05 — Dependencies

All projects target **.NET Framework 4.8**. Packages are NuGet `packages.config` (not SDK-style).

## Project references

```
ERPSolution  →  ERP.BLL, ERP.DAL, ERP.Model
ERP.BLL      →  ERP.DAL, ERP.Model
ERP.Model    →  ERP.DAL
ERP.DAL      →  (none)
```

## Runtime platform

| Dependency | Version (web) | Role |
|---|---|---|
| ASP.NET MVC | 5.2.3 | HTML pages |
| ASP.NET Web API | 5.3.0 | JSON APIs |
| Microsoft.Owin + OAuth | 3.0–4.2 | `/token`, bearer, CORS |
| Autofac + Mvc5 + WebApi2 | 8.0 / 6.1 | DI |
| Oracle.ManagedDataAccess | 19.21 (DAL) | ADO.NET |
| Newtonsoft.Json | 13.0.1 | JSON |
| AngularJS | 1.3.8 | Browser UI |
| jQuery | 1.10.2 | Scripts |
| Bootstrap | 3.0.0 | CSS |
| Microsoft.AspNet.SignalR | 2.2.0 | Realtime dashboard |
| Microsoft ReportViewer | 140.340.80 | RDLC |
| Crystal Reports | project files `*.rpt` | Older reports |

## Data / files / documents

| Package | Project | Role |
|---|---|---|
| Oracle.ManagedDataAccess | DAL | Stored procedures |
| EntityFramework 6 + Oracle EF | DAL | **Referenced, unused in source** |
| AWSSDK.S3 | Web | Optional document store |
| ClosedXML | BLL | Excel |
| PDFsharp / MigraDoc / HtmlRenderer | BLL, DAL, Web | PDF |
| Codaxy.WkHtmlToPdf | Web | HTML → PDF |

## Jobs / mail

| Package | Status in this tree |
|---|---|
| Hangfire + Hangfire.SqlServer 1.5.1 | Referenced; some `BackgroundJob.Enqueue`; **not piped in `Startup`** |
| FluentScheduler 5.0 | `SchedulerRegistry` + `TnATaskSummaryMailJob`; **not initialized** |
| Postal.Mvc5 + RazorEngine | Email templates |

## Why this matters

- New code should use **Autofac + BLL + OraDatabase**, not EF.
- Hangfire/FluentScheduler are **not a reliable job platform** until someone wires `Startup`.
- AngularJS 1.3 is the UI contract; there is no React/Vue app in `src`.
- Oracle client is **Managed** ODP.NET (`Oracle.ManagedDataAccess.Client` in `Web.config`).

## Oracle compile scripts

`src/ERPSolution/oracle/db_compile.bat` and `package_deploy.bat` compile packages into schema user `mtex`. Treat `oracle/packages/*.sql` as the API surface of the database.

## Config dependencies (no secrets)

Document names only. Values stay in `Web.config` / environment.

- `connectionStrings`: `ConnectionString`, `ConnectionStringDr`
- `appSettings`: `DEFAULT_SCHEMA`, `StorageProvider`, deployment version constants
