# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

from pathlib import Path

CSV_FILE = Path.cwd() / 'Outputs' / 'Cerus.csv'


def generate_dash(df):

    # Initialize the app - incorporate css
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = Dash(__name__, external_stylesheets=external_stylesheets)

    # App layout
    app.layout = html.Div([
        html.Div(className='row',
                 children='PLAYING WITH PLOTLY',
                 style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),

        html.Hr(),

        html.Div(className='row', children=[
            html.Div(className='six columns', children=[
                'Chose a value to display:',
                dcc.Dropdown(options=df.columns, value='final percent', id='dropdown-selection2'),
                dcc.Graph(figure={}, id='graph2')
            ]),
            html.Div(className='six columns', children=[
                'Chose a date to see the progress:',
                dcc.Dropdown(options=df.date.unique(), value='2024.03.05', id='dropdown-selection'),
                dcc.Graph(figure={}, id='graph1')
            ]),
        ]),

        html.Div(className='row', children=[
            dash_table.DataTable(
                data=[],
                page_size=30,
                id='table')
        ])
    ])

    # Controls for First Graph
    @callback(
        Output(component_id='graph1', component_property='figure'),
        Input(component_id='dropdown-selection', component_property='value'),
        Input(component_id='dropdown-selection2', component_property='value')
    )
    def update_graph1(date, value):
        dg = df[df['date'] == date]
        fig = px.bar(data_frame=dg, x='time', y=value)
        if value == 'final percent':
            fig.update_layout(yaxis_range=[0, 100])
        return fig

    # Controls for Second Graph
    @callback(
        Output(component_id='graph2', component_property='figure'),
        Input(component_id='dropdown-selection2', component_property='value')
    )
    def update_graph2(value):
        fig = px.histogram(data_frame=df, x='date', y=value, histfunc='avg')
        return fig

    # Controls for Data Table
    @callback(
        Output(component_id='table', component_property='data'),
        Input(component_id='dropdown-selection', component_property='value')
    )
    def update_data_table(col_chosen):
        dg = df[df['date'] == col_chosen]
        data = dg.to_dict('records')
        return data

    app.run(debug=True)


# Run the app
if __name__ == '__main__':
    # Incorporate data
    dataframe = pd.read_csv(CSV_FILE)
    generate_dash(dataframe)
