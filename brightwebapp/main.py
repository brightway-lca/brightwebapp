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





def trace_branch(df: pd.DataFrame, start_node: int) -> list:
    """
    Given a dataframe of graph edges and a "starting node" (producer_unique_id), returns the branch of nodes that lead to the starting node.

    For example:

    | consumer_unique_id | producer_unique_id |
    |--------------------|--------------------|
    | 0                  | 1                  | # 1 is terminal producer node
    | 0                  | 2                  |
    | 0                  | 3                  |
    | 2                  | 4                  | # 4 is terminal producer node
    | 3                  | 5                  |
    | 5                  | 6                  | # 6 is terminal producer node

    For start_node = 6, the function returns [0, 3, 5, 6]

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of graph edges. Must contain integer-type columns 'consumer_unique_id' and 'producer_unique_id'.
    start_node : int
        The integer indicating the producer_unique_id starting node to trace back from.

    Returns
    -------
    list
        A list of integers indicating the branch of nodes that lead to the starting node.
    """

    branch: list = [start_node]

    while True:
        previous_node: int = df[df['producer_unique_id'] == start_node]['consumer_unique_id']
        if previous_node.empty:
            break
        start_node: int = previous_node.values[0]
        branch.insert(0, start_node)

    return branch


def add_branch_information_to_edges_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'branch' information to terminal nodes in a dataframe of graph edges.

    For example:

    | consumer_unique_id | producer_unique_id |
    |--------------------|--------------------|
    | 0                  | 1                  | # 1 is terminal producer node
    | 0                  | 2                  |
    | 0                  | 3                  |
    | 2                  | 4                  | # 4 is terminal producer node
    | 3                  | 5                  |
    | 5                  | 6                  | # 6 is terminal producer node

    | consumer_unique_id | producer_unique_id | branch       |
    |--------------------|--------------------|--------------|
    | 0                  | 1                  | [0, 1]       |
    | 0                  | 2                  | [0, 2]       |
    | 0                  | 3                  | [0, 3]       |
    | 2                  | 4                  | [0, 2, 4]    |
    | 3                  | 5                  | [0, 3, 5]    |
    | 5                  | 6                  | [0, 3, 5, 6] |

    Parameters
    ----------
    df_edges : pd.DataFrame
        A dataframe of graph edges.
        Must contain integer-type columns 'consumer_unique_id' and 'producer_unique_id'.

    Returns
    -------
    pd.DataFrame
        A dataframe of graph nodes with a column 'branch' that contains the branch of nodes that lead to the terminal producer node.
    """
    # initialize empty list to store branches
    branches: list = []

    for _, row in df.iterrows():
        branch: list = trace_branch(df, int(row['producer_unique_id']))
        branches.append({
            'producer_unique_id': int(row['producer_unique_id']),
            'Branch': branch
        })

    return pd.DataFrame(branches)


def create_user_input_columns(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Creates a new column in the 'original' DataFrame where only the
    user-supplied values are kept. The other values are replaced by NaN.

    For instance, given an "original" DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0.5          | 0.5             |
    | 2   | 0.2          | 0.3             |

    and a "user input" DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0            | 0.5             |
    | 2   | 0.2          | 2.1             |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | BurdenIntensity | BurdenIntensity_USER |
    |-----|--------------|-------------------|-----------------|----------------------|
    | 0   | 1            | NaN               | 0.1             | NaN                  |
    | 1   | 0.5          | 0                 | 0.5             | NaN                  |
    | 2   | 0.2          | NaN               | 0.3             | 2.1                  |

    Parameters
    ----------
    df_original : pd.DataFrame
        Original DataFrame.

    df_user_input : pd.DataFrame
        User input DataFrame.
    """
    
    df_merged = pd.merge(
        df_original,
        df_user_input[['UID', 'SupplyAmount', 'BurdenIntensity']],
        on='UID',
        how='left',
        suffixes=('', '_USER')
    )

    for column_name in ['SupplyAmount', 'BurdenIntensity']:
        df_merged[f'{column_name}_USER'] = np.where(
            df_merged[f'{column_name}_USER'] != df_merged[f'{column_name}'],
            df_merged[f'{column_name}_USER'],
            np.nan
        )

    return df_merged


