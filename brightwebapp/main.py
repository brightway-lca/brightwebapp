import bw_graph_tools as bgt
import bw2calc
from brightwebapp.traversal import (
    nodes_dict_to_dataframe,
    edges_dict_to_dataframe,
)



# IMPLEMENT AND UNIT-TEST THIS!
def perform_graph_traversal(
    demand: dict,
    method: tuple,
    cutoff: float,

) -> pd.DataFrame:
    dict_graph_traversal = bgt.NewNodeEachVisitGraphTraversal(lca=lca, cutoff=cutoff)
    df_graph_traversal_nodes = nodes_dict_to_dataframe(dict_graph_traversal['nodes'])
    df_graph_traversal_edges = edges_dict_to_dataframe(dict_graph_traversal['edges'])
    if df_graph_traversal_edges.empty:
        return
    else:
        df_graph_traversal_edges = add_branch_information_to_edges_dataframe(self.df_graph_traversal_edges)
        df_tabulator_from_traversal = pd.merge(
            self.df_graph_traversal_nodes,
            self.df_graph_traversal_edges,
            left_on='UID',
            right_on='producer_unique_id',
            how='left')
        
def _format_graph_traversal_results(
    dict_nodes: dict,
    dict_edges: dict,
) -> pd.DataFrame:
    df_graph_traversal_nodes = nodes_dict_to_dataframe(dict_graph_traversal['nodes'])
    df_graph_traversal_edges = edges_dict_to_dataframe(dict_graph_traversal['edges'])
    if df_graph_traversal_edges.empty:
        return
    else:
        df_graph_traversal_edges = add_branch_information_to_edges_dataframe(self.df_graph_traversal_edges)
        df_tabulator_from_traversal = pd.merge(
            self.df_graph_traversal_nodes,
            self.df_graph_traversal_edges,
            left_on='UID',
            right_on='producer_unique_id',
            how='left')