import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px
import pandas as pd
import requests

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# For Heroku deployment
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# Accessing IMF database
url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/'

commodities = {
    'Crude, Brent':'POILBRE',
    'Crude, WTI':'POILWTI',
    'Crude, Dubai':'POILDUB',
    'Natural gas, EU':'PNGASEU',
    'Natural gas, US':'PNGASUS',
    'Natural gas, Asia':'PNGASJP'}

data = []
for name, value in commodities.items():
    data.append((requests.get(f'{url}CompactData/PCPS/M.W00.{value}.USD').json()['CompactData']['DataSet']['Series']))

data_list = [[obs.get('@TIME_PERIOD'), obs.get('@OBS_VALUE')]
             for obs in data[5]['Obs']]

df = pd.DataFrame(data_list, columns=['Date', 'Price'])
df['Date'] = pd.to_datetime(df['Date']) + pd.DateOffset(days=14)
df = df.set_index('Date')
df['Price'] = df['Price'].astype('float').round(2)
df = df[df.index >= '2000-01-01']

# df_orig = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })
#
# fig_orig = px.bar(df_orig, x="Fruit", y="Amount", color="City", barmode="group")

fig = px.line(df, x=df.index, y='Price', title='Natural Gas, Asia')
fig.update_layout(xaxis_title='Year',
                  xaxis_fixedrange=True,
                  yaxis_title='Price (USD/MMBtu)',
                  yaxis_fixedrange=True,
                 template="seaborn")

app.layout = html.Div(children=[
    html.H1(children='Energy Dashboard'),
    html.Div(children='''
        Source: IMF Primary Commodity Prices, Monthly data
    '''),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
