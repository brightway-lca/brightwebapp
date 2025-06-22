# Panel
import panel as pn
pn.extension(notifications=True)
pn.extension(design='material')
pn.extension('plotly')
pn.extension('tabulator')

# BrightWebApp
from brightwebapp.brightway import (
    load_and_set_useeio_project,
    brightway_wasm_database_storage_workaround
)
from brightwebapp.traversal import perform_graph_traversal
import bw2data as bd


# Plotting
import plotly

# Data Science
import pandas as pd


brightway_wasm_database_storage_workaround()


def create_plotly_figure_piechart(data_dict: dict) -> plotly.graph_objects.Figure:
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


class panel_lca_class:
    """
    This class is used to store all the necessary information for the LCA calculation.
    It provides methods to populate the database and perform Brightway LCA calculations.
    All methods can be bound to a button click event.

    Notes
    -----
    Why this class?
    Because for some reason data (dataframes, etc.) 
    can only be stored in a class.
    Therefore, functions bound to buttons etc., 
    can only be methods of the class.

    See Also
    --------
    https://discourse.holoviz.org/t/update-global-variable-through-function-bound-with-on-click/
    """
    brightway_wasm_database_storage_workaround()
    def __init__(self):
        self.db_name = 'USEEIO-1.1'
        self.db = None
        self.list_db_products = []
        self.dict_db_methods = {}
        self.list_db_methods = []
        self.chosen_activity = ''
        self.chosen_method = ''
        self.chosen_method_unit = ''
        self.chosen_amount = 0
        self.lca = None
        self.scope_dict = {'Scope 1': 0, 'Scope 2': 0, 'Scope 3': 0}
        self.graph_traversal_cutoff = 0.123
        self.graph_traversal = {}
        self.df_graph_traversal_nodes = None
        self.df_graph_traversal_edges = None
        self.df_tabulator_from_traversal = None
        self.df_tabulator_from_user = None
        self.df_tabulator = None # nota bene: gets updated automatically when cells in the tabulator are edited # https://panel.holoviz.org/reference/widgets/Tabulator.html#editors-editing
        self.bool_user_provided_data = False


    def set_db(self, event):
        """
        Checks if the USEEIO-1.1 Brightway project is installed.
        If not, installs it and sets is as current project.
        Else just sets the current project to USEEIO-1.1.
        """
        load_and_set_useeio_project()


    def set_list_db_products(self, event):
        """
        Sets `list_db_products` to a list of product names from the database for use in the autocomplete widget.
        """
        self.list_db_products = [node['name'] for node in self.db if 'product' in node['type']]
    

    def set_methods_objects(self, event):
        """
        dict_methods = {
            'HRSP': ('Impact Potential', 'HRSP'),
            'OZON': ('Impact Potential', 'OZON'),
            ...
        }
        """
        dict_methods = {i[-1]:[i] for i in bd.methods}
        # hardcoded for better Pyodide performance
        dict_methods_names = {
            "HRSP": "Human Health - Respiratory Effects",
            "OZON": "Ozone Depletion",
            "HNC": "Human Health Noncancer",
            "WATR": "Water",
            "METL": "Metals",
            "EUTR": "Eutrophication",
            "HTOX": "Human Health Cancer and Noncancer",
            "LAND": "Land",
            "NREN": "Nonrenewable Energy",
            "ETOX": "Freshwater Aquatic Ecotoxicity",
            "PEST": "Pesticides",
            "REN": "Renewable Energy",
            "MINE": "Minerals and Metals",
            "GCC": "Global Climate Change",
            "ACID": "Acid Rain",
            "HAPS": "Hazardous Air Pollutants",
            "HC": "Human Health Cancer",
            "SMOG": "Smog Formation",
            "ENRG": "Energy"
        }
        # hardcoded for better Pyodide performance
        dict_methods_units = {
            "HRSP": "[kg PM2.5 eq]",
            "OZON": "[kg O3 eq]",
            "HNC": "[CTUh]",
            "WATR": "[m3]",
            "METL": "[kg]",
            "EUTR": "[kg N eq]",
            "HTOX": "[CTUh]",
            "LAND": "[m2*yr]",
            "NREN": "[MJ]",
            "ETOX": "[CTUe]",
            "PEST": "[kg]",
            "REN": "[MJ]",
            "MINE": "[kg]",
            "GCC": "[kg CO2 eq]",
            "ACID": "[kg SO2 eq]",
            "HAPS": "[kg]",
            "HC": "[CTUh]",
            "SMOG": "[kg O3 eq]",
            "ENRG": "[MJ]"
        }
        """
        dict_methods_enriched = {
            'HRSP': [('Impact Potential', 'HRSP'), 'Human Health - Respiratory effects', '[kg PM2.5 eq]'],
            'OZON': [('Impact Potential', 'OZON'), 'Ozone Depletion', '[kg O3 eq]'],
            ...
        }
        """
        dict_methods_enriched = {
            key: [dict_methods[key][0], dict_methods_names[key], dict_methods_units[key]]
            for key in dict_methods
        }

        """
        list_methods_for_autocomplete = [
            ('HRSP', 'Human Health: Respiratory effects', '[kg PM2.5 eq]'),
            ('OZON', 'Ozone Depletion', '[kg O3 eq]'),
            ...
        ]
        """
        list_methods_for_autocomplete = [(key, value[1], value[2]) for key, value in dict_methods_enriched.items()]

        self.dict_db_methods = dict_methods_enriched
        self.list_db_methods = list_methods_for_autocomplete


    def set_chosen_activity(self, event):
        """
        Sets `chosen_activity` to the `bw2data.backends.proxies.Activity` object of the chosen product from the autocomplete widget.
        """
        self.chosen_activity: Activity = bd.utils.get_node(
            database = self.db_name,
            name = widget_autocomplete_product.value,
            type = 'product',
            location = 'United States'
        )


    def set_chosen_method_and_unit(self, event):
        """
        Sets `chosen_method` to the (tuple) corresponding to the chosen method string from the select widget.

        Example:
        --------
        widget_select_method.value = ('HRSP', 'Human Health: Respiratory effects', '[kg PM2.5 eq]')
        widget_select_method.value[0] = 'HRSP'
        dict_db_methods = {'HRSP': [('Impact Potential', 'HRSP'), 'Human Health - Respiratory effects', '[kg PM2.5 eq]']}
        dict_db_methods['HRSP'][0] = ('Impact Potential', 'HRSP') # which is the tuple that bd.Method needs
        """
        self.chosen_method = bd.Method(self.dict_db_methods[widget_select_method.value[0]][0])
        self.chosen_method_unit = widget_select_method.value[2]


    def set_chosen_amount(self, event):
        """
        Sets `chosen_amount` to the float value from the float input widget.
        """
        self.chosen_amount = widget_float_input_amount.value


    def set_graph_traversal_cutoff(self, event):
        """
        Sets the `graph_traversal_cutoff` attribute to the float value from the float slider widget.
        Note that the value is divided by 100 to convert from percentage to decimal.
        """
        self.graph_traversal_cutoff = widget_float_slider_cutoff.value / 100


    def trigger_graph_traversal(self, event):
        self.df_tabulator_from_traversal = perform_graph_traversal(
            demand={self.chosen_activity: self.chosen_amount},
            method=self.chosen_method.name,
            cutoff=self.graph_traversal_cutoff,
            biosphere_cutoff=0.01,
            max_calc=100,
            return_format='dataframe',
        )
        

    def determine_scope_2(self, event):
        """
        sets "Scope" to 2 for all rows where the "Name" column equals "Electricity; at consumer"
        """
        self.df_tabulator_from_traversal.loc[self.df_tabulator_from_traversal['Name'] == 'Electricity; at consumer', 'Scope'] = 2


    def set_table_filename(self, event):
        """
        Generates a string to be used a filename for downloading the tabulator.value DataFrame.

        Returns
        -------
        str
            Filename string.
        """
        str_filename: str = (
            "activity='"
            + self.chosen_activity['name'].replace(' ', '_').replace(';', '') .replace(',', '')
            + "'_method='"
            + '-'.join(self.chosen_method.name).replace(' ', '-')
            + "'_cutoff=" 
            + str(self.graph_traversal_cutoff).replace('.', ',') 
            + ".csv"
        )
        filename_download.value = str_filename


    def determine_scope_emissions(self, event):
        """
        Determines the scope 1/2/3 emissions from the graph traversal nodes dataframe.
        """
        dict_scope = {
            'Scope 1': 0,
            'Scope 2': 0,
            'Scope 3': 0
        }
        
        dict_scope['Scope 1'] = self.widget_tabulator.value.loc[(df['Scope'] == 1)]['Burden(Direct)'].values.sum()
        dict_scope['Scope 2'] = self.widget_tabulator.value.loc[(df['Scope'] == 2)]['Burden(Direct)'].values.sum()
        dict_scope['Scope 3'] = self.widget_tabulator.value['Burden(Direct)'].sum() - dict_scope['Scope 1'] - dict_scope['Scope 2']

        panel_lca_class_instance.scope_dict = dict_scope

