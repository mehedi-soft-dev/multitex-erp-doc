# 11 — Frontend patterns (as implemented, audited against 3 reference guides)

Management wants new frontend work to follow three external references. This audits the actual
code against them (counts below are company-authored files only — `Areas/*/Client/app` +
`src/ERPSolution/Client/app` — vendor libraries in `Scripts/` and `Content/` are excluded from
counts, though their versions are noted).

Reference guides:

1. [John Papa AngularJS style guide (a1)](https://github.com/johnpapa/angular-styleguide/blob/master/a1/README.md)
2. [Angular UI Bootstrap docs, v0.12.1](http://angular-ui.github.io/bootstrap/versioned-docs/0.12.1/)
3. [Telerik Kendo UI Grid — sorting](https://docs.telerik.com/kendo-ui/controls/data-management/grid/sorting)

**Bottom line up front:** the backend recipe in [04-design-patterns.md](04-design-patterns.md) is
reliable enough for an AI to reproduce accurately. The frontend is now documented here to the
same level — an AI told "create a page like X" can follow this file's recipe (section "How to
build a new page's frontend") and match house style, instead of improvising.

## 1. John Papa AngularJS style guide — audit

| Guide rule | Followed? | Evidence |
|---|---|---|
| IIFE per file (Y001) | **Yes, near-universal** | 1191 / 1215 files (98%) start `(function () {`|
| `'use strict'` (Y002) | **Yes, near-universal** | 1186 / 1215 files (98%) |
| Named functions, minification-safe DI (Y023–Y025, Y091) | **Yes, but via inline array literal, not `.$inject`** | 1338 / 1343 `.controller(` calls (99.6%) use `.controller('X', ['dep1', 'dep2', X])` — named function `X` as the last array element. Only 12 files use the `.$inject = [...]` property form the guide shows as the primary example. Example: [`Areas/Admin/Client/app/controllers/GradeController.js:4`](../src/ERPSolution/Areas/Admin/Client/app/controllers/GradeController.js) |
| Anonymous inline controller functions (guide says avoid) | **Followed — none found** | 0 occurrences of `.controller('X', function(...) {...})` |
| `controllerAs` + `vm` (Y030–Y035) | **Yes, but wired in the Razor view, not the JS route config** | `ng-controller="XController as vm"` — 82 occurrences directly in `.cshtml` (some commented out); `var vm = this;` in 973 / 1215 files (80%). Example: [`Areas/Admin/Views/HrGrade/Index1.cshtml`](../src/ERPSolution/Areas/Admin/Views/HrGrade/Index1.cshtml) paired with [`GradeController.js`](../src/ERPSolution/Areas/Admin/Client/app/controllers/GradeController.js). **Do not grep JS route files for `controllerAs:` expecting to find it — it isn't there.** |
| Use `$scope` only for `$watch`/`$on`/`$emit`/`$broadcast`, not view binding (Y035) | **Partially — some legacy exceptions likely** | `$scope.` still appears in 822 / 1215 files (68%). Consistent with the guide where it's event-bus usage; not verified file-by-file whether any of these are old `$scope`-only controllers predating the `vm` convention. Don't assume every hit is compliant — check the individual file before copying it as a reference. |
| Controller `activate()` pattern (Y080) | **Yes, common** | Same `GradeController.js` example: `activate()` called immediately, returns a promise, sets `vm.showSplash = false` on resolve. |
| Folders-by-feature / LIFT (Y152) | **No — folder-by-type, confirmed in all 19 Areas** | Every Area's `Client/app` has exactly `controllers/`, `services/`, `directives/` — zero feature-based subfolders anywhere. This is a direct, consistent deviation from the guide. |

**For new code:** match the existing 99% pattern (IIFE, `'use strict'`, inline-array DI ending in
a named function, `vm = this` + `ng-controller="X as vm"` in the view, an `activate()` bootstrap
function). Don't introduce `.$inject` style or feature folders for one new screen — that makes
the new file the odd one out, which is worse than the guide deviation itself. Raise folder-by-
feature as a team decision if you want to change it project-wide, not per-screen.

## 2. Angular UI Bootstrap (bundled v0.12.1) — audit

Vendor file: `Content/assets/global/plugins/angularjs/plugins/ui-bootstrap-tpls-0.12.1.min.js` —
confirms the version, so the **0.12.1 versioned docs URL above is the correct one to reference**,
not the current Angular UI Bootstrap docs (APIs changed since).

| Component | Used? | Evidence |
|---|---|---|
| Module dependency (`ui.bootstrap`) | Declared at the app-shell level, not per-Area | Only 5 files declare it: `Client/app/app.module.js`, `Client/app/core/core.module.js`, `Client/app/menulesspage.module.js`, `Client/app/displayboard.module.js`, one directive file. Area sub-modules don't need to — they run under the same Angular app. |
| Modal (`$modal.open(...)`) | **Heavily used** | 692 occurrences. **All via the old `$modal` service name — 0 occurrences of `$uibModal`.** This is the pre-rename (0.12.1-era) API; don't write new code assuming `$uibModal` exists, it doesn't in this bundle. |
| Tabs / accordion / datepicker / typeahead / pagination / alert | Used, moderately | ~290 combined occurrences across `.cshtml` views. |

**For new code:** use `$modal.open({...})`, not `$uibModal`. If a future upgrade of the vendor
bundle renames the service, that's a project-wide migration, not something to special-case per
screen.

## 3. Kendo UI Grid — sorting audit

Grids are built almost entirely **declaratively** in Razor views, not imperatively in JS:

| Pattern | Count |
|---|---|
| `kendo-grid` directive in `.cshtml` (declarative, Angular-bound) | 1310 occurrences |
| Raw jQuery `.kendoGrid(...)` call in JS | 32 occurrences (legacy/minority path) |
| `vm.{name}GridOption` naming convention for the JS-side options object | 1330 occurrences — this is **the** naming convention |
| `sortable: true` (simple boolean) | 613 occurrences |
| `sortable: { ... }` (advanced — e.g. multi-column, custom comparer) | 13 occurrences |

**Reading:** the standard pattern is `vm.xGridOption = { ..., sortable: true, ... }` in the
controller, bound via `kendo-grid="grid" k-options="vm.xGridOption"` (or similar) in the view.
Sorting is almost always the plain single-column click-to-sort from the basic Kendo docs — the
advanced sorting page (multi-column `sortable: { mode: "multiple" }`, custom `compare`) the
manager linked is relevant to only ~13 existing grids. If the guideline is "use Kendo's advanced
sorting," that's a deliberate change from current practice, not already the norm — flag that
distinction when asked to build a "grid like the others."

## How to build a new page's frontend (recipe an AI can follow)

Combine with [04-design-patterns.md](04-design-patterns.md) "How to name a change" for the
backend half. Frontend half, in the dominant/confirmed pattern:

1. New controller file `Areas/{Area}/Client/app/controllers/{Name}Controller.js`:
   ```js
   (function () {
       'use strict';
       angular.module('multitex.{area}').controller('{Name}Controller', ['{dep1}', '{dep2}', {Name}Controller]);
       function {Name}Controller({dep1}, {dep2}) {
           var vm = this;
           activate();
           vm.someGridOption = { sortable: true, /* ... */ };
           function activate() { /* load initial data, return a promise */ }
       }
   })();
   ```
2. Razor view wires it up: `<div ng-controller="{Name}Controller as vm"> ... </div>`, grid as
   `kendo-grid="grid" k-options="vm.someGridOption"` (or the project's existing grid directive
   attribute — check a sibling view in the same Area for the exact attribute set, they vary).
3. Modals via `$modal.open({ templateUrl: ..., controller: ... })`, not `$uibModal`.
4. New Angular module dependency needed beyond what the Area module already has? Add it at the
   Area's `.module.js`, not per-controller.
5. Don't create a feature-based subfolder for the new controller/service/directive — put them in
   the existing `controllers/`/`services/`/`directives/` folders to match the other 18 Areas.

## What NOT to assume

- Don't assume `$uibModal` exists — it doesn't in this bundle.
- Don't look for `controllerAs:` in JS route configs — it's wired in the view markup instead.
- Don't assume every grid needs custom sorting — `sortable: true` is the norm; only follow the
  advanced Telerik sorting doc when a screen actually needs multi-column or custom-comparer sort.
- Don't create a new feature-based folder — this codebase is folder-by-type, consistently, across
  all 19 Areas.
