# %%
import pandas as pd
import bw_graph_tools as bgt
import bw2calc as bc

def _traverse_graph(
    demand: dict,
    method: tuple,
    cutoff: float,
    biosphere_cutoff: float,
    max_calc: int,
) -> dict:
    """
    Warnings
    --------
    This function uses the new (v0.5) API of `bw_graph_tools` to perform a graph traversal:  
    `NewNodeEachVisitGraphTraversal(lca, settings)` and `traverse()` instead of `NewNodeEachVisitGraphTraversal(lca, cutoff)` and `.calculate()`.
    """
    lca = bc.LCA(
        demand=demand,
        method=method,
    )
    lca.lci()
    lca.lcia()
    traversal = bgt.NewNodeEachVisitGraphTraversal(
        lca=lca,
        settings=bgt.GraphTraversalSettings(
            cutoff=cutoff,
            biosphere_cutoff=biosphere_cutoff,
            max_calc=max_calc,
        )
    )
    traversal.traverse()
    return {
        'nodes': traversal.nodes,
        'edges': traversal.edges,
    }


def _nodes_dict_to_dataframe(
    nodes: dict,
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

    for node in nodes.values():
        scope = 3
        if node.unique_id == -1:
            continue
        elif node.unique_id == 0:
            scope = 1
        else:
            pass
        list_of_row_dicts.append(
            {
                'UID': node.unique_id,
                'Scope': scope,
                'Name': bd.get_node(id=node.activity_datapackage_id)['name'],
                'SupplyAmount': node.supply_amount,
                'BurdenIntensity': node.direct_emissions_score/node.supply_amount,
                # 'Burden(Cumulative)': node.cumulative_score,
                'Burden(Direct)': node.direct_emissions_score + node.direct_emissions_score_outside_specific_flows,
                'Depth': node.depth,
                'activity_datapackage_id': node.activity_datapackage_id,
            }
        )
    return pd.DataFrame(list_of_row_dicts)


def _edges_dict_to_dataframe(edges: list) -> pd.DataFrame:
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

    if unique_id_last_node not in df['producer_unique_id'].values:
        raise ValueError(
            f"unique_id_last_node {unique_id_last_node} not found in 'producer_unique_id' column of the dataframe."
        )

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
    if df.empty:
        return pd.DataFrame()

    branches: list = []

    for _, row in df.iterrows():
        branch: list = _trace_branch_from_last_node(df, int(row['producer_unique_id']))
        branches.append({
            'producer_unique_id': int(row['producer_unique_id']),
            'Branch': branch
        })

    return pd.DataFrame(branches)


    def perform_graph_traversal(self, event):
        widget_cutoff_indicator_statictext.value = self.graph_traversal_cutoff * 100
        self.graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(self.lca, cutoff=self.graph_traversal_cutoff)
        self.df_graph_traversal_nodes: pd.DataFrame = nodes_dict_to_dataframe(self.graph_traversal['nodes'])
        self.df_graph_traversal_edges: pd.DataFrame = edges_dict_to_dataframe(self.graph_traversal['edges'])
        if self.df_graph_traversal_edges.empty:
            return
        else:
            self.df_graph_traversal_edges = add_branch_information_to_edges_dataframe(self.df_graph_traversal_edges)
            self.df_tabulator_from_traversal = pd.merge(
                self.df_graph_traversal_nodes,
                self.df_graph_traversal_edges,
                left_on='UID',
                right_on='producer_unique_id',
                how='left')