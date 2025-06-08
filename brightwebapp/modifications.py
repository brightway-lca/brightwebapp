import pandas as pd


def _update_burden_intensity_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns `UID`, `BurdenIntensity`, and `BurdenIntensity_USER`,
    updates the `BurdenIntensity` of all nodes with user-defined `BurdenIntensity_USER`. 

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


def _update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns `UID`, `SupplyAmount`, `SupplyAmount_USER` and `Branch`,
    updates the `SupplyAmount` of all nodes which are upstream
    of a node with user-defined `SupplyAmount_USER`.

    For example, given a supply chain graph of the kind:

    ```mermaid
    graph TD
    1 -->|0.5→<b>0.25</b>| 0
    3 -->|0.1| 0
    2 -->|"=0.2*(0.25/0.5)"| 1
    4 -->|0.1→<b>0.2</b>| 2
    5 -->|"=0.05*(0.2/0.1)"| 4
    6 -->|"=0.01*(0.2/0.1)"| 5

    style 0 fill:#FFFFFF
    style 3 fill:#FFFFFF
    style 1 fill:#FFCCCB
    style 2 fill:#FFCCCB
    style 4 fill:#C3FDB8
    style 5 fill:#C3FDB8
    style 6 fill:#C3FDB8
    ```

    which can be represented as a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | Branch        |
    |-----|--------------|-------------------|---------------|
    | 0   | 1            | NaN               | NaN           |
    | 1   | 0.5          | 0.25              | [0,1]         |
    | 2   | 0.2          | NaN               | [0,1,2]       |
    | 3   | 0.1          | NaN               | [0,3]         |
    | 4   | 0.1          | 0.2               | [0,1,2,4]     |
    | 5   | 0.05         | NaN               | [0,1,2,4,5]   |
    | 6   | 0.01         | NaN               | [0,1,2,4,5,6] |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount        | Branch        |
    |-----|---------------------|---------------|
    | 0   | 1                   | NaN           |
    | 1   | 0.25                | [0,1]         | NOTA BENE!
    | 2   | 0.2 * (0.25/0.5)    | [0,1,2]       |
    | 3   | 0.1                 | [0,3]         |
    | 4   | 0.18                | [0,1,2,4]     | NOTA BENE!
    | 5   | 0.05 * (0.18 / 0.1) | [0,1,2,4,5]   | 
    | 6   | 0.01 * (0.18 / 0.1) | [0,1,2,4,5,6] |
    
    Notes
    -----
    As we can see, the function updates production only
    for those nodes upstream of a node with `SupplyAmount_USER`:

    - Node `2` is upstream of node `1`, which has a `SupplyAmount_USER` value.
    - Node `3` is NOT upstream of node `1`. It is upstream of node `0`, but node `0` does not have a `SupplyAmount_USER` value.

    As we can see, the function always takes the "most recent"
    `SupplyAmount_USER` value upstream of a node:

    - Node `5` is upstream of node `4`, which has a `SupplyAmount_USER` value.
    - Node `4` is upstream of node `1`, which also has a `SupplyAmount_USER` value.

    In this case, the function takes the `SupplyAmount_USER` value of node `4`, not of node `1`.

    Parameters
    ----------
    df : `pd.DataFrame`
        Input DataFrame. Must have the columns `UID`, `SupplyAmount`, `SupplyAmount_USER` and `Branch`.

    Returns
    -------
    `pd.DataFrame`
        Output DataFrame with updated `SupplyAmount` column.
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


def _update_burden_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the environmental burden of nodes
    by multiplying the burden intensity and the supply amount.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0.5          | 0.25            |
    | 2   | 0.2          | 0.3             |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity | Burden(Direct) |
    |-----|--------------|-----------------|-----------------|
    | 0   | 1            | 0.1             | 0.1             |
    | 1   | 0.5          | 0.25            | 0.125           |
    | 2   | 0.2          | 0.3             | 0.06            |

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