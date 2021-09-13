import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web  # requires v0.6.0 or later
from datetime import datetime
import os
import pandas_datareader.data as web
import pandas as pd

filepath = "https://raw.githubusercontent.com/pierreolivierbonin/test_dash_app/main/NASDAQcompanylist.csv"
nsdq = pd.read_csv(filepath, encoding="cp1252")
nsdq.set_index("Symbol", inplace=True)
options = []

for tic in nsdq.index:
    # {"label":"user sees", "value": "script sees"}
    mydict = {}
    mydict["label"] = nsdq.loc[tic]["Name"]
    mydict["value"] = tic
    options.append(mydict)

os.environ["ALPHAVANTAGE_API_KEY"] = "JCEMC6W4T175WZ2T"

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),
    html.Div([html.H3('Enter a stock symbol:',
                      style={"paddingRight": "30px"}),
              dcc.Dropdown(
        id='my_ticker_symbol',
        value=['TSLA'],
        options=options,
        multi=True
    )], style={"display": "inline-block", "verticalAlign": "top", "width": "30%"}),
    html.Div([html.H3("Select a start and end date:"),
              dcc.DatePickerRange(
        id="my_date_picker",
        min_date_allowed=datetime(2015, 1, 1),
        max_date_allowed=datetime.today(),
        start_date=datetime(2018, 1, 1),
        end_date=datetime.today()
    )
    ], style={"display": "inline-block"}),
    html.Div([
        html.Button(id="submit-button",
                    n_clicks=0,
                    children="Submit",
                    style={"fontSize": 24, "marginLeft": "30px"})

    ], style={"display": "inline-block"}),
    dcc.Graph(
        id='my_graph',
        figure={
            'data': [
                {'x': [1, 2], 'y': [3, 1]}
            ]
        }
    )
])


@ app.callback(
    Output('my_graph', 'figure'),
    [Input("submit-button", "n_clicks")],
    [State('my_ticker_symbol', 'value'),
     State("my_date_picker", "start_date"),
     State("my_date_picker", "end_date")
     ])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    start = datetime.strptime(start_date[:10], "%Y-%m-%d")
    end = datetime.strptime(end_date[:10], "%Y-%m-%d")
    traces = []
    for tic in stock_ticker:
        df = web.DataReader(tic, "av-daily",
                            start=start_date,
                            end=end_date,
                            api_key=os.getenv('ALPHAVANTAGE_API_KEY'))
        traces.append({'x': df.index, 'y': df["close"],
                       "name": tic})

    fig = {
        'data': traces,
        'layout': {'title': stock_ticker}
    }
    return fig


if __name__ == '__main__':
    app.run_server()
