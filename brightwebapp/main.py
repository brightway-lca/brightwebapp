import bw_graph_tools as bgt
from brightwebapp.traversal import (
    _traverse_graph,
    _nodes_dict_to_dataframe,
    _edges_dict_to_dataframe,
    _trace_branch_from_last_node,
    _add_branch_information_to_edges_dataframe

)

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