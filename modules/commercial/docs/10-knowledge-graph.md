# 10 — Knowledge graph plan (for a later AI skill)

Goal: when you ask “how does yarn issue work?”, an agent should walk **nodes and edges**, not grep the whole tree.

This documentation is already shaped as graph seed data. Do not invent a second structure.

## Node types

Use these IDs in feature files (`id:` front-matter).

| Type | ID pattern | Example | Source |
|---|---|---|---|
| `Module` | `mod:{area}` | `mod:merchandising` | [06-modules.md](06-modules.md) |
| `AreaRoute` | `route:{area}` | `route:Merchandising/{controller}/{action}` | `*AreaRegistration.cs` |
| `MvcAction` | `mvc:{area}.{controller}.{action}` | `mvc:Security.ScUser.SignIn` | MVC controllers |
| `ApiAction` | `api:{httpmethod}:{path}` | `api:GET:api/mrc/buyer/BuyerByUserList` | `[RoutePrefix]+[Route]` |
| `Service` | `svc:{interface}` | `svc:IMC_BUYERService` | BLL |
| `ServiceMethod` | `svc:{type}.{method}` | `svc:MC_BUYERService.Save` | BLL method |
| `Model` | `model:{class}` | `model:MC_BUYERModel` | ERP.Model |
| `Table` | `tbl:{name}` | `tbl:MC_BUYER` | inferred + Oracle dump |
| `Column` | `col:{table}.{column}` | `col:MC_BUYER.BUYER_CODE` | model property / ALL_TAB_COLUMNS |
| `Package` | `pkg:{name}` | `pkg:PKG_MERCHANDISING` | `oracle/packages` |
| `Procedure` | `proc:{pkg}.{proc}` | `proc:PKG_MERCHANDISING.mc_buyer_insert` | package spec |
| `Option` | `opt:{proc}:{n}` | `opt:mc_buyer_select:3000` | BLL `pOption` |
| `SessionKey` | `sess:{name}` | `sess:multiScUserId` | login |
| `JsClient` | `js:{path}` | `js:Areas/Merchandising/Client/app/...` | Angular |
| `Report` | `rpt:{file}` | `rpt:rptExportLC.rdlc` | Area Reports |

## Edge types

| Edge | From → To | Meaning |
|---|---|---|
| `CONTAINS` | Module → ApiAction / Table | belongs to |
| `ROUTES_TO` | AreaRoute / URL → MvcAction or ApiAction | HTTP |
| `INJECTS` | ApiAction → Service | Autofac constructor |
| `CALLS` | ServiceMethod → Procedure | `ExecuteStoredProcedure` |
| `USES_OPTION` | ServiceMethod → Option | `pOption` |
| `MAPS_ROW` | ServiceMethod → Model | DataRow mapping |
| `PERSISTS` | Procedure → Table | insert/update |
| `READS` | Procedure → Table | select |
| `HAS_COLUMN` | Table → Column | schema |
| `FK_TO` | Column → Table | `*_ID` |
| `RETURNS` | ApiAction → Model | JSON body |
| `REQUIRES` | ApiAction → SessionKey / auth | |
| `UI_CALLS` | JsClient → ApiAction | `$http` |
| `UPSTREAM` / `DOWNSTREAM` | Module → Module | business flow |

## Status: implemented (minimal)

- Harvester: `.agent/knowledge-graph/harvest_graph.py` — reads `docs/features/*.md` + `docs/schema/*.md`
  front-matter, writes `.agent/knowledge-graph/{nodes,edges}.jsonl`. Run it after adding/editing a
  feature or schema file. Currently harvests `Feature`/`Table`/`Column` nodes and the
  `CONTAINS`/`CALLS`/`USES_TABLE`/`MAPS_ROW`/`REQUIRES`/`UPSTREAM`/`DOWNSTREAM`/`BELONGS_TO`/
  `MAPS_MODEL`/`HAS_PACKAGE`/`HAS_PROCEDURE`/`FK_TO` edges below — not yet the `ApiAction`/`MvcAction`/
  `JsClient` regex-harvest step (item 1, 7 below); that's still future work.
