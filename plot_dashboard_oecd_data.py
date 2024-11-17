import os
import dash
from dash import dcc, html, Input, Output, State, MATCH, ALL
import pandas as pd
import plotly.express as px
import statsmodels

# Folder where the data files are stored
data_folder = r'[PATH]/01 - Datasets'

# Initialize the Dash app with suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Function to load a CSV file and parse it into a DataFrame
def load_and_parse_data(file_path):
    df = pd.read_csv(file_path)
    print(f"Loaded dataset from {file_path} with columns: {df.columns}")

    def parse_observation_values(row):
        import ast
        try:
            observations = ast.literal_eval(row['Observation Value'])
            obs_df = pd.DataFrame(list(observations.items()), columns=['Year', 'Value'])
            for col in row.index:
                if col != 'Observation Value':
                    obs_df[col] = row[col]
            return obs_df
        except (ValueError, SyntaxError):
            return pd.DataFrame()

    parsed_df = pd.concat(df.apply(parse_observation_values, axis=1).tolist(), ignore_index=True)
    parsed_df['Year'] = parsed_df['Year'].astype(int)
    parsed_df['Value'] = pd.to_numeric(parsed_df['Value'], errors='coerce')
    print(f"Parsed data shape: {parsed_df.shape}, with columns: {parsed_df.columns}")

    return parsed_df

# Define the layout of the app
app.layout = html.Div([
    html.H1("OECD Data Dashboard", 
            style={
                'textAlign': 'center',
                    'font-family': 'Bebas Neue'
            }
    ),

    # Dropdown to select the dataset file
    html.Label("Select Dataset:",
                style={
                    'font-family': 'Quicksand',  # Set the font to Quicksand
                    'font-size': '16px'  # Adjust font size as needed
                }
    ),
    
    dcc.Dropdown(
        id='dataset-dropdown',
        options=[{'label': os.path.splitext(f)[0], 'value': f} for f in os.listdir(data_folder) if f.endswith('.csv')],
        placeholder='Select a dataset',
        value=None,
        clearable=False,
        style={
            'font-family': 'Quicksand',  # Set the font to Quicksand
            'font-size': '16px'  # Adjust font size as needed
        }
    ),

    # Loading spinner for dynamic controls (dropdowns)
    dcc.Loading(
        id="loading-dynamic-controls",
        type="circle",  # You can choose 'dot', 'circle', or 'cube' for the spinner
        children=[
            html.Div(id='dynamic-controls')  # This is where the dynamic dropdowns will appear
        ]
    ),

    # Placeholder for dynamic controls and hidden data
    dcc.Store(id='dynamic-controls-data'),

    # Update button to manually refresh the graph
    html.Button('Update Plot', 
                id='update-button', 
                n_clicks=0, 
                style={
                    'margin-top': '20px',
                    'font-family': 'Quicksand',  # Set the font to Quicksand
                    'font-size': '16px'  # Adjust font size as needed
                }
    ),

    # Loading spinner for the graph
    dcc.Loading(
        id="loading-icon",
        type="circle",  # Choose the type of loading spinner: 'circle', 'dot', or 'cube'
        children=[
            dcc.Graph(id='graph-output')
        ]
    ),
])

# Callback to generate dynamic controls based on the selected dataset
@app.callback(
    [Output('dynamic-controls', 'children'),
     Output('dynamic-controls-data', 'data')
    ],
    Input('dataset-dropdown', 'value')
)
def generate_controls(selected_file):
    if selected_file is None:
        return [], {}

    # Load the data
    file_path = os.path.join(data_folder, selected_file)
    df = load_and_parse_data(file_path)

    # Generate dynamic dropdowns for each column except Year and Value
    controls = []
    dropdown_ids = {}

    for col in df.columns:
        if col not in ['Year', 'Value']:
            unique_values = sorted(df[col].dropna().unique())
            if len(unique_values) > 1:
                dropdown_id = f'{col}-dropdown'
                dropdown_ids[col] = dropdown_id

                controls.append(html.Label(f"Select {col.replace('_', ' ').title()}:",
                                           style={
                                                'font-family': 'Quicksand',  # Set the font to Quicksand
                                                'font-size': '16px'  # Adjust font size as needed
                                            }
                                )
                )

                controls.append(
                    dcc.Dropdown(
                        id={'type': 'dynamic-dropdown', 'index': dropdown_id},
                        options=[{'label': str(v), 'value': str(v)} for v in unique_values],
                        value=None,
                        clearable=True,
                        multi=True,
                        style={
                            'font-family': 'Quicksand',  # Set the font to Quicksand
                            'font-size': '16px'  # Adjust font size as needed
                        }
                    )
                )

    # Add a range slider for selecting the year range
    controls.append(html.Label("Select Year Range:",
                               style={
                                    'font-family': 'Quicksand',  # Set the font to Quicksand
                                    'font-size': '16px'  # Adjust font size as needed
                                }
                    )               
    )
    
    controls.append(
        dcc.RangeSlider(
            id='year-range-slider',
            min=int(df['Year'].min()),
            max=int(df['Year'].max()),
            step=1,
            marks={year: str(year) for year in range(int(df['Year'].min()), int(df['Year'].max()) + 1, 5)},
            value=[int(df['Year'].min()), int(df['Year'].max())],
        )
    )

    # Dropdown for selecting chart type
    controls.append(html.Label("Select Chart Type:",
                               style={
                                    'font-family': 'Quicksand',  # Set the font to Quicksand
                                    'font-size': '16px'  # Adjust font size as needed
                                }
                    )
    )

    controls.append(
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Scatter Plot', 'value': 'scatter'},
                {'label': 'Bar Chart', 'value': 'bar'}
            ],
            value='line',
            clearable=False,
            style={
                'font-family': 'Quicksand',  # Set the font to Quicksand
                'font-size': '16px'  # Adjust font size as needed
            }
        )
    )

    # Dropdown for selecting the column to use for color coding
    controls.append(html.Label("Select Color Dimension:",
                                style={
                                    'font-family': 'Quicksand',  # Set the font to Quicksand
                                    'font-size': '16px'  # Adjust font size as needed
                                }        
                    )
    )

    controls.append(
        dcc.Dropdown(
            id='color-dimension-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns if col not in ['Year', 'Value']],
            placeholder='Select a column for color coding',
            value=None,
            clearable=True,
            style={
                'font-family': 'Quicksand',  # Set the font to Quicksand
                'font-size': '16px'  # Adjust font size as needed
            }
        )
    )

    # Checkbox for adding regression line in scatter plot
    controls.append(html.Label("Add Linear Regression Line (Scatter Only):",
                               style={
                                    'font-family': 'Quicksand',  # Set the font to Quicksand
                                    'font-size': '16px'  # Adjust font size as needed
                                }
                    )
    )
    controls.append(
        dcc.Checklist(
            id='regression-checkbox',
            options=[{'label': 'Show Regression Line', 'value': 'show_regression'}],
            value=[],
            style={
                'font-family': 'Quicksand',  # Set the font to Quicksand
                'font-size': '16px'  # Adjust font size as needed
            }
        )
    )

    return controls, dropdown_ids

