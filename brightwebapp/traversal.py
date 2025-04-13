# %%
import pandas as pd


def nodes_dict_to_dataframe(
        nodes: dict,
        uid_electricity: int = 53 # hardcoded for USEEIO
    ) -> pd.DataFrame:
    """
    Returns a dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.

    Parameters
    ----------
    nodes : dict
        A dictionary of nodes in the graph traversal.
        Can be created by selecting the 'nodes' key from the dictionary
        returned by the function `bw_graph_tools.NewNodeEachVisitGraphTraversal.calculate()`.

    Returns
    -------
    pd.DataFrame
        A dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.
    """
    list_of_row_dicts = []
    for current_node in nodes.values():

        scope: int = 3
        if current_node.unique_id == -1:
            continue
        elif current_node.unique_id == 0:
            scope = 1
        elif current_node.activity_datapackage_id == uid_electricity:
            scope = 2
        else:
            pass
        list_of_row_dicts.append(
            {
                'UID': current_node.unique_id,
                'Scope': scope,
                'Name': bd.get_node(id=current_node.activity_datapackage_id)['name'],
                'SupplyAmount': current_node.supply_amount,
                'BurdenIntensity': current_node.direct_emissions_score/current_node.supply_amount,
                # 'Burden(Cumulative)': current_node.cumulative_score,
                'Burden(Direct)': current_node.direct_emissions_score + current_node.direct_emissions_score_outside_specific_flows,
                'Depth': current_node.depth,
                'activity_datapackage_id': current_node.activity_datapackage_id,
            }
        )
    return pd.DataFrame(list_of_row_dicts)


def edges_dict_to_dataframe(edges: list) -> pd.DataFrame:
    """
    To be added...
    """
    if len(edges) < 2:
        return pd.DataFrame()
    else:
        list_of_row_dicts = []
        for current_edge in edges:
            list_of_row_dicts.append(
                {
                    'consumer_unique_id': current_edge.consumer_unique_id,
                    'producer_unique_id': current_edge.producer_unique_id
                }
            )
        return pd.DataFrame(list_of_row_dicts).drop(0)
    

def _trace_branch_from_last_node(
    df: pd.DataFrame,
    unique_id_last_node: int
) -> list:
    """
    Given a dataframe of graph edges with columns `consumer_unique_id` and `producer_unique_id`
    and the `producer_unique_id` of the "final node" in a branch,
    returns the branch of nodes that lead to the final node.

    For example, for the following graph:

    ```mermaid
    graph TD
    0 --> 1
    0 --> 2
    0 --> 3
    2 --> 4
    3 --> 5
    5 --> 6
    ```

    which can be represented as a DataFrame of edges:

    | `consumer_unique_id` | `producer_unique_id` | Comment                                      |
    |----------------------|----------------------|----------------------------------------------|
    | 0                    | 1                    | # 1 is terminal producer node of this branch |
    | 0                    | 2                    |                                              |
    | 0                    | 3                    |                                              |
    | 2                    | 4                    | # 4 is terminal producer node of this branch |
    | 3                    | 5                    |                                              |
    | 5                    | 6                    | # 6 is terminal producer node of this branch |

    For `unique_id_last_node = 6`, the function returns `[0, 3, 5, 6]`.

    Example
    -------
    ```python
    >>> data = {
    >>>     'consumer_unique_id': [0, 0, 0, 2, 3, 5],
    >>>     'producer_unique_id': [1, 2, 3, 4, 5, 6],
    >>> }
    >>> df = pd.DataFrame(data)
    >>> trace_branch_from_last_node(df, 6)
    [0, 3, 5, 6]
    ```

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of graph edges. Must contain integer-type columns 'consumer_unique_id' and 'producer_unique_id'.
    unique_id_last_node : int
        The `producer_unique_id` integer indicating the last node of a branch to trace.

    Returns
    -------
    list
        A list of integers indicating the branch of nodes that lead to the starting node.
    """

    branch: list = [unique_id_last_node]

    while True:
        previous_node: int = df[df['producer_unique_id'] == unique_id_last_node]['consumer_unique_id']
        if previous_node.empty:
            break
        unique_id_last_node: int = previous_node.values[0]
        branch.insert(0, unique_id_last_node)

    return branch