def update_burden_intensity_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the burden intensity when user data is provided.

    For instance, given a DataFrame of the kind:

    | UID | BurdenIntensity | BurdenIntensity_USER |
    |-----|-----------------|----------------------|
    | 0   | 0.1             | NaN                  |
    | 1   | 0.5             | 0.25                 |
    | 2   | 0.3             | NaN                  |

    the function returns a DataFrame of the kind:

    | UID | BurdenIntensity |
    |-----|-----------------|
    | 0   | 0.1             |
    | 1   | 0.25            |
    | 2   | 0.3             |

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Output dataframe.
    """


    df['BurdenIntensity'] = df['BurdenIntensity_USER'].combine_first(df['BurdenIntensity'])
    df = df.drop(columns=['BurdenIntensity_USER'])

    return df


def update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | Branch        |
    |-----|--------------|-------------------|---------------|
    | 0   | 1            | NaN               | NaN           |
    | 1   | 0.5          | 0.25              | [0,1]         |
    | 2   | 0.2          | NaN               | [0,1,2]       |
    | 3   | 0.1          | NaN               | [0,3]         |
    | 4   | 0.1          | 0.18              | [0,1,2,4]     |
    | 5   | 0.05         | NaN               | [0,1,2,4,5]   |
    | 6   | 0.01         | NaN               | [0,1,2,4,5,6] |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount      | Branch        |
    |-----|-------------------|---------------|
    | 0   | 1                 | NaN           |
    | 1   | 0.25              | [0,1]         | NOTA BENE!
    | 2   | 0.2 * (0.25/0.5)  | [0,1,2]       |
    | 3   | 0.1               | [0,3]         |
    | 4   | 0.18              | [0,1,2,4]     | NOTA BENE!
    | 5   | 0.05 * (0.1/0.18) | [0,1,2,4,5]   |
    | 6   | 0.01 * (0.1/0.18) | [0,1,2,4,5,6] |

    Notes
    -----

    As we can see, the function updates production only
    for those nodes upstream of a node with 'production_user':

    - Node 2 is upstream of node 1, which has a 'production_user' value.
    - Node 3 is NOT upstream of node 1. It is upstream of node 0, but node 0 does not have a 'production_user' value.

    As we can see, the function always takes the "most recent"
    'production_user' value upstream of a node:

    - Node 5 is upstream of node 4, which has a 'production_user' value.
    - Node 4 is upstream of node 1, which also has a 'production_user' value.

    In this case, the function takes the 'production_user' value of node 4, not of node 1.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must have the columns 'production', 'production_user' and 'branch'.

    Returns
    -------
    pd.DataFrame
        Output DataFrame.
    """

    df_filtered = df[~df['SupplyAmount_USER'].isna()]
    dict_user_input = df_filtered.set_index('UID').to_dict()['SupplyAmount_USER']
    
    """
    For the example DataFrame from the docstrings above,
    the dict_user_input would be:

    dict_user_input = {
        1: 0.25,
        4: 0.18
    }
    """

    df = df.copy(deep=True)
    def multiplier(row):
        if not isinstance(row['Branch'], list):
            return row['SupplyAmount']
        elif (
            not np.isnan(row['SupplyAmount_USER'])
        ):
            return row['SupplyAmount_USER']
        elif (
            set(dict_user_input.keys()).intersection(row['Branch'])
        ):
            for branch_UID in reversed(row['Branch']):
                if branch_UID in dict_user_input.keys():
                    return row['SupplyAmount'] * dict_user_input[branch_UID]
        else:
            return row['SupplyAmount']

    df['SupplyAmount_EDITED'] = df.apply(multiplier, axis=1)

    df.drop(columns=['SupplyAmount_USER'], inplace=True)
    df['SupplyAmount'] = df['SupplyAmount_EDITED']
    df.drop(columns=['SupplyAmount_EDITED'], inplace=True)

    return df


def update_burden_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the environmental burden of nodes
    by multiplying the burden intensity and the supply amount.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Output dataframe.
    """

    df['Burden(Direct)'] = df['SupplyAmount'] * df['BurdenIntensity']
    return df


def determine_edited_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determines which rows have been edited by the user.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount_USER | BurdenIntensity_USER |
    |-----|-------------------|----------------------|
    | 0   | NaN               | NaN                  |
    | 1   | 0.25              | NaN                  |
    | 2   | NaN               | 2.1                  |
    | 3   | NaN               | NaN                  |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount_USER | BurdenIntensity_USER | Edited? |
    |-----|-------------------|----------------------|---------|
    | 0   | NaN               | NaN                  | False   |
    | 1   | 0.25              | NaN                  | True    |
    | 2   | NaN               | 2.1                  | True    |
    | 3   | NaN               | NaN                  | False   |
    """
    df['Edited?'] = df[['SupplyAmount_USER', 'BurdenIntensity_USER']].notnull().any(axis=1)
    return df
