import pandas as pd
import numpy as np


def _create_user_input_columns(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Given two dataframes with at least the columns `'UID', 'SupplyAmount', 'BurdenIntensity'`,
    returns a dataframe with additional columns 'SupplyAmount_USER', 'BurdenIntensity_USER'`
    where only the user-provided values are kept. All other values in these new columns are replaced by `NaN`.

    For instance, given an 'original' DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0.5          | 0.5             |
    | 2   | 0.2          | 0.3             |

    and a "user input" DataFrame of the kind (modified values highlighted):

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | **0**        | 0.5             |
    | 2   | 0.2          | **2.1**         |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | BurdenIntensity | BurdenIntensity_USER |
    |-----|--------------|-------------------|-----------------|----------------------|
    | 0   | 1            | NaN               | 0.1             | NaN                  |
    | 1   | 0.5          | **0**             | 0.5             | NaN                  |
    | 2   | 0.2          | NaN               | 0.3             | **2.1**              |

    Parameters
    ----------
    df_original : pd.DataFrame
        Original DataFrame.   
        Must have at least columns `'UID', 'SupplyAmount', 'BurdenIntensity'`.
    df_user_input : pd.DataFrame
        User input DataFrame.  
        Must have at least columns `'UID', 'SupplyAmount', 'BurdenIntensity'`.

    Returns
    -------
    pd.DataFrame
        Output DataFrame.

    Raises
    ------
    ValueError
        If the set of UIDs in `df_original` and `df_user_input` do
        not match exactly.
    """
    uids_original = set(df_original['UID'])
    uids_user_input = set(df_user_input['UID'])

    if uids_original != uids_user_input:
        raise ValueError("UIDs in original and user input dataframes do not match.")

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


def _update_burden_intensity_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe with columns `'BurdenIntensity', 'BurdenIntensity_USER'`,
    overwrites the values in `BurdenIntensity` whenever values are provided in `BurdenIntensity_USER`.

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
        Input DataFrame.

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

    | UID | SupplyAmount      | Branch        | Updated? |
    |-----|-------------------|---------------|----------|
    | 0   | 1                 | NaN           | False    |
    | 1   | 0.25              | [0,1]         | False    |
    | 2   | 0.2 * (0.25/0.5)  | [0,1,2]       | True     |
    | 3   | 0.1               | [0,3]         | False    |
    | 4   | 0.18              | [0,1,2,4]     | False    |
    | 5   | 0.05 * (0.18/0.1) | [0,1,2,4,5]   | True     |
    | 6   | 0.01 * (0.18/0.1) | [0,1,2,4,5,6] | True     |

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
    df_filtered = df.dropna(subset=['SupplyAmount_USER'])
    dict_user_input = df_filtered.set_index('UID')['SupplyAmount_USER'].to_dict()
    dict_original_amount = df.set_index('UID')['SupplyAmount'].to_dict()
    
    df_copy = df.copy()

    def get_new_values(row) -> tuple[float, bool]:
        if not pd.isna(row['SupplyAmount_USER']):
            return (row['SupplyAmount_USER'], False)
        
        elif not isinstance(row['Branch'], list):
            return (row['SupplyAmount'], False)
        
        elif set(dict_user_input.keys()).intersection(row['Branch']):
            for branch_UID in reversed(row['Branch']):
                if branch_UID in dict_user_input:
                    original_upstream = dict_original_amount[branch_UID]
                    user_upstream = dict_user_input[branch_UID]

                    if original_upstream == 0:
                        return (0, True) 
                    else:
                        new_amount = row['SupplyAmount'] * (user_upstream / original_upstream)
                        return (new_amount, True) 
        
        else:
            return (row['SupplyAmount'], False)

    results = df_copy.apply(get_new_values, axis=1)
    df_copy[['SupplyAmount_EDITED', 'Updated?']] = pd.DataFrame(results.tolist(), index=df_copy.index)

    df_copy['SupplyAmount'] = df_copy['SupplyAmount_EDITED']
    df_copy.drop(columns=['SupplyAmount_USER', 'SupplyAmount_EDITED'], inplace=True)
    
    return df_copy


def _update_burden_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
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


def _determine_edited_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe with at least columns `'SupplyAmount_USER', 'BurdenIntensity_USER'`,
    returns a DataFrame with a new column that indicates whether a row has been edited by the user.

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