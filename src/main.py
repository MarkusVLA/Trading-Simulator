import dash
from dash import html, dcc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import pandas as pd
from data_feeder import DataFeeder
from trader import Trader
import yfinance as yf

symbol = "AAPL"
data_feeder = DataFeeder(symbol, "2024-03-25", "2024-03-26", "1m")
manager = Trader(initial_capital=1000.0)
manager.addStock(symbol)


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1(f'Stock and Capital Over Time: {symbol}', style={'textAlign': 'center', 'color': 'midnightblue'}),
    dcc.Graph(id='live-update-graph'),
    html.Div(id='live-info', style={
        'textAlign': 'center',
        'marginTop': '20px',
        'color': 'darkslategray',
        'fontSize': 20,
        'fontFamily': 'Arial'
    }),  
    dcc.Interval(
        id='interval-component',
        interval=100, 
        n_intervals=0
    )
], style={'padding': '20px', 'fontFamily': 'Arial'})


@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):
    df = traderCycle()
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.1, subplot_titles=('Stock Prices and Volume', 'Capital'),
                    specs=[[{"secondary_y": True}], [{}]],  
                    row_width=[0.7, 0.3])

    # Stock Prices: Open and Close
    fig.add_trace(go.Scatter(x=pd.to_datetime(df['Datetime']), y=df['Open'], mode='lines', name='Open',
                             line=dict(width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=pd.to_datetime(df['Datetime']), y=df['Close'], mode='lines', name='Close',
                             line=dict(width=2)), row=1, col=1)
    

    # Add Volume data on the same graph as a bar chart using the secondary y-axis
    fig.add_trace(go.Bar(x=pd.to_datetime(df['Datetime']), y=df['Volume'], name='Volume',
                     marker=dict(color='rgba(50, 171, 96, 0.6)'), opacity=0.6),
              row=1, col=1, secondary_y=True)
    

    # Buy and Sell Signals
    buy_signals = df[df['Signal'] == 1]
    if not buy_signals.empty:
        fig.add_trace(go.Scatter(x=pd.to_datetime(buy_signals['Datetime']), y=buy_signals['Close'],
                                 mode='markers', name='Buy',
                                 marker=dict(color='Green', size=10, symbol='triangle-up')), row=1, col=1)
    sell_signals = df[df['Signal'] == 2]
    if not sell_signals.empty:
        fig.add_trace(go.Scatter(x=pd.to_datetime(sell_signals['Datetime']), y=sell_signals['Close'],
                                 mode='markers', name='Sell',
                                 marker=dict(color='Red', size=10, symbol='triangle-down')), row=1, col=1)

    # Capital
    if 'Capital' in df.columns:
        fig.add_trace(go.Scatter(x=pd.to_datetime(df['Datetime']), y=df['Capital'], mode='lines', name='Capital',
                                 line=dict(width=2, color='orange')), row=2, col=1)
        
    
    fig.update_layout(
        title=f'Stock and Capital Over Time: {symbol}', 
        template='plotly_white',
        height=800
    )
    
    # Update layout and axis titles as needed
    fig.update_layout(title=f'Stock Prices, Volume Over Time: {symbol}', template='plotly_white', height=800)
    fig.update_xaxes(title_text="Time", row=2, col=1) 
    fig.update_yaxes(title_text="Price", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Volume", row=1, col=1, secondary_y=True)

    return fig






@app.callback(Output('live-info', 'children'), [Input('interval-component', 'n_intervals')])
def update_info(n):
    total_value = manager.calculateTotalValue()  
    return html.Div([
        html.P(f"Last Update:"),
        html.P(f"Total Value: ${total_value:,.2f}"),
    ])


def traderCycle():
    row = data_feeder.getNextRow()
    if row is not None:
        manager.distributeData(
            stock=symbol,
            datetime=row.name,
            open_price=row['Open'],
            high_price=row['High'],
            low_price=row['Low'],
            close_price=row['Close'],
            adj_close_price=row['Adj Close'],
            volume=row['Volume']
        )

    dataF = manager.getLiveDataFrame().getFrame()
    manager.saveActions()
    return dataF

if __name__ == '__main__':
    app.run_server(debug=True)
