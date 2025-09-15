# %%
import pandas as pd
import bw_graph_tools as bgt
import bw2calc as bc
import bw2data as bd

def _traverse_graph(
    demand: dict,
    method: tuple,
    cutoff: float,
    biosphere_cutoff: float,
    max_calc: int,
) -> dict:
    """
    Conducts a graph traversal of a life-cycle assessment calculation
    using the `bw_graph_tools` library.

    Warnings
    --------
    This function uses the new (v0.5) API of `bw_graph_tools` to perform a graph traversal:  
    `NewNodeEachVisitGraphTraversal(lca, settings)` and `traverse()` instead of `NewNodeEachVisitGraphTraversal(lca, cutoff)` and `.calculate()`.

    See Also
    --------
    [`bw_graph_tools.graph_traversal.new_node_each_visit.NewNodeEachVisitGraphTraversal`](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph_tools/graph_traversal/new_node_each_visit/index.html#bw_graph_tools.graph_traversal.new_node_each_visit.NewNodeEachVisitGraphTraversal)

    Parameters
    ----------
    demand : dict
        A dictionary representing the demand for the life-cycle assessment.
        Keys are `bw2data` nodes (activities) and the values are the amounts
        of those activities to be produced or consumed.
        Of the form:  
        ```python
        {bd.get_node(code='bike'): 1}
        ```
    method : tuple
        A tuple representing the method to be used for the life-cycle assessment.
        Of the form:  
        ```python
        ('Impact Potential', 'GCC')
        ```
    cutoff : float
        A float representing the cutoff threshold for the graph traversal.
    biosphere_cutoff : float
        A float representing the biosphere cutoff threshold for the graph traversal.
    max_calc : int
        An integer representing the maximum number of calculations to be performed during the graph traversal.

    Returns
    -------
    dict
        A dictionary containing the nodes and edges of the graph traversal.  
        Of the form:  
        ```python
        {
            'nodes': dict,  # Dictionary of Node objects
            'edges': list   # List of Edge objects
        }
        ```
    """
    my_functional_unit, data_objs, _ = bd.prepare_lca_inputs(
        demand=demand,
        method=method
    )
    lca = bc.LCA(
        demand=my_functional_unit,
        data_objs=data_objs,
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
    Returns a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
    with human-readable descriptions and emissions values of the nodes in the graph traversal.
    Every node in the graph traversal is represented by a row in the DataFrame.

    Warnings
    --------
    By default, only the node producing the functional unit is scope 1.
    All other nodes are scope 3.

    See Also
    --------
    [`bw_graph_tools.graph_traversal.new_node_each_visit.NewNodeEachVisitGraphTraversal`](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph)  
    [`brightwebapp.traversal._traverse_graph`][]  
    [`brightwebapp.traversal._edges_dict_to_dataframe`][]

    Parameters
    ----------
    nodes : dict
        A dictionary of nodes in the graph traversal.  
        Of the form:  
        ```python
        {
        -1: Node(
            unique_id=-1,
            activity_datapackage_id=-1,
            activity_index=-1,
            reference_product_datapackage_id=-1,
            reference_product_index=-1,
            reference_product_production_amount=1.0,
            depth=0,
            supply_amount=1.0,
            cumulative_score=37.68834121437976,
            direct_emissions_score=0.0,
            max_depth=None,
            direct_emissions_score_outside_specific_flows=0.0,
            remaining_cumulative_score_outside_specific_flows=0.0,
            terminal=False
        ),
        0: Node(
            unique_id=0,
            activity_datapackage_id=235,
            activity_index=234,
            reference_product_datapackage_id=542,
            reference_product_index=153,
            reference_product_production_amount=0.9988390803337097,
            depth=1,
            supply_amount=100.11622689671918,
            cumulative_score=37.68834121437975,
            direct_emissions_score=1.5464815391143154,
            max_depth=None,
            direct_emissions_score_outside_specific_flows=0.7561131308224808,
            remaining_cumulative_score_outside_specific_flows=36.897972806087914,
            terminal=False
        ),
        (...)
        }
        ```

    Returns
    -------
    pd.DataFrame
        A dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.  
        Of the form:  

        | `UID` | `Scope` | `Name` | `SupplyAmount` | (...) |
        |-------|---------|--------|----------------|-------|
        | (...) | (...)   | (...)  | (...)          | (...) |

    Raises
    ------
    TypeError
        If `nodes` is not a dictionary.
    """
    if not isinstance(nodes, dict):
        raise TypeError(
            f"Expected 'nodes' to be a dict, but got {type(nodes)}."
        )

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
                'Burden(Cumulative)': node.cumulative_score,
                'Burden(Direct)': node.direct_emissions_score + node.direct_emissions_score_outside_specific_flows,
                'Depth': node.depth,
                'activity_datapackage_id': node.activity_datapackage_id,
            }
        )
    return pd.DataFrame(list_of_row_dicts)


def _edges_dict_to_dataframe(edges: list) -> pd.DataFrame:
    """
    Returns a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
    with the edges of the graph traversal.
    Every node in the graph traversal is represented by a row in the DataFrame.

    See Also
    --------
    [`bw_graph_tools.graph_traversal.new_node_each_visit.NewNodeEachVisitGraphTraversal`](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph_tools/graph_traversal/new_node_each_visit/index.html#bw_graph_tools.graph_traversal.new_node_each_visit.NewNodeEachVisitGraphTraversal)  
    [`brightwebapp.traversal._traverse_graph`][]  
    [`brightwebapp.traversal._nodes_dict_to_dataframe`][]

    Parameters
    ----------
    edges : list
        A list of edges in the graph traversal.  
        Of the form:  
        ```python
        [
            Edge(
                consumer_index=-1,
                consumer_unique_id=-1,
                producer_index=234,
                producer_unique_id=0,
                product_index=153,
                amount=100.0
            ),
            Edge(
                consumer_index=234,
                consumer_unique_id=0,
                producer_index=78,
                producer_unique_id=1,
                product_index=42,
                amount=1.2520303865276814
            ),
            (...)
        ]
        ```

    Returns
    -------
    pd.DataFrame
        A dataframe with the edges of the graph traversal.  
        Of the form:  

        | `consumer_unique_id` | `producer_unique_id` |
        |----------------------|----------------------|
        | -1                   | 0                    |
        | 0                    | 1                    |
        | (...)                | (...)                |

    Raises
    ------
    TypeError
        If `edges` is not a list.
    """
    if not isinstance(edges, list):
        raise TypeError(
            f"Expected 'edges' to be a list, but got {type(edges)}."
        )
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

    See Also
    --------
    [`brightwebapp.traversal._add_branch_information_to_edges_dataframe`][]

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
        branch.insert(0, int(unique_id_last_node))

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

    See Also
    --------
    [`brightwebapp.traversal._trace_branch_from_last_node`][]

    Parameters
    ----------
    df : pd.DataFrame
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
            'producer_unique_id': row['producer_unique_id'],
            'Branch': branch
        })

    return pd.DataFrame(branches)


def perform_graph_traversal(
    demand: dict,
    method: tuple,
    cutoff: float,
    biosphere_cutoff: float,
    max_calc: int,
    return_format: str,
) -> pd.DataFrame | str:
    """
    Performs a graph traversal of a life-cycle assessment calculation
    and returns a DataFrame with the nodes and edges of the graph traversal.

    See Also
    --------
    [`bw_graph_tools`](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph_tools/index.html)

    Parameters
    ----------
    demand : dict
        A dictionary representing the demand for the life-cycle assessment.
        Keys are `bw2data` nodes (activities) and the values are the amounts
        of those activities to be produced or consumed.  
        Of the form:
        ```python
        {bd.get_node(code='bike'): 1}
        ```
    method : tuple
        A tuple representing the method to be used for the life-cycle assessment.
        Of the form:
        ```python
        ('Impact Potential', 'GCC')
        ```
    cutoff : float
        A float representing the cutoff threshold for the graph traversal.
        This is used to limit the depth of the traversal and the amount of data processed.
    biosphere_cutoff : float
        A float representing the biosphere cutoff threshold for the graph traversal.
        This is used to limit the amount of biosphere data processed.
    max_calc : int
        An integer representing the maximum number of calculations to be performed during the graph traversal.
        This is used to limit the amount of data processed and the depth of the traversal.
    return_format : str
        A string indicating the format of the return value.
        Can be either `'dataframe'` or `'csv'`.

    Returns
    -------
    pd.DataFrame
        **If `return_format` is `'dataframe'`**:  

        A DataFrame with the nodes and edges of the graph traversal.  
        The DataFrame contains the following columns:  

        - `UID`: Unique identifier of the node
        - `Scope`: Scope of the node (1 for functional unit, 3 for other nodes)
        - `Name`: Name of the node
        - `SupplyAmount`: Supply amount of the node
        - `BurdenIntensity`: Burden intensity of the node
        - `Burden(Direct)`: Direct burden of the node
        - `Depth`: Depth of the node in the graph
        - `Branch`: A list of unique identifiers of the nodes in the branch leading to the terminal producer node 
    str
        **If `return_format` is `'csv'`**:  

        A CSV string representation of the DataFrame with the nodes and edges of the graph traversal.  
        Separated by `,` without an index column:

        ```csv
        'UID,Scope,Name,SupplyAmount,BurdenIntensity,Burden(Direct),Depth,Branch\n
        0,1,Automobiles; at manufacturer,1.0011622689671917,0.01544686198282003,0.023025946699367965,1,\n
        1,3,Vehicle electrical and electronic equipment; at manufacturer,0.013377550027867835,0.0093078791680739,0.0002490332384485149,2,"[0, 1]"\n
        2,3,Transmission and power train parts; at manufacturer,0.09230018343308832,0.016065891653621933,0.002965769493290854,2,"[0, 2]"\n
        (...)
        ```
        
    Raises
    ------
    ValueError
        If `return_format` is not `'dataframe'` or `'csv'`.  
        If no edges are found in the graph traversal.
    """
    traversal: dict = _traverse_graph(
        demand=demand,
        method=method,
        cutoff=cutoff,
        biosphere_cutoff=biosphere_cutoff,
        max_calc=max_calc,
    )
    df_graph_traversal_nodes: pd.DataFrame = _nodes_dict_to_dataframe(traversal['nodes'])
    df_graph_traversal_edges: pd.DataFrame = _edges_dict_to_dataframe(traversal['edges'])
    if df_graph_traversal_edges.empty:
        raise ValueError(
            "No edges found in the graph traversal. "
            "This may be due to a cutoff value that is too high, "
            "or a demand that does not lead to any edges."
        )
    else:
        df_graph_traversal_edges = _add_branch_information_to_edges_dataframe(df_graph_traversal_edges)
        df_traversal = pd.merge(
            df_graph_traversal_nodes,
            df_graph_traversal_edges,
            left_on='UID',
            right_on='producer_unique_id',
            how='left'
        )
    df_traversal = df_traversal.drop(columns=['producer_unique_id', 'activity_datapackage_id'])
    if return_format == 'dataframe':
        return df_traversal
    elif return_format == 'csv':
        return df_traversal.to_csv(index=False)