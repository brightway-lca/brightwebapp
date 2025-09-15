# `brightwebapp` Changelog

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