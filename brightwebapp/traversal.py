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

