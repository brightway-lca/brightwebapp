import pytest
import pandas.testing as pdt

from .fixtures.utility import (
    fixture_determine_edited_rows,
    fixture_create_user_input_columns
)

from brightwebapp.utility import (
    _determine_edited_rows,
    _create_user_input_columns
)

@pytest.mark.parametrize("case_name", [
    'basic',
    'all_nan',
    'all_edited',
    'empty',
    'mixed_with_additional_columns'
])
def test_determine_edited_rows(case_name, fixture_determine_edited_rows):
    _make_case, _ = fixture_determine_edited_rows
    input_df, expected_df = _make_case(case_name)
    result_df = _determine_edited_rows(input_df)
    pdt.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("case_name", [
    'basic',
    'no_changes',
    'all_changed',
    'empty',
    'with_additional_columns'
])
def test_create_user_input_columns(case_name, fixture_create_user_input_columns):
    _make_case, _ = fixture_create_user_input_columns
    (df_original, df_user_input), expected_df = _make_case(case_name)
    result_df = _create_user_input_columns(df_original, df_user_input)
    pdt.assert_frame_equal(result_df, expected_df)