# MultitechERP technical documentation

This folder is the project knowledge base: architecture, request flow, modules, Oracle mapping, and feature traces. It is the **one canonical doc tree** for this repo — not split per AI tool.

The application lives in `src/`. There is no Entity Framework table map and no DDL in the repo. Tables exist in Oracle schema **MTEX**. C# models and package parameter names are the in-repo proxy for columns.

## For AI agents

This team uses more than one AI coding tool (Claude, Cursor, Grok). The shared entry point is
[`AGENTS.md`](../AGENTS.md) at the repo root — tool-agnostic instructions that point back into
this folder and into `.agent/knowledge-graph/`. Thin per-tool pointers exist so each tool picks it up
automatically: [`CLAUDE.md`](../CLAUDE.md), [`.cursor/rules/multitech-erp.mdc`](../.cursor/rules/multitech-erp.mdc),
and the [`.claude/skills/multitech-erp-explorer/`](../.claude/skills/multitech-erp-explorer) skill.
None of them duplicate content — read `AGENTS.md` for the actual traversal steps.

## How to read this (day-1 path)

1. [01-overview.md](01-overview.md) — what the product is
2. [02-architecture.md](02-architecture.md) — layers, projects, Areas
3. [03-request-lifecycle.md](03-request-lifecycle.md) — where a request starts and what it calls
4. [04-design-patterns.md](04-design-patterns.md) — patterns that actually exist in the code
5. [05-dependencies.md](05-dependencies.md) — NuGet and runtime dependencies
6. [06-modules.md](06-modules.md) — module catalog (Area / BLL / Model / Oracle prefix)
7. [07-data-access-and-oracle.md](07-data-access-and-oracle.md) — `OraDatabase`, packages, `pOption`
8. [08-security-and-auth.md](08-security-and-auth.md) — session login vs OAuth vs menu permission
9. [09-naming-conventions.md](09-naming-conventions.md) — names you will see everywhere, plus the doc/graph ID rules
10. [10-knowledge-graph.md](10-knowledge-graph.md) — the node/edge schema behind `.agent/knowledge-graph/*.jsonl` and the AI skill
11. [11-frontend-patterns.md](11-frontend-patterns.md) — AngularJS/UI-Bootstrap/Kendo Grid conventions, audited against management's 3 reference guides, with a "how to build a new page's frontend" recipe
12. [CONTRIBUTING.md](CONTRIBUTING.md) — how to write new feature/schema docs so they stay graph-compatible

Worked examples:

- [features/security-signin.md](features/security-signin.md)
- [features/merchandising-buyer.md](features/merchandising-buyer.md)
- [features/_template.md](features/_template.md) — copy this for the next screen you explore

Schema (partial; grow per table):

- [schema/_conventions.md](schema/_conventions.md)
- [schema/MC_BUYER.md](schema/MC_BUYER.md)
- [schema/HR_DEPARTMENT.md](schema/HR_DEPARTMENT.md)

Graph (generated — do not hand-edit, see [10-knowledge-graph.md](10-knowledge-graph.md)):

- `.agent/knowledge-graph/nodes.jsonl`, `.agent/knowledge-graph/edges.jsonl` — regenerate with `python .agent/knowledge-graph/harvest_graph.py`
- Consumed by the `.claude/skills/multitech-erp-explorer/` skill

## Documentation structure

Keep **stable IDs** so the knowledge graph can ingest files without rewriting them — full rules
in [CONTRIBUTING.md](CONTRIBUTING.md) and [09-naming-conventions.md](09-naming-conventions.md#doc--graph-id-rules).

```
docs/
  README.md                          # this index
  CONTRIBUTING.md                    # how to write new docs so they stay graph-compatible
  01-overview.md
  02-architecture.md
  03-request-lifecycle.md
  04-design-patterns.md
  05-dependencies.md
  06-modules.md
  07-data-access-and-oracle.md
  08-security-and-auth.md
  09-naming-conventions.md
  10-knowledge-graph.md
  features/
    _template.md
    {module}-{feature}.md            # one file per screen / API use-case
  schema/
    _conventions.md
    {TABLE_NAME}.md                  # one file per Oracle table
  packages/
    {PKG_NAME}.md                    # optional: one file per Oracle package (later)
  api/
    {route-prefix}.md                # optional: route catalog (later)

.agent/knowledge-graph/              # machine-facing graph artifacts, not docs content
  nodes.jsonl, edges.jsonl           # generated — see harvest_graph.py
  harvest_graph.py
```

### What belongs where

| Layer | File | One sentence |
|---|---|---|
| Product | `01-overview.md` | Garment ERP: merch → knit → dye → cut → sew → ship, plus HR/commercial/inventory |
| Code shape | `02-architecture.md` | ASP.NET MVC 5 + Web API 2 + AngularJS 1.3 + Autofac + Oracle packages |
| Runtime | `03-request-lifecycle.md` | Browser → Area MVC page → Angular `$http` → Web API → BLL → `OraDatabase` → `PKG_*.proc` |
| Domain | `06-modules.md` | One row per Area |
| Data | `schema/{TABLE}.md` | Columns, PK/FK, header/detail, who writes it |
| Behavior | `features/{id}.md` | URL, controller, service, package, `pOption`, tables, session keys |
| AI | `10-knowledge-graph.md` | Node/edge types for a later skill |

### What is *not* in the repo

- Table DDL, views, sequences, indexes, triggers
- Official ERD or data dictionary
- Accounting MVC Area (packages exist: `PKG_ACC_*`)

To complete column-accurate schema docs you need a dump from live Oracle (`ALL_TAB_COLUMNS`, `ALL_CONSTRAINTS`) and then join it to `*Model.cs`.

## Coverage of this first pass

**Done:** architecture, request pipeline, patterns, dependencies, module catalog, Oracle call convention, auth, two full feature traces, two sample tables, knowledge-graph plan.

**Not done (too large for day 1; hundreds of services):** every API, every table/column, every `pOption` branch. Use the feature template as you explore each screen.

## Source of truth

| Question | Look here |
|---|---|
| How is the web app started? | `src/ERPSolution/Global.asax.cs`, `Startup.cs` |
| How is DI wired? | `src/ERPSolution/App_Start/IocConfig.cs` |
| How is Oracle called? | `src/ERP.DAL/OraDatabase.cs` |
| What packages exist? | `src/ERPSolution/oracle/packages/` |
| What tables look like? | `src/ERP.Model/**` properties + live MTEX |
| What a screen does | Area `Views` + `Client/app/*.js` + `Api/*Controller.cs` |
