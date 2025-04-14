import pytest
import numpy as np
import pandas as pd


@pytest.fixture(scope="module")
def fixture_update_burden_intensity():
    """
    Fixture returning a factory function to generate test cases for `_update_burden_intensity_based_on_user_data`.

    The `cases` dictionary contains:
    - `key`: string describing the test scenario
    - `value`: tuple of (input_df, expected_df) where:
        - `input_df`: pandas DataFrame with 'UID', 'BurdenIntensity', 'BurdenIntensity_USER', and optional columns
        - `expected_df`: pandas DataFrame with expected 'UID', 'BurdenIntensity', and preserved additional columns
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)
    """
    cases = {
        'basic': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [np.nan, 0.25, np.nan]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.1, 0.25, 0.3]
            })
        ),
        'all_user_nan': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [np.nan, np.nan, np.nan]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.1, 0.5, 0.3]
            })
        ),
        'all_user_provided': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.1, 0.5, 0.3],
                'BurdenIntensity_USER': [0.2, 0.4, 0.6]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'BurdenIntensity': [0.2, 0.4, 0.6]
            })
        ),
        'empty': (
            pd.DataFrame(columns=['UID', 'BurdenIntensity', 'BurdenIntensity_USER']),
            pd.DataFrame(columns=['UID', 'BurdenIntensity'])
        ),
        'with_additional_columns': (
            pd.DataFrame({
                'UID': [0, 1],
                'BurdenIntensity': [0.1, 0.5],
                'BurdenIntensity_USER': [np.nan, 0.25],
                'OtherColumn': ['a', 'b']
            }),
            pd.DataFrame({
                'UID': [0, 1],
                'BurdenIntensity': [0.1, 0.25],
                'OtherColumn': ['a', 'b']
            })
        ),
    }

    def _make_case(case_name):
        if case_name not in cases:
            raise ValueError(f"No test case defined for {case_name}")
        return cases[case_name]

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_update_burden():
    """
    Fixture returning a factory function to generate test cases for `_update_burden_intensity_based_on_user_data`.

    The `cases` dictionary contains:
    - `key`: string describing the test scenario
    - `value`: tuple of (input_df, expected_df) where:
        - `input_df`: pandas DataFrame with 'UID', 'BurdenIntensity', 'BurdenIntensity_USER', and optional columns
        - `expected_df`: pandas DataFrame with expected 'UID', 'BurdenIntensity', and preserved additional columns
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)
    """
    cases = {
        'basic': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [1, 0.5, 0.2],
                'BurdenIntensity': [0.1, 0.25, 0.3]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [1, 0.5, 0.2],
                'BurdenIntensity': [0.1, 0.25, 0.3],
                'Burden(Direct)': [0.1, 0.125, 0.06]
            })
        ),
        'zero_values': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [0, 0.5, 0],
                'BurdenIntensity': [0.1, 0, 0]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [0, 0.5, 0],
                'BurdenIntensity': [0.1, 0, 0],
                'Burden(Direct)': [0.0, 0.0, 0.0]
            })
        ),
        'negative_values': (
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [-1, 0.5, -0.2],
                'BurdenIntensity': [0.1, -0.25, -0.3]
            }),
            pd.DataFrame({
                'UID': [0, 1, 2],
                'SupplyAmount': [-1, 0.5, -0.2],
                'BurdenIntensity': [0.1, -0.25, -0.3],
                'Burden(Direct)': [-0.1, -0.125, 0.06]
            })
        ),
        'empty': (
            pd.DataFrame(columns=['UID', 'SupplyAmount', 'BurdenIntensity']),
            pd.DataFrame(columns=['UID', 'SupplyAmount', 'BurdenIntensity', 'Burden(Direct)'])
        ),
        'with_additional_columns': (
            pd.DataFrame({
                'UID': [0, 1],
                'SupplyAmount': [1, 0.5],
                'BurdenIntensity': [0.1, 0.25],
                'OtherColumn': ['a', 'b']
            }),
            pd.DataFrame({
                'UID': [0, 1],
                'SupplyAmount': [1, 0.5],
                'BurdenIntensity': [0.1, 0.25],
                'OtherColumn': ['a', 'b'],
                'Burden(Direct)': [0.1, 0.125]
            })
        ),
    }

    def _make_case(case_name):
        if case_name not in cases:
            raise ValueError(f"No test case defined for {case_name}")
        return cases[case_name]

    return _make_case, list(cases.keys())