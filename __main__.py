import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

from ISSAPI import ISS

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

ISSData = ISS()

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

fig = go.FigureWidget(
    data = go.Scattergeo(
      lat = ISSData.df['latitude'],
      lon = ISSData.df['longitude'],
      text = [f'Altitude: {alt} on {date}' for alt, date in zip(ISSData.df['altitude'], ISSData.df['date'])],
      mode = 'markers',
      marker = dict(
        size = 8,
        opacity = 0.75,
        reversescale = True,
        autocolorscale = False,
        symbol = 'circle',
        line = dict(
          width = 1,
          color = 'rgba(102, 102, 102)'
          ),
        colorscale = 'Magma',
        cmin = ISSData.df['altitude'].min(),
        color = ISSData.df['altitude'],
        cmax = ISSData.df['altitude'].max(),
        colorbar_title = 'Altitude of ISS'
        )
      )
    )

app.layout = html.Div(
  html.Div([
    html.H4('ISS Live Feed'),
    html.Div(id = 'live-update-text'),
    dcc.Graph(id = 'live-update-graph', figure = fig),
    dcc.Interval(
      id = 'interval-component',
      interval = 1 * 1000,  # in milliseconds
      n_intervals = 0,
      )
    ]),
  )


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_live_display(dummy):

  ISSData.where()
  if dummy % 60 == 0:
    ISSData.cache()
  data = ISSData.df

  cur = data.iloc[-1]
  lat = cur['latitude']
  lon = cur['longitude']
  alt = cur['altitude']
  date = cur['date']
  style = {'padding': '5px', 'fontSize': '16px'}

  min_h, max_h = data['altitude'].min(), data['altitude'].max()

  fig.update_layout(
    title = 'ISS Positional Data',
    geo = dict(
      scope = 'world',
      projection_type = 'natural earth',
      showland = True,
      landcolor = "rgb(250, 250, 250)",
      subunitcolor = "rgb(217, 217, 217)",
      countrycolor = "rgb(217, 217, 217)",
      countrywidth = 0.5,
      subunitwidth = 0.5
      ),
    height = 1200,
    width = 1200
    )
  with fig.batch_update():
    fig.data[0].lat = data['latitude']
    fig.data[0].lon = data['longitude']
    fig.data[0].text = [
      f'Altitude: {alt} on {date}' for alt, date in zip(data['altitude'], data['date'])
      ]
    fig.data[0].marker.cmax = max_h
    fig.data[0].marker.cmin = min_h
    fig.data[0].marker.color = data['altitude']

  return [
    html.Span(f'Longitude: {str(lon)}', style = style),
    html.Span(f'Latitude: {str(lat)}', style = style),
    html.Span(f'Altitude: {str(alt)}', style = style),
    html.Span(f'Date: {str(date)}', style = style)
    ]


if __name__ == '__main__':
  app.run_server(debug = True, port = 8077, threaded = True)