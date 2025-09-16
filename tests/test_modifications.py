import pytest
from pandas.testing import assert_frame_equal

import pandas as pd
import numpy as np

from brightwebapp.modifications import (
    _create_user_input_columns,
    _update_burden_intensity_based_on_user_data,
    _update_burden_based_on_user_data,
    _determine_edited_rows,
    _update_production_based_on_user_data
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

@pytest.fixture
def base_df() -> pd.DataFrame:
    """Provides the main DataFrame used in the docstring for tests."""
    data = {
        'UID': [0, 1, 2, 3, 4, 5, 6],
        'SupplyAmount': [1.0, 0.5, 0.2, 0.1, 0.1, 0.05, 0.01],
        'SupplyAmount_USER': [np.nan, 0.25, np.nan, np.nan, 0.18, np.nan, np.nan],
        'Branch': [
            np.nan,
            [0, 1],
            [0, 1, 2],
            [0, 3],
            [0, 1, 2, 4],
            [0, 1, 2, 4, 5],
            [0, 1, 2, 4, 5, 6]
        ]
    }
    return pd.DataFrame(data)


class TestUpdateProductionBasedOnUserData:
    """
    Test suite for the `_update_production_based_on_user_data` function.
    """

    def test_main_scenario_from_docstring(self, base_df):
        """
        Tests the primary use case described in the function's docstring.
        It verifies direct updates, downstream propagation, and the "most recent" upstream rule.
        """
        expected_data = {
            'UID': [0, 1, 2, 3, 4, 5, 6],
            'SupplyAmount': [
                1.0,                     # Unchanged root
                0.25,                    # Direct user update
                0.1,                     # Scaled by UID 1
                0.1,                     # Unaffected branch
                0.18,                    # Direct user update
                0.09,                    # Scaled by UID 4 (most recent)
                0.018                    # Scaled by UID 4 (most recent)
            ],
            'Branch': [
                np.nan,
                [0, 1],
                [0, 1, 2],
                [0, 3],
                [0, 1, 2, 4],
                [0, 1, 2, 4, 5],
                [0, 1, 2, 4, 5, 6]
            ],
            'Updated?': [False, False, True, False, False, True, True]
        }
        expected_df = pd.DataFrame(expected_data)
        result_df = _update_production_based_on_user_data(base_df)
        assert_frame_equal(result_df, expected_df, atol=1e-9)


    def test_no_user_input_makes_no_changes(self, base_df):
        """
        Tests that if the 'SupplyAmount_USER' column is all NaN, the function
        returns the original 'SupplyAmount' values unchanged.
        """
        df_no_user_input = base_df.copy()
        df_no_user_input['SupplyAmount_USER'] = np.nan
        
        # Create the expected DataFrame by dropping the user column...
        expected_df = df_no_user_input.drop(columns=['SupplyAmount_USER'])
        # ...and adding the new 'Updated?' column with all False values.
        expected_df['Updated?'] = False

        result_df = _update_production_based_on_user_data(df_no_user_input)

        assert_frame_equal(result_df, expected_df)


    def test_division_by_zero_upstream_sets_downstream_to_zero(self):
        """
        Tests the critical edge case where an upstream node has an original
        SupplyAmount of 0. All downstream nodes should be updated to 0.
        """
        data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 0.0, 5.0],
            'SupplyAmount_USER': [np.nan, 2.0, np.nan],
            'Branch': [np.nan, [0, 1], [0, 1, 2]]
        }
        df = pd.DataFrame(data)

        expected_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 2.0, 0.0],
            'Branch': [np.nan, [0, 1], [0, 1, 2]],
            # FIX: Added 'Updated?' column with correct boolean values
            'Updated?': [False, False, True]
        }
        expected_df = pd.DataFrame(expected_data)

        result_df = _update_production_based_on_user_data(df)

        assert_frame_equal(result_df, expected_df)


    def test_user_input_on_root_node_propagates_correctly(self):
        """
        Tests that if the root node (UID 0) has a user value, it correctly
        propagates to all its direct and indirect children.
        """
        data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [100.0, 50.0, 20.0],
            'SupplyAmount_USER': [50.0, np.nan, np.nan],
            'Branch': [np.nan, [0, 1], [0, 2]]
        }
        df = pd.DataFrame(data)
        
        expected_data = {
            'UID': [0, 1, 2],
            'SupplyAmount': [
                50.0,       # Direct update
                25.0,       # Scaled by root
                10.0        # Scaled by root
            ],
            'Branch': [np.nan, [0, 1], [0, 2]],
            # FIX: Added 'Updated?' column with correct boolean values
            'Updated?': [False, True, True]
        }
        expected_df = pd.DataFrame(expected_data)
        
        result_df = _update_production_based_on_user_data(df)
        
        assert_frame_equal(result_df, expected_df, atol=1e-9)


