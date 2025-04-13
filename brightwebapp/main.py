# IMPLEMENT AND UNIT-TEST THIS!
def perform_graph_traversal(self, event):
        widget_cutoff_indicator_statictext.value = self.graph_traversal_cutoff * 100
        self.graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(self.lca, cutoff=self.graph_traversal_cutoff)
        self.df_graph_traversal_nodes: pd.DataFrame = nodes_dict_to_dataframe(self.graph_traversal['nodes'])
        self.df_graph_traversal_edges: pd.DataFrame = edges_dict_to_dataframe(self.graph_traversal['edges'])
        if self.df_graph_traversal_edges.empty:
            return
        else:
            self.df_graph_traversal_edges = add_branch_information_to_edges_dataframe(self.df_graph_traversal_edges)
            self.df_tabulator_from_traversal = pd.merge(
                self.df_graph_traversal_nodes,
                self.df_graph_traversal_edges,
                left_on='UID',
                right_on='producer_unique_id',
                how='left')