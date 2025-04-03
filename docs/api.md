# API

## Scope Splitting Logic

The _scope splitting logic_ of `brightwebapp` accepts a Brightway node identifier (eg. `id` for the Ecoinvent databse) and `amount` of the activity.

It then solves the "inventory problem" [1] and returns the total environmental impact and a list of supply chain nodes with associated metadata:

| `activity_id` (Brightway node attribute `id`) | `amount` | `intensity` | `scope` | `supply_chain_uuid` |
|-----------------------------------------------|----------|-------------|---------|---------------------|

Users may edit edit any of [`amount`, `intensity`, `scope`] for a `supply_chain_uuid` in the returned list.

The _scope splitting logic_ will then update the total environmental impact and the list of supply chain nodes with associated metadata. No repeated modifications to the table are allowed. Users are permitted to make changes only once.

[1] Section 2.3, [Heijungs & Suh "The Computational Structure of Life Cycle Assessment" (2002)](https://doi.org/https://doi.org/10.1007/978-94-015-9900-9)