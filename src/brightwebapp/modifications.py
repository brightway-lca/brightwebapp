import pandas as pd
import numpy as np


def _create_user_input_columns(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Given two dataframes with columns `'UID', 'SupplyAmount', 'BurdenIntensity'`,
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