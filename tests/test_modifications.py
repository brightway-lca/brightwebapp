import pytest
import pandas.testing as pdt

from .fixtures.modifications import (
    fixture_update_burden_intensity,
    fixture_update_burden
)

from brightwebapp.modifications import (
    _update_burden_intensity_based_on_user_data,
    _update_production_based_on_user_data,
    _update_burden_based_on_user_data
)

@pytest.mark.parametrize("case_name", [
    'basic',
    'all_user_nan',
    'all_user_provided',
    'empty',
    'with_additional_columns'
])
def test_update_burden_intensity(case_name, fixture_update_burden_intensity):
    _make_case, _ = fixture_update_burden_intensity
    input_df, expected_df = _make_case(case_name)
    result_df = _update_burden_intensity_based_on_user_data(input_df)
    pdt.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("case_name", [
    'basic',
    'zero_values',
    'negative_values',
    'empty',
    'with_additional_columns'
])
def test_update_burden(case_name, fixture_update_burden):
    _make_case, _ = fixture_update_burden
    input_df, expected_df = _make_case(case_name)
    result_df = _update_burden_based_on_user_data(input_df)
    pdt.assert_frame_equal(result_df, expected_df)