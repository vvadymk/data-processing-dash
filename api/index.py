import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc


TICKERS = ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'AMZN']

end_date = datetime.today()
start_date = end_date - timedelta(days=180)

def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.reset_index(inplace=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip('_') for col in data.columns.values]
    return data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server 
app.title = 'Ціни акцій'

app.layout = html.Div([
    html.H1('📈 Ціни акцій', className="text-center my-4"),

    html.Div([
        html.Label("Виберіть акцію:", className="fw-bold"),
        dcc.Dropdown(
            id='stock-dropdown',
            options=[{'label': i, 'value': i} for i in TICKERS],
            value='AAPL',
            clearable=False
        ),
    ], className='mb-3'),

    html.Div([
        html.Label("Виберіть діапазон дат:", className="fw-bold"),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=datetime(2015, 1, 1),
            start_date=start_date.date(),
            end_date=end_date.date()
        ),
    ], className='mb-4'),

    html.Div([
    html.Button("⬇️ Завантажити CSV", id="btn_csv", className="btn btn-primary"),
    dcc.Download(id="download-dataframe-csv")
], className="mb-4"),

    dcc.Graph(id='price-graph'),

    html.H3("📊 Інші візуалізації", className="mt-5"),

    dcc.Graph(id='volume-bar-chart'),
    dcc.Graph(id='moving-average-line')
], className="container")

@app.callback(
    Output('price-graph', 'figure'),
    Output('volume-bar-chart', 'figure'),
    Output('moving-average-line', 'figure'),
    Input('stock-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_graphs(ticker, start_date, end_date):
    df = load_data(ticker, start_date, end_date)

    price_col = f'Close_{ticker}'
    volume_col = f'Volume_{ticker}'

    fig_price = px.line(df, x='Date', y=price_col, title=f'{ticker} Ціна акцій')
    fig_volume = px.bar(df, x='Date', y=volume_col, title=f'{ticker} Обсяг торгів')
    df['MA20'] = df[price_col].rolling(window=20).mean()
    fig_ma = px.line(df, x='Date', y='MA20', title=f'{ticker} 20-денна змінна середня')

    return fig_price, fig_volume, fig_ma

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("stock-dropdown", "value"),
    State("date-picker", "start_date"),
    State("date-picker", "end_date"),
    prevent_initial_call=True
)
def func(n_clicks, ticker, start_date, end_date):
    df = load_data(ticker, start_date, end_date)
    return dcc.send_data_frame(df.to_csv, f"{ticker}_stock_data.csv")

def handler(request):
    return server  # потрібно для запуску через Vercel