# `brightwebapp` Changelog

## 1.0.1 (2026-09-28)

### Bug Fixes

- Fixed `perform_graph_traversal` raising `TypeError: object of type 'NoneType' has no len()` when called with a pre-computed `lca` object instead of `method` and `demand`, which broke the LCA calculation in the web application. The function also no longer prints a spurious warning when called with `method` and `demand` only.
- Fixed the `Burden(Direct)` column of `perform_graph_traversal` double-counting direct emissions: it was the sum of `direct_emissions_score` and `direct_emissions_score_outside_specific_flows`, but the latter is part of the former. `Burden(Direct)` is now `direct_emissions_score` (`= SupplyAmount * BurdenIntensity`). This also fixes the scope pie chart and the "Update Data based on User Table Input" results of the web application.
- Added the missing upper bounds `peewee<4` (`bw2data==4.5` is incompatible with peewee 4) and `numpy<2.4` (`bw_graph_tools==0.6` uses `numpy.in1d`, which was removed in NumPy 2.4).
- Raised the minimum Python version to 3.10, since the package does not import on Python 3.9.

### Web Application

- The web application now loads all Python packages from a lock file (`pyodide/pyodide-lock.json`) instead of resolving them from PyPI on every page load. Previously, the release of `typing-inspection==0.4.4` (requiring `typing-extensions>=4.15.0`) broke the web application on load.
- Added `app/build.py` to build the web application, and `app/smoke_test.py` to test it in a headless browser before every deployment and once a week.
- Scope 3 emissions are now the LCA score minus Scope 1 and Scope 2 emissions, instead of the sum of the direct emissions of the processes shown in the table (which depended on the graph traversal cut-off).
- Fixed the unit of the "Ozone Depletion" method (`kg CFC11 eq` instead of `kg O3 eq`).
- Very small LCA scores are now shown in scientific notation instead of `0.000`.
- If the graph traversal fails (e.g. because the cut-off is too high), the web application now shows only the error notification, instead of raising an exception and showing the results of the previous calculation.
- Clicking "Update Data based on User Table Input" before computing an LCA score now shows a notification instead of raising an exception.
- Documentation links now open in a new tab, instead of leaving the web application (and discarding the loaded database).

## 1.0.0 (2025-09-26)

First stable release.

## 0.0.10 (2025-09-17)

### New Features

- Added documentation and tests to the `perform_lca` function in `brightwebapp/traversal.py`, including error handling for invalid demand inputs.
- Updated the `/database/getnode` API endpoint to allow fetching bw2data node codes by `name`, `location`, etc.

## 0.0.9 (2025-09-16)

### New Features

- The `traverse_graph` function now accepts optional parameters `lca`, `method`, and `demand` to allow for more flexible graph traversal without relying on a pre-existing LCA instance. This allows the dashboard to use the `lca.score` values directly.

## 0.0.8 (2025-09-15)

### New Features

- Moved the `create_plotly_figure_piechart` function from the `app/index.py` file to the `brightwebapp/visualization.py` module for better modularity and reusability.

### Bug Fixes

- Adjusted `app/index.py` to fail LCA calculation gracefully with notification if no nodes are found in the graph traversal (due to high cutoff value), instead of throwing an error (https://github.com/brightway-lca/brightwebapp/issues/31).

## 0.0.7 (2025-07-13)

First release including the FastAPI `api` module.

### Bug Fixes

The `_trace_branch_from_last_node` function now correctly adds only `int` values to the traversal list, instead of `np.int64` values, which caused issues when converting the traversal dataframe to a CSV file.

## 0.0.6 (2025-06-27)

First "stable" release.

## 0.0.2 - 0.0.5

Minor releases no longer available on PyPi

## 0.0.1 (2025-06-22)

Initial release of `brightwebapp`.