panel_lca_class_instance = panel_lca_class()


# COLUMN 1 ####################################################################


def button_action_load_database(event):
    panel_lca_class_instance.set_db(event)
    panel_lca_class_instance.set_list_db_products(event)
    panel_lca_class_instance.set_methods_objects(event)
    widget_autocomplete_product.options = panel_lca_class_instance.list_db_products
    widget_select_method.options = panel_lca_class_instance.list_db_methods
    widget_select_method.value = [item for item in panel_lca_class_instance.list_db_methods if 'GCC' in item[0]][0] # global warming as default value


def button_action_perform_lca(event):
    if widget_autocomplete_product.value == '':
        pn.state.notifications.error('Please select a reference product first!', duration=5000)
        return
    else:
        widget_plotly_figure_piechart.object = create_plotly_figure_piechart({'null':0})
        pn.state.notifications.info('Calculating LCA score...', duration=5000)
        pass
    panel_lca_class_instance.set_chosen_activity(event)
    panel_lca_class_instance.set_chosen_method_and_unit(event)
    panel_lca_class_instance.set_chosen_amount(event)
    panel_lca_class_instance.set_graph_traversal_cutoff(event)
    panel_lca_class_instance.trigger_graph_traversal(event)
    panel_lca_class_instance.determine_scope_2(event)
    widget_number_lca_score.format = f'{{value:,.3f}} {panel_lca_class_instance.chosen_method_unit}'
    widget_tabulator.value = panel_lca_class_instance.df_tabulator_from_traversal
    pn.state.notifications.success('Completed LCA score calculation!', duration=5000)
    perform_scope_analysis(event)


