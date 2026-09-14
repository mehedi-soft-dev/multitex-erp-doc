# Contributing to these docs (structure & style)

Goal: every doc file you write should double as **graph seed data**, so an AI agent can traverse
nodes/edges instead of grepping ~1700 BLL files cold.

[10-knowledge-graph.md](10-knowledge-graph.md) defines the node/edge schema and the feature-file
YAML front-matter format. Adopt it as-is — don't invent a second schema. What follows is the
*process and style* around it: how to keep writing docs so that schema stays true.

## 1. Folder shape

```
docs/
  README.md                # index + "day-1 path"
  CONTRIBUTING.md           # this file
  01-overview.md .. 09-naming-conventions.md   # stable architecture facts, rarely change
  10-knowledge-graph.md    # node/edge schema — the contract for everything below
  features/
    _template.md
    {module}-{feature}.md  # one per screen / API use-case, YAML front-matter + prose
  schema/
    _conventions.md
    {TABLE_NAME}.md         # one per Oracle table actually touched
  packages/                # optional, later: one per Oracle package
  api/                      # optional, later: route catalog

.agent/knowledge-graph/     # machine-facing graph artifacts, not docs content
  nodes.jsonl               # harvested, not hand-written
  edges.jsonl
  harvest_graph.py
```

## 2. Two kinds of file — treat them differently

**Reference docs (`01`–`09`, `_conventions.md`)** — describe things that are true for the whole
system (a layer, a convention, a pattern). Write these once, update only when the *shape* of the
system changes (new layer, new auth mechanism). Cite `file:line` for every non-obvious claim.

**Instance docs (`features/*`, `schema/*`)** — describe one screen or one table. These grow
continuously, one file per thing you actually explored. Never write these speculatively for
things you haven't opened — an empty/guessed file is worse than a missing one, because the
knowledge graph will treat its presence as "documented."

## 3. Every instance doc starts with YAML front-matter — that front-matter *is* the graph node

Use [10-knowledge-graph.md](10-knowledge-graph.md)'s node/edge tables verbatim (`mod:`, `route:`,
`mvc:`, `api:`, `svc:`, `model:`, `tbl:`, `col:`, `pkg:`, `proc:`, `opt:`, `sess:`, `js:`, `rpt:`).
Example for a feature file:

```yaml
---
id: feat:mrc-buyer-save
module: merchandising
http: POST /api/mrc/buyer/Save
api: BuyerApiController.Save
service: MC_BUYERService.Save
procedure: PKG_MERCHANDISING.mc_buyer_insert
pOption: 1000
tables: [MC_BUYER]
models: [MC_BUYERModel]
session: [multiScUserId]
status: verified   # verified | inferred — be honest when you didn't confirm against a running system
---
```

