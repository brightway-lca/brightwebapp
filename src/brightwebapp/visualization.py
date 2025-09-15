import plotly.graph_objects


def create_plotly_figure_piechart(data_dict: dict) -> plotly.graph_objects.Figure:
    """
    Creates a `plotly.graph_objects.Figure` pie chart using [Plotly](https://plotly.com/python/) 
    based on a provided data dictionary of emission scopes and values.

    If the dictionary is empty, or all values are zero, an empty pie chart is returned.

    Parameters
    ----------
    data_dict : dict
        Dictionary with labels as keys and corresponding values.  
        Example:  
        ```
        {'Scope 1': 12.34, 'Scope 2': 56.78, 'Scope 3': 90.12}
        ```

    See Also
    --------
    [`plotly.graph_objects.Pie`](https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Pie.html)

    Example
    -------
    ```python
    create_plotly_figure_piechart({'Scope 1': 12.34, 'Scope 2': 56.78, 'Scope 3': 90.12})
    ```
    ```python exec="true" html="true"
    from brightwebapp.visualization import create_plotly_figure_piechart
    fig = create_plotly_figure_piechart({'Scope 1': 12.34, 'Scope 2': 56.78, 'Scope 3': 90.12})
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    # https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
    ```

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly Figure object representing the pie chart.
    """
    if not data_dict or all(value == 0 for value in data_dict.values()):
        data_dict = {'no_data': 0}

    marker_colors = []
    for label in data_dict.keys():
        if label == 'Scope 1':
            marker_colors.append('#33cc33')  # Color for Scope 1
        elif label == 'Scope 2':
            marker_colors.append('#ffcc00')  # Color for Scope 2
        elif label == 'Scope 3':
            marker_colors.append('#3366ff')  # Color for Scope 3
        else:
            marker_colors.append('#000000')  # Default color for other labels

    plotly_figure = plotly.graph_objects.Figure(
        data=[
            plotly.graph_objects.Pie(
                labels=list(data_dict.keys()),
                values=list(data_dict.values()),
                marker=dict(colors=marker_colors)  # Set the colors for the pie chart
            )
        ]
    )
    plotly_figure.update_traces(
        marker=dict(
            line=dict(color='#000000', width=2)
        )
    )
    plotly_figure.update_layout(
        autosize=True,
        height=300,
        legend=dict(
            orientation="v",
            yanchor="auto",
            y=1,
            xanchor="right",
            x=-0.3
        ),
        margin=dict(
            l=50,
            r=50,
            b=0,
            t=0,
            pad=0
        ),
    )
    return plotly_figure