def perform_scope_analysis(event):
    pn.state.notifications.info('Performing Scope Analysis...', duration=5000)
    panel_lca_class_instance.determine_scope_emissions(event)
    widget_plotly_figure_piechart.object = create_plotly_figure_piechart(panel_lca_class_instance.scope_dict)
    panel_lca_class_instance.set_table_filename(event)
    widget_number_lca_score.value = panel_lca_class_instance.df_tabulator['Burden(Direct)'].sum()
    pn.state.notifications.success('Scope Analysis Complete!', duration=5000)


widget_button_load_db = pn.widgets.Button( 
    name='Load USEEIO Database',
    icon='database-plus',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_load_db.on_click(button_action_load_database)



widget_autocomplete_product = pn.widgets.AutocompleteInput( 
    name='Reference Product/Product/Service',
    options=[],
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Start typing your product name here...',
    sizing_mode='stretch_width'
)

markdown_method_documentation = pn.pane.Markdown("""
The impact assessment methods are documented [in Table 3](https://www.nature.com/articles/s41597-022-01293-7/tables/4) of the [USEEIO release article](https://doi.org/10.1038/s41597-022-01293-7).
""")

widget_select_method = pn.widgets.Select( 
    name='Impact Assessment Method',
    options=[],
    sizing_mode='stretch_width',
)

widget_float_input_amount = pn.widgets.FloatInput( 
    name='(Monetary) Amount of Reference Product [USD]',
    value=100,
    step=1,
    start=0,
    sizing_mode='stretch_width'
)

widget_button_lca = pn.widgets.Button( 
    name='Compute LCA Score',
    icon='calculator',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_lca.on_click(button_action_perform_lca)

widget_float_slider_cutoff = pn.widgets.EditableFloatSlider(
    name='Graph Traversal Cut-Off [%]',
    start=1,
    end=50,
    step=1,
    value=10,
    sizing_mode='stretch_width'
)

markdown_cutoff_documentation = pn.pane.Markdown("""
[A cut-off of 10%](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph_tools/graph_traversal/new_node_each_visit/index.html) means that an upstream process is shown if it accounts for at least 10% of total impact. The lower value of 1% is chosen here for performance reasons only.
""")

widget_button_graph = pn.widgets.Button(
    name='Update Data based on User Input',
    icon='chart-donut-3',
    button_type='primary',
    sizing_mode='stretch_width'
)
# widget_button_graph.on_click(button_action_scope_analysis)

widget_number_lca_score = pn.indicators.Number(
    name='LCA Impact Score',
    font_size='30pt',
    title_size='20pt',
    value=0,
    format='{value:,.3f}',
    margin=0
)

widget_plotly_figure_piechart = pn.pane.Plotly(
    create_plotly_figure_piechart(
        {'Scope 1': 0}
    )
)

col1 = pn.Column(
    '# LCA Settings',
    widget_button_load_db,
    widget_autocomplete_product,
    markdown_method_documentation,
    widget_select_method,
    widget_float_input_amount,
    markdown_cutoff_documentation,
    widget_float_slider_cutoff,
    widget_button_lca,
    widget_button_graph,
    pn.Spacer(height=10),
    widget_number_lca_score,
    widget_plotly_figure_piechart,
)

# COLUMN 2 ####################################################################


def highlight_tabulator_cells(tabulator_row):
    """
    Applies a background color to all rows where the 'Edited?' column is True.

    See Also
    --------
    - https://stackoverflow.com/a/48306463
    - https://discourse.holoviz.org/t/dynamic-update-of-tabulator-style
    """
    if tabulator_row['Edited?'] == True:
        return ['background-color: orange'] * len(tabulator_row)
    else:
        return [''] * len(tabulator_row)
    

widget_tabulator = pn.widgets.Tabulator(
    pd.DataFrame([['']], columns=['Data will appear here after calculations...']),
    theme='site',
    show_index=False,
    hidden_columns=['activity_datapackage_id', 'producer_unique_id'],
    layout='fit_data_stretch',
    sizing_mode='stretch_width'
)
widget_tabulator.style.apply(highlight_tabulator_cells, axis=1)

filename_download, button_download = widget_tabulator.download_menu(
    text_kwargs={'name': 'Filename', 'value': 'filename.csv'},
    button_kwargs={'name': 'Download Table'}
)
filename_download.sizing_mode = 'stretch_width'
button_download.align = 'center'
button_download.icon = 'download'

widget_cutoff_indicator_statictext = pn.widgets.StaticText(
    name='Includes processes responsible for amount of emissions [%]',
    value=None
)

col2 = pn.Column(
    pn.Row('# Table of Upstream Processes', filename_download, button_download),
    widget_tabulator
)

# SITE ######################################################################

code_open_window = """
window.open("https://brightwebapp.readthedocs.io/")
"""
button_about = pn.widgets.Button(name="Learn more about this web application...", button_type="success")
button_about.js_on_click(code=code_open_window)

header = pn.Row(
    button_about,
    pn.HSpacer(),
    pn.pane.SVG(
        'https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/logo_PSI-ETHZ-WISER_white.svg',
        #height=50,
        margin=0,
        align="center"
    ),
    sizing_mode="stretch_width",
)

template = pn.template.MaterialTemplate(
    header=header,
    title='BrightWebApp (Carbon Accounting)',
    header_background='#2d853a', # green
    logo='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/docs/_logos/brightwebapp_logo.svg',
    favicon='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/docs/_logos/brightwebapp_logo.svg',
)

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1 # 1/3rd of the width
gspec[:,1:3] = col2 # 2/3rds of the width

template.main.append(gspec)
template.servable()