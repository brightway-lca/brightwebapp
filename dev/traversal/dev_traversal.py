# %%
import bw2data as bd
import bw2calc as bc
import bw2io as bi
import pandas as pd
from brightwebapp.brightway import load_and_set_useeio_project
from brightwebapp.traversal import perform_graph_traversal

load_and_set_useeio_project()

activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Automobiles; at manufacturer',
    type = 'product',
    location = 'United States'
)
method = ('Impact Potential', 'GCC')

traversal = perform_graph_traversal(
    demand={activity: 1},
    method=method,
    cutoff=0.01,
    biosphere_cutoff=0.01,
    max_calc=100,
    return_format='csv'
)