def _add_branch_information_to_edges_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of graph edges with columns `consumer_unique_id` and `producer_unique_id`
    adds a column `branch` containing a list of 
    
    For example, for the following graph:

    ```mermaid
    graph TD
    0 --> 1
    0 --> 2
    0 --> 3
    2 --> 4
    3 --> 5
    5 --> 6
    ```

    which can be represented as a DataFrame of edges:

    | `consumer_unique_id` | `producer_unique_id` | Comment                                      |
    |----------------------|----------------------|----------------------------------------------|
    | 0                    | 1                    | # 1 is terminal producer node of this branch |
    | 0                    | 2                    |                                              |
    | 0                    | 3                    |                                              |
    | 2                    | 4                    | # 4 is terminal producer node of this branch |
    | 3                    | 5                    |                                              |
    | 5                    | 6                    | # 6 is terminal producer node of this branch |

    the function returns a DataFrame of edges with an additional column `branch`:

    | `consumer_unique_id` | `producer_unique_id` | `branch`       |
    |----------------------|----------------------|----------------|
    | 0                    | 1                    | `[0, 1]`       |
    | 0                    | 2                    | `[0, 2]`       |
    | 0                    | 3                    | `[0, 3]`       |
    | 2                    | 4                    | `[0, 2, 4]`    |
    | 3                    | 5                    | `[0, 3, 5]`    |
    | 5                    | 6                    | `[0, 3, 5, 6]` |

    Parameters
    ----------
    df_edges : pd.DataFrame
        A dataframe of graph edges.  
        Must contain integer-type columns `consumer_unique_id` and `producer_unique_id`.

    Returns
    -------
    pd.DataFrame
        A dataframe of graph nodes with a column `branch` that contains the branch of nodes that lead to the terminal producer node.
    """

    branches: list = []

    for _, row in df.iterrows():
        branch: list = _trace_branch_from_last_node(df, int(row['producer_unique_id']))
        branches.append({
            'producer_unique_id': int(row['producer_unique_id']),
            'Branch': branch
        })

    return pd.DataFrame(branches)


def _update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    
    For instance, given a DataFrame of the kind:

    | `UID` | `SupplyAmount` | `SupplyAmount_USER` | `Branch`        |
    |-------|----------------|---------------------|-----------------|
    | `0`   | `1`            | `NaN`               | `NaN`           |
    | `1`   | `0.5`          | `0.25`              | `[0,1]`         |
    | `2`   | `0.2`          | `NaN`               | `[0,1,2]`       |
    | `3`   | `0.1`          | `NaN`               | `[0,3]`         |
    | `4`   | `0.1`          | `0.18`              | `[0,1,2,4]`     |
    | `5`   | `0.05`         | `NaN`               | `[0,1,2,4,5]`   |
    | `6`   | `0.01`         | `NaN`               | `[0,1,2,4,5,6]` |

    the function returns a DataFrame of the kind:

    | `UID` | `SupplyAmount`      | `Branch`        |
    |-------|---------------------|-----------------|
    | `0`   | `1`                 | `NaN`           |
    | `1`   | `0.25`              | `[0,1]`         | NOTA BENE!
    | `2`   | `0.2 * (0.25/0.5)`  | `[0,1,2]`       |
    | `3`   | `0.1`               | `[0,3]`         |
    | `4`   | `0.18`              | `[0,1,2,4]`     | NOTA BENE!
    | `5`   | `0.05 * (0.18 / 0.1)` | `[0,1,2,4,5]`   | # Corrected calculation based on logic
    | `6`   | `0.01 * (0.18 / 0.1)` | `[0,1,2,4,5,6]` | # Corrected calculation based on logic


    Notes
    -----

    As we can see, the function updates production only
    for those nodes upstream of a node with `SupplyAmount_USER`:

    - Node `2` is upstream of node `1`, which has a `SupplyAmount_USER` value.
    - Node `3` is NOT upstream of node `1`. It is upstream of node `0`, but node `0` does not have a `SupplyAmount_USER` value.

    As we can see, the function always takes the "most recent"
    `SupplyAmount_USER` value upstream of a node:

    - Node `5` is upstream of node `4`, which has a `SupplyAmount_USER` value.
    - Node `4` is upstream of node `1`, which also has a `SupplyAmount_USER` value.

    In this case, the function takes the `SupplyAmount_USER` value of node `4`, not of node `1`.

    Warnings
    --------

    ![Diagram](../_media/user_input_table.svg)

    We assume:

    Parameters
    ----------
    df : `pd.DataFrame`
        Input DataFrame. Must have the columns `UID`, `SupplyAmount`, `SupplyAmount_USER` and `Branch`.

    Returns
    -------
    `pd.DataFrame`
        Output DataFrame with updated `SupplyAmount` column.
    """

    df_filtered = df[~df['SupplyAmount_USER'].isna()]
    dict_user_input = df_filtered.set_index('UID').to_dict()['SupplyAmount_USER']
    
    """
    For the example DataFrame from the docstrings above,
    the dict_user_input would be:

    dict_user_input = {
        1: 0.25,
        4: 0.18
    }
    """

    df = df.copy(deep=True)
    def multiplier(row):
        if not isinstance(row['Branch'], list):
            return row['SupplyAmount']
        elif (
            not np.isnan(row['SupplyAmount_USER'])
        ):
            return row['SupplyAmount_USER']
        elif (
            set(dict_user_input.keys()).intersection(row['Branch'])
        ):
            for branch_UID in reversed(row['Branch']):
                if branch_UID in dict_user_input.keys():
                    return row['SupplyAmount'] * dict_user_input[branch_UID]
        else:
            return row['SupplyAmount']

    df['SupplyAmount_EDITED'] = df.apply(multiplier, axis=1)

    df.drop(columns=['SupplyAmount_USER'], inplace=True)
    df['SupplyAmount'] = df['SupplyAmount_EDITED']
    df.drop(columns=['SupplyAmount_EDITED'], inplace=True)

    return df