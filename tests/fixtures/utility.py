import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope="module")
def fixture_determine_edited_rows():
    """
    Fixture returning a factory function to generate test cases for `_determine_edited_rows`.

    The `cases` dictionary contains:
    - `key`: string describing the test scenario
    - `value`: tuple of (input_df, expected_df) where:
        - `input_df`: pandas DataFrame with 'UID', 'SupplyAmount_USER', 'BurdenIntensity_USER', and optional columns
        - `expected_df`: pandas DataFrame with 'UID', 'SupplyAmount_USER', 'BurdenIntensity_USER', 'Edited?', and optional columns
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)
    """
    cases = {
        'basic': (
            pd.DataFrame({
                'UID': [0, 1, 2, 3],
                'SupplyAmount_USER': [np.nan, 0.25, np.nan, np.nan],
                'BurdenIntensity_USER': [np.nan, np.nan, 2.1, np.nan]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2, 3],
                'SupplyAmount_USER': [np.nan, 0.25, np.nan, np.nan],
                'BurdenIntensity_USER': [np.nan, np.nan, 2.1, np.nan],
                'Edited?': [False, True, True, False]
            })
        ),
        'all_nan': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount_USER': [np.nan, np.nan, np.nan],
                'BurdenIntensity_USER': [np.nan, np.nan, np.nan]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount_USER': [np.nan, np.nan, np.nan],
                'BurdenIntensity_USER': [np.nan, np.nan, np.nan],
                'Edited?': [False, False, False]
            })
        ),
        'all_edited': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount_USER': [0.5, np.nan, 1.0],
                'BurdenIntensity_USER': [np.nan, 0.2, 0.3]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount_USER': [0.5, np.nan, 1.0],
                'BurdenIntensity_USER': [np.nan, 0.2, 0.3],
                'Edited?': [True, True, True]
            })
        ),
        'empty': (
            pd.DataFrame(columns=['UID', 'SupplyAmount_USER', 'BurdenIntensity_USER']),
            pd.DataFrame(columns=['UID', 'SupplyAmount_USER', 'BurdenIntensity_USER', 'Edited?'])
        ),
        'mixed_with_additional_columns': (
            pd.DataFrame({
                'UID': [0, 1],
                'SupplyAmount_USER': [np.nan, 0.4],
                'BurdenIntensity_USER': [1.5, np.nan],
                'OtherColumn': ['x', 'y']
            }),
            pd.DataFrame({
                'UID': [0, 1],
                'SupplyAmount_USER': [np.nan, 0.4],
                'BurdenIntensity_USER': [1.5, np.nan],
                'OtherColumn': ['x', 'y'],
                'Edited?': [True, True]
            })
        ),
    }

    def _make_case(case_name):
        if case_name not in cases:
            raise ValueError(f"No test case defined for {case_name}")
        return cases[case_name]

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_create_user_input_columns():
    """
    Fixture returning a factory function to generate test cases for `_create_user_input_columns`.

    The `cases` dictionary contains:
    - `key`: string describing the test scenario
    - `value`: tuple of (input_data, expected_output) where:
        - `input_data`: tuple of (df_original, df_user_input), each a pandas DataFrame with 'UID', 'SupplyAmount', 'BurdenIntensity', and optional columns
        - `expected_output`: pandas DataFrame with 'UID', 'SupplyAmount', 'SupplyAmount_USER', 'BurdenIntensity', 'BurdenIntensity_USER', and optional columns
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)
    """
    cases = {
        'basic': (
            (
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [1, 0.5, 0.2],
                    'BurdenIntensity': [0.1, 0.5, 0.3]
                }),
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [1, 0, 0.2],
                    'BurdenIntensity': [0.1, 0.5, 2.1]
                })
            ),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [1, 0.5, 0.2],
                'SupplyAmount_USER': [np.nan, 0, np.nan],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [np.nan, np.nan, 2.1]
            })
        ),
        'no_changes': (
            (
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [1, 0.5, 0.2],
                    'BurdenIntensity': [0.1, 0.5, 0.3]
                }),
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [1, 0.5, 0.2],
                    'BurdenIntensity': [0.1, 0.5, 0.3]
                })
            ),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [1, 0.5, 0.2],
                'SupplyAmount_USER': [np.nan, np.nan, np.nan],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [np.nan, np.nan, np.nan]
            })
        ),
        'all_changed': (
            (
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [1, 0.5, 0.2],
                    'BurdenIntensity': [0.1, 0.5, 0.3]
                }),
                pd.DataFrame({
                    'UID': [0, 1, 2],
                    'SupplyAmount': [2, 0.7, 0.1],
                    'BurdenIntensity': [0.2, 0.4, 0.6]
                })
            ),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [1, 0.5, 0.2],
                'SupplyAmount_USER': [2, 0.7, 0.1],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [0.2, 0.4, 0.6]
            })
        ),
        'empty': (
            (
                pd.DataFrame(columns=['UID', 'SupplyAmount', 'BurdenIntensity']),
                pd.DataFrame(columns=['UID', 'SupplyAmount', 'BurdenIntensity'])
            ),
            pd.DataFrame(columns=['UID', 'SupplyAmount', 'SupplyAmount_USER', 'BurdenIntensity', 'BurdenIntensity_USER'])
        ),
        'with_additional_columns': (
            (
                pd.DataFrame({
                    'UID': [0, 1],
                    'SupplyAmount': [1, 0.5],
                    'BurdenIntensity': [0.1, 0.5],
                    'OtherColumn': ['a', 'b']
                }),
                pd.DataFrame({
                    'UID': [0, 1],
                    'SupplyAmount': [1, 0.4],
                    'BurdenIntensity': [0.2, 0.5]
                })
            ),
            pd.DataFrame({
                'UID': [0, 1],
                'SupplyAmount': [1, 0.5],
                'SupplyAmount_USER': [np.nan, 0.4],
                'BurdenIntensity': [0.1, 0.5],
                'BurdenIntensity_USER': [0.2, np.nan],
                'OtherColumn': ['a', 'b']
            })
        ),
    }

    def _make_case(case_name):
        if case_name not in cases:
            raise ValueError(f"No test case defined for {case_name}")
        return cases[case_name]

    return _make_case, list(cases.keys())