@app.callback(
    Output('graph-output', 'figure'),
    [Input('update-button', 'n_clicks'),
     State('dataset-dropdown', 'value'),
     State('year-range-slider', 'value'),
     State('chart-type-dropdown', 'value'),
     State('color-dimension-dropdown', 'value'),
     State('regression-checkbox', 'value'),
     State('dynamic-controls-data', 'data')] +
    [State({'type': 'dynamic-dropdown', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_graph(n_clicks, selected_file, year_range, chart_type, color_dimension, regression_checkbox, dropdown_ids, *selected_values):
    if not n_clicks or not selected_file:
        return dash.no_update

    # Load the data
    file_path = os.path.join(data_folder, selected_file)
    df = load_and_parse_data(file_path)
    plot_title = os.path.splitext(selected_file)[0]

    # Debugging: Check the loaded dataframe shape and columns
    print(f"Loaded DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")

    # Apply the filters based on selected dropdown values
    if dropdown_ids:
        for (col, dropdown_id), selected_value in zip(dropdown_ids.items(), selected_values[0]):
            if selected_value:
                print(f"Filtering on column: {col} with selected value(s): {selected_value}")
                df = df[df[col].astype(str).isin([str(v).strip() for v in selected_value])]
                print(f"Filtered DataFrame shape after {col} filtering: {df.shape}")
    
    UNIT_MEASURE_elements = []
    if 'UNIT_MEASURE' in df.columns and not df['UNIT_MEASURE'].empty:
        for m in df['UNIT_MEASURE']:
            if m not in UNIT_MEASURE_elements:
                UNIT_MEASURE_elements.append(m)
        if len(UNIT_MEASURE_elements) <2:
            UNIT_MEASURE_Title = UNIT_MEASURE_elements[0]
        else:
            UNIT_MEASURE_Title = UNIT_MEASURE_elements[0]
            for m in UNIT_MEASURE_Title[1:]:
                UNIT_MEASURE_Title += 'vs. ' + UNIT_MEASURE_elements[m]
        

    # Filter by the selected year range
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    print(f"DataFrame shape after year range filtering: {df.shape}")

    # Check if the dataframe is empty after filtering
    if df.empty:
        print("Warning: DataFrame is empty after applying all filters.")
        return px.scatter(title="No data available for the selected filters")

    # Define the trendline option for scatter plot
    trendline = 'ols' if 'show_regression' in regression_checkbox and chart_type == 'scatter' else None

    annotations = []
    # Title
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=1.05,
                              xanchor='center', yanchor='bottom',
                              text=f"{plot_title}",
                              font=dict(family='Bebas Neue',
                                        size=30,
                                        color='rgb(0,0,0)'),
                              showarrow=False))

    # Create the chart
    if chart_type == 'scatter':
        fig = px.scatter(
            df, x='Year', y='Value', color=color_dimension,
            trendline=trendline,
        )
    elif chart_type == 'line':
        fig = px.line(
            df, x='Year', y='Value', color=color_dimension, markers = True,
        )
    elif chart_type == 'bar':
        fig = px.bar(
            df, x='Year', y='Value', color=color_dimension,
        )
    else:
        fig = px.scatter(
            df, x='Year', y='Value', color=color_dimension,
            trendline=trendline, 
        )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=UNIT_MEASURE_Title,
        legend_title=color_dimension,
        template='plotly_white',
        annotations=annotations
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