class TestDetermineEditedRows:
    """
    Test suite for the _determine_edited_rows function.
    """

    def test_basic_case_mixed_edits(self):
        """
        Tests the standard case with a mix of edited and unedited rows,
        mirroring the function's docstring.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2, 3],
            'SupplyAmount_USER': [np.nan, 0.25, np.nan, np.nan],
            'BurdenIntensity_USER': [np.nan, np.nan, 2.1, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2, 3],
            'SupplyAmount_USER': [np.nan, 0.25, np.nan, np.nan],
            'BurdenIntensity_USER': [np.nan, np.nan, 2.1, np.nan],
            'Edited?': [False, True, True, False]
        })
        result_df = _determine_edited_rows(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_no_edits(self):
        """
        Tests that all rows are marked as False when no user edits are present.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount_USER': [np.nan, np.nan],
            'BurdenIntensity_USER': [np.nan, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount_USER': [np.nan, np.nan],
            'BurdenIntensity_USER': [np.nan, np.nan],
            'Edited?': [False, False]
        })
        result_df = _determine_edited_rows(input_df)
        assert_frame_equal(result_df, expected_df)
        

    def test_both_columns_edited_in_one_row(self):
        """
        Tests that a row is correctly marked as True if both user columns have values.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount_USER': [np.nan, 5.0],
            'BurdenIntensity_USER': [np.nan, 1.5]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount_USER': [np.nan, 5.0],
            'BurdenIntensity_USER': [np.nan, 1.5],
            'Edited?': [False, True]
        })
        result_df = _determine_edited_rows(input_df)
        assert_frame_equal(result_df, expected_df)
        

    def test_empty_dataframe(self):
        """
        Tests that the function correctly handles an empty DataFrame.
        """
        input_df = pd.DataFrame({
            'SupplyAmount_USER': pd.Series([], dtype='float'),
            'BurdenIntensity_USER': pd.Series([], dtype='float')
        })
        expected_df = pd.DataFrame({
            'SupplyAmount_USER': pd.Series([], dtype='float'),
            'BurdenIntensity_USER': pd.Series([], dtype='float'),
            'Edited?': pd.Series([], dtype='bool')
        })
        result_df = _determine_edited_rows(input_df)
        assert_frame_equal(result_df, expected_df)


class TestUpdateBurden:
    """
    Test suite for the _update_burden_based_on_user_data function.
    """

    def test_basic_calculation(self):
        """
        Tests if the 'Burden(Direct)' column is calculated correctly with standard positive numbers.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 5.0, 100.0],
            'BurdenIntensity': [0.5, 2.0, 0.1]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 5.0, 100.0],
            'BurdenIntensity': [0.5, 2.0, 0.1],
            'Burden(Direct)': [5.0, 10.0, 10.0]  # 10*0.5=5, 5*2=10, 100*0.1=10
        })

        result_df = _update_burden_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_calculation_with_zeros(self):
        """
        Tests that the multiplication correctly results in zero if one of the factors is zero.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 0.0, 50.0],
            'BurdenIntensity': [0.5, 100.0, 0.0]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'SupplyAmount': [10.0, 0.0, 50.0],
            'BurdenIntensity': [0.5, 100.0, 0.0],
            'Burden(Direct)': [5.0, 0.0, 0.0]  # 10*0.5=5, 0*100=0, 50*0=0
        })

        result_df = _update_burden_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)

    
    def test_empty_dataframe(self):
        """
        Tests that the function correctly handles an empty DataFrame.
        """
        input_df = pd.DataFrame({
            'SupplyAmount': pd.Series([], dtype='float'),
            'BurdenIntensity': pd.Series([], dtype='float')
        })
        expected_df = pd.DataFrame({
            'SupplyAmount': pd.Series([], dtype='float'),
            'BurdenIntensity': pd.Series([], dtype='float'),
            'Burden(Direct)': pd.Series([], dtype='float')
        })

        result_df = _update_burden_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


class TestUpdateBurdenIntensity:
    """
    Tests the `_update_burden_intensity_based_on_user_data` function.
    """

    def test_basic_case_with_mixed_overrides(self):
        """
        Tests the standard case where some values are overridden and others are not.
        This mirrors the example in the function's docstring.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [0.1, 0.5, 0.3],
            'BurdenIntensity_USER': [np.nan, 0.25, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [0.1, 0.25, 0.3]
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_no_overrides_provided(self):
        """
        Tests that the original data is preserved when the `_USER` column is all NaN.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [0.1, 0.5, 0.3],
            'BurdenIntensity_USER': [np.nan, np.nan, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [0.1, 0.5, 0.3]
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_all_values_overridden(self):
        """
        Tests that all original values are replaced when the `_USER` column is fully populated.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [0.1, 0.5, 0.3],
            'BurdenIntensity_USER': [1.1, 1.5, 1.3]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1, 2],
            'BurdenIntensity': [1.1, 1.5, 1.3]
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_zero_as_override_value(self):
        """
        Tests that `0` is correctly treated as a valid override value.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1],
            'BurdenIntensity': [0.1, 0.5],
            'BurdenIntensity_USER': [0.0, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1],
            'BurdenIntensity': [0.0, 0.5]
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_empty_dataframe(self):
        """
        Tests that the function correctly handles an empty DataFrame.
        """
        input_df = pd.DataFrame({
            'UID': pd.Series([], dtype='int'),
            'BurdenIntensity': pd.Series([], dtype='float'),
            'BurdenIntensity_USER': pd.Series([], dtype='float')
        })
        expected_df = pd.DataFrame({
            'UID': pd.Series([], dtype='int'),
            'BurdenIntensity': pd.Series([], dtype='float')
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df)


    def test_preserves_other_columns(self):
        """
        Tests that other columns in the DataFrame are unaffected.
        """
        input_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount': [100, 200], # This column should be preserved
            'BurdenIntensity': [0.1, 0.5],
            'BurdenIntensity_USER': [0.9, np.nan]
        })
        expected_df = pd.DataFrame({
            'UID': [0, 1],
            'SupplyAmount': [100, 200],
            'BurdenIntensity': [0.9, 0.5]
        })

        result_df = _update_burden_intensity_based_on_user_data(input_df)
        assert_frame_equal(result_df, expected_df[result_df.columns])


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