- **Column-level graph** (added 2026-09-14, ported from the sibling `MultiTechERPAccounting` repo
  after piloting there): each `docs/schema/{TABLE}.md` frontmatter can carry a `columns:` line,
  e.g. `columns: [PAYMENT_MODE_ID->ACC_PAYMENT_MODE.PAYMENT_MODE_ID, VOUCHER_MASTER_ID]` — each
  entry is either `COLUMN->TABLE.COLUMN` (a DB-verified FK) or a bare `COLUMN` (a PK, declared so
  other tables' FK edges resolve to a real node instead of dangling). FK targets outside this
  repo's documented tables (`SC_USER`, `HR_COMPANY`, `HR_OFFICE`, `HR_COUNTRY`, `LOOKUP_DATA`,
  `RF_BANK`, `RF_PAYM_TERM`, `RF_ACTN_STATUS`, `ACC_VOUCHER_TYPE`, `ACC_MAP_CLASS`,
  `ACC_GL_LINK_COA_H`) are **expected to be dangling** — those tables aren't documented in this
  repo's `docs/schema/` yet (some may only exist in the Accounting repo's own schema set).
- Skill: `.claude/skills/multitech-erp-explorer/SKILL.md` — traverses this docs tree + the graph
  files before falling back to source exploration. Restart Claude Code (or start a new session)
  for it to be picked up if it wasn't loaded when this session started.

## How to harvest (script later)

1. **API nodes:** regex `[RoutePrefix]` + `[Route]` + `[HttpGet|HttpPost]` under `Areas/*/Api`.
2. **CALLS edges:** in BLL, `string sp = "pkg_x.y"` / `const string sp`.
3. **USES_OPTION:** `pOption = N` or `Value = 1000`.
4. **MAPS_ROW:** `dr["COL"]`.
5. **Table nodes:** `class XModel` → `X` (strip `Model`); confirm with Oracle dump.
6. **FK_TO:** properties matching `^[A-Z0-9_]+_ID$` except own PK.
7. **UI_CALLS:** Angular `$http` / `.get(` / `.post(` in `Client/app`.

Store harvest as JSONL under `.agent/knowledge-graph/`, e.g. `nodes.jsonl`, `edges.jsonl`, so a Grok skill can embed or grep it.

## Skill layout (when you build it)

Built at `.claude/skills/multitech-erp-explorer/` (see status note above) — actual layout:

```
.claude/skills/multitech-erp-explorer/
  SKILL.md                 # when to use, how to traverse
  references/
    graph-schema.md        # this file's node/edge tables
```

(harvester lives at `.agent/knowledge-graph/harvest_graph.py`, next to the graph output it
writes, rather than inside the skill folder — same script either way.)

Do not dump whole `IocConfig.cs` into the skill. Point at the graph.

## Feature file as a graph record

Every `docs/features/*.md` should start with:

```yaml
---
id: feat:mrc-buyer-save
module: merchandising
http: POST /api/mrc/buyer/Save
mvc: null
api: BuyerApiController.Save
service: MC_BUYERService.Save
procedure: PKG_MERCHANDISING.mc_buyer_insert
pOption: 1000
tables: [MC_BUYER]
models: [MC_BUYERModel]
session: [multiScUserId]
status: verified
---
```

That YAML **is** the node. The rest of the markdown is human explanation.

## Coverage strategy

Do **not** generate 2000 empty schema files. Order:

1. Keep architecture docs current (done).
2. Add a feature file every time you learn a screen (template).
3. Add schema files for tables you actually touch.
4. After DB access, batch-import `ALL_TAB_COLUMNS` into `docs/schema/`.
5. Then run harvest for CALLS/ROUTES edges.

## Relation to existing explore-codebase skill

A code-review graph (callers/callees at function level) is complementary. This ERP graph is **business-shaped** (screen → package → table). An agent should use both: function graph for “who calls this C# method”, this graph for “which Oracle table and pOption”.
