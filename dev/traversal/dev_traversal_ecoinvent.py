# %%
import bw2data as bd
import bw2calc as bc
import bw2io as bi
import pandas as pd
from brightwebapp.brightway import load_and_set_ecoinvent_project
from brightwebapp.traversal import perform_graph_traversal

load_and_set_ecoinvent_project(
    username='MichaelWeinold',
    password='PASSWORD',
    overwrite_existing=False
)

activity = bd.utils.get_node(
    database = 'ecoinvent-3.10-cutoff',
    name = 'electricity production, hard coal',
    location = 'DE'
)
method = ('ecoinvent-3.10', 'CML v4.8 2016', 'climate change', 'global warming potential (GWP100)')

traversal = perform_graph_traversal(
    demand={activity: 1},
    method=method,
    cutoff=0.001,
    biosphere_cutoff=0.001,
    max_calc=15,
    return_format='dataframe'
)