Rules:
- Every ID segment (`{module}`, `{TABLE}`, `{PKG}`, `{ClassName}`, ...) must be an exact
  code-derived term, not an invented abbreviation — see
  [09-naming-conventions.md](09-naming-conventions.md#doc--graph-id-rules) for the vocabulary
  table and which existing doc is the source of truth for each concept.
- `status: inferred` for anything read from code but not confirmed by running it or querying
  Oracle (e.g., a table's columns taken only from a `Model.cs` file, not `ALL_TAB_COLUMNS`).
- IDs are permanent once assigned — a knowledge-graph ingester keys on `id:`, so renaming it
  later orphans old edges. If a feature is reworked, keep the id and update the body.
- One `id:` per file. If a file legitimately covers two API actions, split it.

## 4. Writing style (applies to prose in every doc)

- Lead with the one-sentence fact, then the file:line evidence. Don't narrate how you found it.
- No secrets: config *key names* only, never connection strings, tokens, passwords (even from
  `Web.config` in this repo).
- No invented behavior. If `pOption` branches aren't all traced, say which ones are covered and
  which aren't — don't imply full coverage.
- Prefer a table over a paragraph when listing more than 3 parallel facts (columns, routes, params).
- Keep architecture docs (01–09) short enough that a skill can load the *whole file* into context
  cheaply. If one grows past ~150 lines, split it (e.g., `07a-oracle-packages.md`,
  `07b-oracle-conventions.md`).

## 5. Growth order (don't boil the ocean)

1. Architecture docs (01–09) — mostly done.
2. One feature file per screen as you're asked to explain/debug/change it — driven by real work,
   not a checklist.
3. One schema file per table that shows up in a feature file's `tables:` list.
4. Once you have Oracle read access: batch-dump `ALL_TAB_COLUMNS` / `ALL_CONSTRAINTS`, generate
   `schema/{TABLE}.md` for everything referenced so far (not all ~hundreds of tables at once).
5. Only then extend the harvester regex-scan for `ApiAction`/`MvcAction`/`JsClient` nodes
   directly from `src/` — it should parse front-matter + a few regexes, not re-derive facts docs
   already captured.

## 6. Packaging as an AI skill — done (minimal), grows with the docs

Built already:

```
AGENTS.md                          # tool-agnostic instructions — the actual traversal steps
CLAUDE.md                          # thin pointer to AGENTS.md (Claude Code auto-loads this)
.claude/skills/multitech-erp-explorer/
  SKILL.md                         # thin pointer to AGENTS.md, triggers on ERP questions
  references/
    graph-schema.md                # copy of 10-knowledge-graph.md's node/edge tables
.cursor/rules/multitech-erp.mdc    # thin pointer to AGENTS.md, alwaysApply: true
.agent/knowledge-graph/
  harvest_graph.py                 # regenerates nodes.jsonl/edges.jsonl from docs/features/*.md + docs/schema/*.md
  nodes.jsonl, edges.jsonl          # generated — never hand-edit
```

None of the pointer files duplicate the instructions — they all point at `AGENTS.md` so there's
one place to update, not several that drift.

Current harvester coverage is intentionally minimal: `Feature`/`Table` nodes and the edges
derivable from front-matter alone (`CALLS`, `USES_TABLE`, `MAPS_ROW`, `REQUIRES`, `BELONGS_TO`,
`MAPS_MODEL`, `HAS_PACKAGE`, `HAS_PROCEDURE`, `UPSTREAM`/`DOWNSTREAM`). The regex-harvest step
for `ApiAction`/`MvcAction`/`JsClient` nodes (scanning `[RoutePrefix]`/`[Route]` and Angular
`$http` calls directly from `src/`) is still future work — add it only once there are enough
feature files that the front-matter-only graph feels incomplete, not before.

`AGENTS.md` traversal steps (matches [10-knowledge-graph.md](10-knowledge-graph.md)):

1. Identify the `Module` from the URL prefix or table prefix (e.g. `MC_` → merchandising).
2. Look for `docs/features/{module}-{feature}.md`. If found, that's the answer — stop.
3. If missing, check the graph (`.agent/knowledge-graph/{nodes,edges}.jsonl`) before grepping source.
4. If still missing, follow the request-lifecycle checklist to trace it live, **then write the
   feature file** before answering (so the next question is a lookup, not a re-trace).
5. For column-level questions, prefer `docs/schema/{TABLE}.md`; fall back to model properties +
   `dr["..."]` mapping, and mark the answer `inferred`.

Don't inline the whole codebase map into any of these pointer files — point at the docs tree and
the graph files instead. A skill/rule that dumps `IocConfig.cs` into context on every invocation
defeats the point of building the graph.

## 7. What NOT to do

- Don't create a second, differently-shaped doc tree per AI tool (`docs/claude`, `docs/grok`,
  `docs/gpt`, ...) — there is one canonical `docs/` tree. Tool-specific needs are thin pointer
  files (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`), never a parallel copy of the content.
- Don't generate placeholder schema files for tables you haven't looked at.
- Don't hand-write `graph/*.jsonl` — it should always be regenerable from the docs + a harvest
  script, or it silently drifts from the source of truth.
