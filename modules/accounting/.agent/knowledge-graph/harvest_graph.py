#!/usr/bin/env python3
"""Regenerate .agent/knowledge-graph/{nodes,edges}.jsonl from the YAML
front-matter embedded in docs/accounting/features/*.md and
docs/accounting/schema/*.md.

This script is the *only* thing allowed to write {nodes,edges}.jsonl. Never
hand-edit those files - re-run this script instead after adding/editing a
feature or schema doc.

Adapted from MultitechERP's .agent/knowledge-graph/harvest_graph.py, re-pathed
because in this repo features/schema live under docs/accounting/, not
directly under docs/.

Usage:
    python .agent/knowledge-graph/harvest_graph.py

No third-party dependencies (front-matter here is a flat key: value block,
not general YAML, so a tiny hand-rolled parser is enough and keeps this
script runnable on any machine with plain Python 3).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .agent/knowledge-graph/ -> .agent/ -> repo root
DOCS_ROOT = REPO_ROOT / "docs" / "accounting"
FEATURES_DIR = DOCS_ROOT / "features"
SCHEMA_DIR = DOCS_ROOT / "schema"
GRAPH_DIR = Path(__file__).resolve().parent  # .agent/knowledge-graph/

SKIP_FILES = {"_template.md", "_conventions.md", "ERD.md"}

FRONTMATTER_RE = re.compile(r"```yaml\s*\n---\s*\n(.*?)\n---\s*\n```", re.DOTALL)

WARNINGS: list[str] = []


def parse_frontmatter(text: str) -> dict | None:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return None
    fields: dict[str, object] = {}
    for line in match.group(1).splitlines():
        line = line.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # strip inline comments (naive: only when '#' is preceded by whitespace)
        value = re.sub(r"\s+#.*$", "", value)
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fields[key] = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif value == "":
            fields[key] = None
        else:
            fields[key] = value
    return fields


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def looks_like_identifier(value: str) -> bool:
    return bool(IDENTIFIER_RE.match(value))


def split_multi(value: object) -> list[str]:
    """Split a scalar that may contain '|' or ',' separated alternatives, or pass through a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    parts = re.split(r"[|,]", str(value))
    return [p.strip() for p in parts if p.strip()]


def split_procedures(value: object) -> list[str]:
    """Like split_multi, but when the first alternative is package-qualified
    (PKG_X.proc) and later ones are bare (proc), re-prefix them with the same
    package - the doc convention is "PKG_X.a | b | c" meaning all belong to
    PKG_X, not that b/c are unqualified globals."""
    parts = split_multi(value)
    if not parts:
        return parts
    prefix = None
    if "." in parts[0]:
        prefix = parts[0].rsplit(".", 1)[0]
    result = []
    for part in parts:
        if prefix and "." not in part:
            part = f"{prefix}.{part}"
        result.append(part)
    return result


