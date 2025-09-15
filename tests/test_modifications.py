import pytest
from pandas.testing import assert_frame_equal

import pandas as pd
import numpy as np

from brightwebapp.modifications import (
    _create_user_input_columns
)

@pytest.fixture
def df_original() -> pd.DataFrame:
    data = {
        'UID': [0, 1, 2],
        'SupplyAmount': [1.0, 0.5, 0.2],
        'BurdenIntensity': [0.1, 0.5, 0.3],
        'OtherColumn': ['A', 'B', 'C']  # To ensure other columns are preserved
    }
    return pd.DataFrame(data)


class TestCreateUserInputColumns:
    """
    Tests the `_create_user_input_columns` function.
    """

    def test_basic_case_from_docstring(self, df_original):
        """
        Tests the primary use case where some values are changed by the user.
        This test mirrors the example in the function docstrings.
        """
        user_input_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [1.0, 0.0, 0.2],    # Changed for UID 1
            'BurdenIntensity': [0.1, 0.5, 2.1], # Changed for UID 2
        }
        df_user_input = pd.DataFrame(user_input_data)
        expected_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [1.0, 0.5, 0.2],
            'SupplyAmount_USER': [np.nan, 0.0, np.nan],
            'BurdenIntensity': [0.1, 0.5, 0.3],
            'BurdenIntensity_USER': [np.nan, np.nan, 2.1],
            'OtherColumn': ['A', 'B', 'C'],
        }
        expected_df = pd.DataFrame(expected_data)
        result_df = _create_user_input_columns(df_original, df_user_input)
        assert_frame_equal(result_df, expected_df[result_df.columns])


    def test_no_changes(self, df_original):
        """
        Tests the case where the user input is identical to the original data.
        The resulting `_USER` columns should be entirely NaN.
        """
        df_user_input = df_original.copy()
        expected_df = df_original.copy()
        expected_df['SupplyAmount_USER'] = np.nan
        expected_df['BurdenIntensity_USER'] = np.nan

        result_df = _create_user_input_columns(df_original, df_user_input)
        assert_frame_equal(result_df, expected_df[result_df.columns])


    def test_all_values_changed(self, df_original):
        """
        Tests the case where all user-editable values have been changed.
        The `_USER` columns should contain all the new values, with no NaNs.
        """
        user_input_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 5.0, 2.0],
            'BurdenIntensity': [1.1, 5.5, 3.3],
        }
        df_user_input = pd.DataFrame(user_input_data)
        expected_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [1.0, 0.5, 0.2],
            'SupplyAmount_USER': [10.0, 5.0, 2.0],
            'BurdenIntensity': [0.1, 0.5, 0.3],
            'BurdenIntensity_USER': [1.1, 5.5, 3.3],
            'OtherColumn': ['A', 'B', 'C'],
        }
        expected_df = pd.DataFrame(expected_data)
        result_df = _create_user_input_columns(df_original, df_user_input)
        assert_frame_equal(result_df, expected_df[result_df.columns])

    # ---

    def test_empty_dataframes(self):
        """
        Tests that the function handles empty DataFrames correctly.
        """
        empty_df = pd.DataFrame({'UID': [], 'SupplyAmount': [], 'BurdenIntensity': []})
        expected_df = pd.DataFrame({
            'UID': [],
            'SupplyAmount': [],
            'BurdenIntensity': [],
            'SupplyAmount_USER': [],
            'BurdenIntensity_USER': [],
        })

        result_df = _create_user_input_columns(empty_df, empty_df.copy())
        assert_frame_equal(result_df, expected_df, check_dtype=False)


    def test_raises_error_if_user_input_misses_uids(self, df_original):
        """
        Tests that a ValueError is raised if the user input is missing UIDs.
        """
        user_input_data = { # Missing UID 1
            'UID': [0, 2],
            'SupplyAmount': [10.0, 0.2],
            'BurdenIntensity': [0.1, 3.0],
        }
        df_user_input = pd.DataFrame(user_input_data)

        with pytest.raises(ValueError, match="UIDs in original and user input dataframes do not match."):
            _create_user_input_columns(df_original, df_user_input)


    def test_raises_error_if_user_input_has_extra_uids(self, df_original):
        """
        Tests that a ValueError is raised if the user input has extra UIDs.
        """
        user_input_data = { # Extra UID 99
            'UID': [0, 1, 2, 99],
            'SupplyAmount': [1.0, 0.0, 0.2, 100.0],
            'BurdenIntensity': [0.1, 0.5, 2.1, 100.0],
        }
        df_user_input = pd.DataFrame(user_input_data)

        with pytest.raises(ValueError, match="UIDs in original and user input dataframes do not match."):
            _create_user_input_columns(df_original, df_user_input)


    def test_nan_handling(self):
        """
        Tests how the function handles NaN values in various combinations.
        Note: `np.nan != np.nan` evaluates to `True`, which this test accounts for.
        """
        # Arrange
        original_data = {
            'UID': [1, 2, 3, 4],
            'SupplyAmount':    [1.0, np.nan, 3.0,    np.nan],
            'BurdenIntensity': [10.0, 20.0,   np.nan, np.nan],
        }
        df_original = pd.DataFrame(original_data)
        user_input_data = {
            'UID': [1, 2, 3, 4],
            'SupplyAmount':    [np.nan, 2.0, 3.0,    np.nan],
            'BurdenIntensity': [10.0, 20.0,   30.0,   np.nan],
        }
        df_user_input = pd.DataFrame(user_input_data)
        expected_data = {
            'UID': [1, 2, 3, 4],
            'SupplyAmount': [1.0, np.nan, 3.0, np.nan],
            'BurdenIntensity': [10.0, 20.0, np.nan, np.nan],
            'SupplyAmount_USER': [np.nan, 2.0, np.nan, np.nan],
            'BurdenIntensity_USER': [np.nan, np.nan, 30.0, np.nan],
        }
        expected_df = pd.DataFrame(expected_data)

        result_df = _create_user_input_columns(df_original, df_user_input)
        assert_frame_equal(result_df, expected_df[result_df.columns])