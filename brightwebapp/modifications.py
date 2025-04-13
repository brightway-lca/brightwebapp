import pandas as pd

def _update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    
    For instance, given a DataFrame of the kind:

    | `UID` | `SupplyAmount` | `SupplyAmount_USER` | `Branch`        |
    |-------|----------------|---------------------|-----------------|
    | `0`   | `1`            | `NaN`               | `NaN`           |
    | `1`   | `0.5`          | `0.25`              | `[0,1]`         |
    | `2`   | `0.2`          | `NaN`               | `[0,1,2]`       |
    | `3`   | `0.1`          | `NaN`               | `[0,3]`         |
    | `4`   | `0.1`          | `0.18`              | `[0,1,2,4]`     |
    | `5`   | `0.05`         | `NaN`               | `[0,1,2,4,5]`   |
    | `6`   | `0.01`         | `NaN`               | `[0,1,2,4,5,6]` |

    the function returns a DataFrame of the kind:

    | `UID` | `SupplyAmount`      | `Branch`        |
    |-------|---------------------|-----------------|
    | `0`   | `1`                 | `NaN`           |
    | `1`   | `0.25`              | `[0,1]`         | NOTA BENE!
    | `2`   | `0.2 * (0.25/0.5)`  | `[0,1,2]`       |
    | `3`   | `0.1`               | `[0,3]`         |
    | `4`   | `0.18`              | `[0,1,2,4]`     | NOTA BENE!
    | `5`   | `0.05 * (0.18 / 0.1)` | `[0,1,2,4,5]`   | # Corrected calculation based on logic
    | `6`   | `0.01 * (0.18 / 0.1)` | `[0,1,2,4,5,6]` | # Corrected calculation based on logic


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

    Warnings
    --------

    ![Diagram](../_media/user_input_table.svg)

    We assume:

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