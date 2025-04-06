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