def harvest_feature(path: Path, fields: dict) -> tuple[list[dict], list[dict]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    feat_id = fields.get("id")
    if not feat_id:
        return nodes, edges

    nodes.append({
        "id": feat_id,
        "type": "Feature",
        "source_file": str(path.relative_to(REPO_ROOT)),
        "status": fields.get("status"),
        "http": fields.get("http"),
        "module": fields.get("module"),
        "category": fields.get("category"),
    })

    module = fields.get("module")
    if module:
        edges.append({"from": f"mod:{module}", "to": feat_id, "type": "CONTAINS"})

    service = fields.get("service")
    if service:
        svc_id = f"svc:{service}"
        nodes.append({"id": svc_id, "type": "Service", "source_file": str(path.relative_to(REPO_ROOT)), "name": service})
        edges.append({"from": feat_id, "to": svc_id, "type": "USES_SERVICE"})

    mvc = fields.get("mvc")
    if mvc:
        if looks_like_identifier(mvc.replace(".", "_")):
            mvc_id = f"mvc:{mvc}"
            nodes.append({"id": mvc_id, "type": "MvcAction", "source_file": str(path.relative_to(REPO_ROOT)), "handler": mvc})
            edges.append({"from": feat_id, "to": mvc_id, "type": "EXPOSES"})
        else:
            WARNINGS.append(f"{path}: skipping non-identifier mvc value {mvc!r}")

    # api: list of "METHOD PATH -> Controller.Method" entries — one ApiAction node per route,
    # EXPOSES edge from the feature, INJECTS edge to the feature's service (if any).
    for entry in split_multi(fields.get("api")):
        if " -> " not in entry:
            WARNINGS.append(f"{path}: skipping malformed api entry {entry!r} (expected 'METHOD PATH -> Controller.Method')")
            continue
        route_part, handler = (p.strip() for p in entry.split(" -> ", 1))
        if " " not in route_part:
            WARNINGS.append(f"{path}: skipping malformed api route {route_part!r} (expected 'METHOD PATH')")
            continue
        http_method, http_path = route_part.split(" ", 1)
        api_id = f"api:{http_method}:{http_path}"
        nodes.append({
            "id": api_id,
            "type": "ApiAction",
            "source_file": str(path.relative_to(REPO_ROOT)),
            "method": http_method,
            "path": http_path,
            "handler": handler,
        })
        edges.append({"from": feat_id, "to": api_id, "type": "EXPOSES"})
        if service:
            edges.append({"from": api_id, "to": f"svc:{service}", "type": "INJECTS"})

    for proc in split_procedures(fields.get("procedure")):
        if not looks_like_identifier(proc):
            WARNINGS.append(f"{path}: skipping non-identifier procedure value {proc!r}")
            continue
        edges.append({"from": feat_id, "to": f"proc:{proc}", "type": "CALLS"})

    for table in split_multi(fields.get("tables")):
        if not looks_like_identifier(table):
            WARNINGS.append(f"{path}: skipping non-identifier table value {table!r}")
            continue
        edges.append({"from": feat_id, "to": f"tbl:{table}", "type": "USES_TABLE"})

    for model in split_multi(fields.get("models")):
        edges.append({"from": feat_id, "to": f"model:{model}", "type": "MAPS_ROW"})

    for sess in split_multi(fields.get("session")):
        edges.append({"from": feat_id, "to": f"sess:{sess}", "type": "REQUIRES"})

    for up in split_multi(fields.get("upstream")):
        target = up if ":" in up else None
        if target:
            edges.append({"from": target, "to": feat_id, "type": "UPSTREAM"})

    for down in split_multi(fields.get("downstream")):
        target = down if ":" in down else None
        if target:
            edges.append({"from": feat_id, "to": target, "type": "DOWNSTREAM"})

    return nodes, edges


def harvest_schema(path: Path, fields: dict) -> tuple[list[dict], list[dict]]:
    nodes: list[dict] = []
    edges: list[dict] = []
    tbl_id = fields.get("id")
    if not tbl_id:
        return nodes, edges

    nodes.append({
        "id": tbl_id,
        "type": "Table",
        "source_file": str(path.relative_to(REPO_ROOT)),
        "status": fields.get("status"),
        "module": fields.get("module"),
    })

    module = fields.get("module")
    if module:
        edges.append({"from": tbl_id, "to": f"mod:{module}", "type": "BELONGS_TO"})

    model = fields.get("model")
    if model:
        edges.append({"from": tbl_id, "to": f"model:{model}", "type": "MAPS_MODEL"})

    package = fields.get("package")
    if package:
        edges.append({"from": tbl_id, "to": f"pkg:{package}", "type": "HAS_PACKAGE"})

    for proc in split_multi(fields.get("procedures")):
        if not looks_like_identifier(proc):
            WARNINGS.append(f"{path}: skipping non-identifier procedure value {proc!r}")
            continue
        proc_id = f"proc:{package}.{proc}" if package and "." not in proc else f"proc:{proc}"
        edges.append({"from": tbl_id, "to": proc_id, "type": "HAS_PROCEDURE"})

    # Pilot: column-level FK edges. Encoding is deliberately a flat string, not nested YAML,
    # to match this file's hand-rolled flat-key:value parser. Two forms per entry:
    #   "COLUMN->TABLE.COLUMN"  — this column is an FK to that column (creates node + FK_TO edge)
    #   "COLUMN"                — bare declaration, e.g. a PK that's an FK target elsewhere
    #                             (creates the node only, so FK_TO edges pointing at it aren't dangling)
    table_name = tbl_id.split(":", 1)[1] if ":" in tbl_id else tbl_id
    for col_entry in split_multi(fields.get("columns")):
        if "->" in col_entry:
            col_name, fk_target = (p.strip() for p in col_entry.split("->", 1))
        else:
            col_name, fk_target = col_entry.strip(), None
        if not looks_like_identifier(col_name):
            WARNINGS.append(f"{path}: skipping non-identifier column name {col_name!r}")
            continue
        col_id = f"col:{table_name}.{col_name}"
        nodes.append({"id": col_id, "type": "Column", "source_file": str(path.relative_to(REPO_ROOT)), "table": tbl_id})
        if fk_target is None:
            continue
        if "." not in fk_target:
            WARNINGS.append(f"{path}: skipping malformed fk target {fk_target!r} for column {col_name!r}")
            continue
        ref_table, ref_col = fk_target.rsplit(".", 1)
        edges.append({"from": col_id, "to": f"col:{ref_table}.{ref_col}", "type": "FK_TO"})

    return nodes, edges


def main() -> int:
    all_nodes: list[dict] = []
    all_edges: list[dict] = []

    for directory, harvester in ((FEATURES_DIR, harvest_feature), (SCHEMA_DIR, harvest_schema)):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name in SKIP_FILES:
                continue
            text = path.read_text(encoding="utf-8")
            fields = parse_frontmatter(text)
            if fields is None:
                WARNINGS.append(f"no front-matter found: {path}")
                continue
            if not fields.get("id"):
                WARNINGS.append(f"front-matter missing 'id': {path}")
                continue
            nodes, edges = harvester(path, fields)
            all_nodes.extend(nodes)
            all_edges.extend(edges)

    seen_ids: set[str] = set()
    deduped_nodes: list[dict] = []
    for node in all_nodes:
        if node["id"] in seen_ids:
            continue
        seen_ids.add(node["id"])
        deduped_nodes.append(node)
    all_nodes = deduped_nodes

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    nodes_path = GRAPH_DIR / "nodes.jsonl"
    edges_path = GRAPH_DIR / "edges.jsonl"

    with nodes_path.open("w", encoding="utf-8") as f:
        for node in all_nodes:
            f.write(json.dumps(node, ensure_ascii=False) + "\n")

    with edges_path.open("w", encoding="utf-8") as f:
        for edge in all_edges:
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")

    print(f"wrote {len(all_nodes)} nodes -> {nodes_path.relative_to(REPO_ROOT)}")
    print(f"wrote {len(all_edges)} edges -> {edges_path.relative_to(REPO_ROOT)}")
    for w in WARNINGS:
        print(f"warning: {w}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
