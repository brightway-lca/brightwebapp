import pandas as pd
import numpy as np


def _determine_edited_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with columns `SupplyAmount_USER` and `BurdenIntensity_USER`,
    adds a new column `Edited?` that indicates whether the user has edited
    the values in the `SupplyAmount_USER` or `BurdenIntensity_USER` columns.

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

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    
    Returns
    -------
    pd.DataFrame
        Output DataFrame with an additional column `Edited?`.
    """

    df['Edited?'] = df[['SupplyAmount_USER', 'BurdenIntensity_USER']].notnull().any(axis=1)
    return df


def _create_user_input_columns(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Given an "original" DataFrame and a "user input" DataFrame, both of which have at least the columns
    `UID`, `SupplyAmount`, and `BurdenIntensity`, this function
    rreates a new column in the "original" DataFrame where only the
    user-supplied values are kept. All other values are replaced by `NaN`.

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