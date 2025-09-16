import pytest
import bw2data as bd
import pandas as pd
from pandas.testing import assert_frame_equal
from bw_graph_tools.graph_traversal.graph_objects import Node

from tests.fixtures.supplychain import (
    example_system_bike_production
)


from brightwebapp.traversal import (
    _traverse_graph,
    perform_lca,
    perform_graph_traversal,
    _nodes_dict_to_dataframe,
    _edges_dict_to_dataframe,
    _trace_branch_from_last_node,
    _add_branch_information_to_edges_dataframe,
)


def test_perform_lca() -> None:
    """
    Tests the `perform_lca` function
    to ensure it correctly performs LCA on a simple supply chain graph.

    Returns
    -------
    None
    """
    example_system_bike_production()
    lca = perform_lca(
        demand={bd.get_node(code='bike'): 1},
        method=('IPCC', ),
    )
    assert lca.score > 0
    assert lca.characterized_inventory.shape == (1, 3)
    assert lca.inventory.shape == (1, 3)
    assert lca.technosphere_matrix.data.shape == (6,)
    assert lca.biosphere_matrix.data.shape == (2,)
    return lca


def test_traverse_graph() -> dict:
    """
    Tests the `_traverse_graph` function
    to ensure it correctly traverses a simple supply chain graph.

    Returns
    -------
    dict
        `bw_graph_tools.NewNodeEachVisitGraphTraversal` dictionary containing the nodes and edges of the graph traversal.
    """
    example_system_bike_production()
    lca = test_perform_lca()
    traversal = _traverse_graph(
        lca=lca,
        cutoff=0.01,
        biosphere_cutoff=0.01,
        max_calc=100,
    )
    assert isinstance(traversal, dict)
    assert 'nodes' in traversal
    assert 'edges' in traversal
    assert len(traversal['nodes']) == 4
    assert len(traversal['edges']) == 3
    return traversal


def test_nodes_dict_to_dataframe() -> None:
    """
    Test the `_nodes_dict_to_dataframe` function to ensure it correctly converts
    a dictionary of traversed nodes into a DataFrame with human-readable descriptions and emissions values.
    """
    traversal = test_traverse_graph()
    nodes = traversal['nodes']
    df = _nodes_dict_to_dataframe(nodes)
    assert df.iloc[0]['Scope'] == 1
    assert df.iloc[0]['Name'] == 'bike production'
    

def test_add_branch_information_to_edges_dataframe():
    """
    Test the `_add_branch_information_to_edges_dataframe` function to ensure it correctly
    adds branch information to a DataFrame of edges.
    """
    df_edges = pd.DataFrame([
        {'consumer_unique_id': 0, 'producer_unique_id': 1},
        {'consumer_unique_id': 1, 'producer_unique_id': 2},
        {'consumer_unique_id': 0, 'producer_unique_id': 3},
    ])
    df_expected = pd.DataFrame([
        {'producer_unique_id': 1, 'Branch': [0, 1]},
        {'producer_unique_id': 2, 'Branch': [0, 1, 2]},
        {'producer_unique_id': 3, 'Branch': [0, 3]},
    ])
    assert_frame_equal(
        _add_branch_information_to_edges_dataframe(df_edges),
        df_expected,
    )


def test_trace_branch_from_last_node():
    """
    Test the `_trace_branch_from_last_node` function to ensure it correctly traces the branch
    from the last node to the root node.
    """
    df_edges = pd.DataFrame([
        {'consumer_unique_id': 0, 'producer_unique_id': 1},
        {'consumer_unique_id': 1, 'producer_unique_id': 2},
        {'consumer_unique_id': 2, 'producer_unique_id': 3},
    ])
    branch = _trace_branch_from_last_node(df_edges, 3)
    assert branch == [0, 1, 2, 3]