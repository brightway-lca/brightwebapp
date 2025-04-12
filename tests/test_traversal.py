# %%
import pytest

import bw_graph_tools as bgt
import bw2calc as bc
import bw2data as bd

from .fixtures.traversal import example_system_bike_production

def test_traversal(example_system_bike_production):
    """
    Test the traversal function.
    """
    db = example_system_bike_production
    lca = bc.LCA( 
        demand={bd.get_node(code='bike'): 100}, 
        method = ('IPCC')
    )
    lca.lci()
    
test_traversal(example_system_bike_production)