import unittest
import plotly.graph_objects as go

from brightwebapp.visualization import (
    create_plotly_figure_piechart
)

class TestCreatePlotlyFigurePiechart(unittest.TestCase):
    """
    Test suite for the `create_plotly_figure_piechart` function.
    """

    def test_standard_input(self):
        """
        Tests the `create_plotly_figure_piechart` function
        with a typical dictionary containing all scopes.
        """
        data = {'Scope 1': 10, 'Scope 2': 20, 'Scope 3': 70}
        fig = create_plotly_figure_piechart(data)

        # 1. Check if the returned object is the correct type
        self.assertIsInstance(fig, go.Figure, "The return type should be a Plotly Figure.")

        # 2. Check if the figure contains one trace (the pie chart)
        self.assertEqual(len(fig.data), 1, "The figure should contain exactly one trace.")
        
        pie_chart = fig.data[0]

        # 3. Verify the data passed to the pie chart
        self.assertEqual(list(pie_chart.labels), ['Scope 1', 'Scope 2', 'Scope 3'])
        self.assertEqual(list(pie_chart.values), [10, 20, 70])
        
        # 4. Verify the custom marker colors
        expected_colors = ['#33cc33', '#ffcc00', '#3366ff']
        self.assertEqual(list(pie_chart.marker.colors), expected_colors)

    def test_empty_dictionary(self):
        """
        Tests the `create_plotly_figure_piechart` function
        with an empty typical dictionary.
        """
        data = {}
        fig = create_plotly_figure_piechart(data)
        
        pie_chart = fig.data[0]
        
        # The function should handle this by creating a default slice
        self.assertEqual(list(pie_chart.labels), ['no_data'])
        self.assertEqual(list(pie_chart.values), [0])

    def test_all_zero_values(self):
        """
        Tests the `create_plotly_figure_piechart` function
        when all dictionary values are zero.
        """
        data = {'Scope 1': 0, 'Scope 2': 0}
        fig = create_plotly_figure_piechart(data)
        
        pie_chart = fig.data[0]
        
        # The function should handle this by creating a default slice
        self.assertEqual(list(pie_chart.labels), ['no_data'])
        self.assertEqual(list(pie_chart.values), [0])