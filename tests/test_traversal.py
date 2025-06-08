import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from brightwebapp.traversal import (
    _nodes_dict_to_dataframe,
    _edges_dict_to_dataframe,
    _trace_branch_from_last_node,
    _add_branch_information_to_edges_dataframe,
)

def test_nodes_dict_to_dataframe():
    dict_nodes = {
        -1: Node(unique_id=-1, activity_datapackage_id=-1, activity_index=-1, reference_product_datapackage_id=-1, reference_product_index=-1, reference_product_production_amount=1.0, depth=0, supply_amount=1.0, cumulative_score=1374.6606234406681, direct_emissions_score=0.0, max_depth=None, direct_emissions_score_outside_specific_flows=0.0, remaining_cumulative_score_outside_specific_flows=0.0, terminal=False),
        0: Node(unique_id=0, activity_datapackage_id=190005058932379648, activity_index=0, reference_product_datapackage_id=190005058932379648, reference_product_index=0, reference_product_production_amount=1.0, depth=1, supply_amount=1.0, cumulative_score=1374.6606234406681, direct_emissions_score=0.0, max_depth=None, direct_emissions_score_outside_specific_flows=0.0, remaining_cumulative_score_outside_specific_flows=1374.6606234406681, terminal=False),
        1: Node(unique_id=1, activity_datapackage_id=190005058949156864, activity_index=1, reference_product_datapackage_id=190005058949156864, reference_product_index=1, reference_product_production_amount=1.0, depth=2, supply_amount=15.5, cumulative_score=1374.6606234406681, direct_emissions_score=412.30000591278076, max_depth=None, direct_emissions_score_outside_specific_flows=0.0, remaining_cumulative_score_outside_specific_flows=962.3606175278874, terminal=False),
        2: Node(unique_id=2, activity_datapackage_id=190005058961739776, activity_index=2, reference_product_datapackage_id=190005058961739776, reference_product_index=2, reference_product_production_amount=1.0, depth=3, supply_amount=85.25, cumulative_score=962.3606175278871, direct_emissions_score=954.7999837398529, max_depth=None, direct_emissions_score_outside_specific_flows=0.0, remaining_cumulative_score_outside_specific_flows=7.560633788034238, terminal=True)
    }

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