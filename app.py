import dash
import MySQLdb
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly

print(dcc.__version__)  # 0.6.0 or above is required

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
])


index_page = html.Div([
    # dcc.Link('Go to bar graph', href='/page-bar'),
    # html.Br(),
    # dcc.Link('Go to Page 2', href='/page-2'),
    html.Div([
        # Pie chart
        html.Div([
            html.H3('Emerging Tech vs Traditional',
                    style={'color': 'orange'}),
            dcc.Graph(
                id='pie-graph',
            ),
        ], className="six columns"),
        # Funnel chart
        html.Div([
            html.H3('Sales Funnel', style={'color': 'orange'}),
            dcc.Graph(
                id='funnel-graph',
            )
        ], className="six columns"),
        # Bar graph
        html.Div([
            html.H3('Client rank', style={'color': 'orange'}),
            dcc.Graph(
                id='Bar-graph',
            )
        ], className="twelve columns"),

        html.Div([
            html.H3('Sales Stats', style={'color': 'orange'}),
            dcc.Graph(
                id='user-Bar-graph',
            ),
        ], className="twelve columns")
    ], className="row")

])

page_2_layout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])

page_1_layout = html.Div([
    html.Button('Update Graphs', id='button', n_clicks=0),

    html.H3('Emerging Tech vs Traditional', style={'color': 'orange'}),
    dcc.Graph(
        id='pie-graph',
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
], className="six columns")

page_funnel_layout = html.Div([
    html.Button('Update Graphs', id='button', n_clicks=0),
    html.H3('Sales Funnel', style={'color': 'orange'}),
    dcc.Graph(
        id='funnel-graph',
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
], className="six columns")

page_client_layout = html.Div([
    html.Button('Update Graphs', id='button', n_clicks=0),
    html.H3('Client rank', style={'color': 'orange'}),
    dcc.Graph(
        id='Bar-graph',
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
], className="six columns")

page_sales_layout = html.Div([
    html.Button('Update Graphs', id='button', n_clicks=0),
    html.H3('Sales Stats', style={'color': 'orange'}),
    dcc.Graph(
        id='user-Bar-graph',
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,
        n_intervals=0
    ),
], className="six columns")


@app.callback(Output('user-Bar-graph', 'figure'),
              inputs=[Input('interval-component', 'n_intervals')])
def update_graph_bar(n_intervals):
    conn = MySQLdb.connect(host="localhost", user="root", db="qpipe")
    cursor = conn.cursor()
    cursor.execute('''SELECT u.id AS user_id, u.firstname AS firstname, COUNT(*)/2 as total_count,
                    sum(case when p.sales_cycle_id BETWEEN 0 AND 4 then 1 else 0 end) as opportunity_count,
                    sum(case when p.sales_cycle_id BETWEEN 5 AND 8 then 1 else 0 end) as project_count
                    FROM projects AS p
                    INNER JOIN users AS u
                    ON u.id = p.rep_id
                    GROUP BY p.rep_id
                    ORDER BY total_count DESC''')
    rows = cursor.fetchall()
    cursor.close()

    df3 = pd.DataFrame([[ij for ij in i] for i in rows])
    df3.rename(columns={1: 'Name', 3: 'Opportunity',
                        4: 'Project'}, inplace=True)
    if df3.empty == True:
        df3['Name'] = "Unknown"
        df3['Opportunity'] = 0
        df3['Project'] = 0
    else:
        df3['Name'] = df3['Name']
        df3['Opportunity'] = df3['Opportunity']
        df3['Project'] = df3['Project']

    trace1 = []
    trace1.append(go.Bar(
        y=df3['Name'],
        x=df3['Opportunity'],
        name='Opportunitiy',
        orientation='h'
    ))
    trace1.append(go.Bar(
        y=df3['Name'],
        x=df3['Project'],
        name='Project',
        orientation='h'
    ))
    layout = plotly.graph_objs.Layout(
        barmode='group'
    )
    return {'data': trace1, 'layout': layout}

    # Solution Pie Chart
@app.callback(Output('pie-graph', 'figure'),
              inputs=[Input('interval-component', 'n_intervals')])
def update_graph_pie(n_intervals):
    conn = MySQLdb.connect(host="localhost", user="root", db="qpipe")
    cursor = conn.cursor()
    cursor.execute('''SELECT count(*), sol_class.name from solutions as s 
INNER JOIN sol_classifications as sol_class 
ON s.sol_classification_id = sol_class.id 
GROUP BY sol_classification_id''')
    rows = cursor.fetchall()
    cursor.close()

    df3 = pd.DataFrame([[ij for ij in i] for i in rows])
    df3.rename(columns={0: 'Total', 1: 'Name'}, inplace=True)

    pie = []
    pie.append(go.Pie(
        labels=df3['Name'],
        values=df3['Total'],
    ))

    return {'data': pie, }

@app.callback(Output('funnel-graph', 'figure'),
              inputs=[Input('interval-component', 'n_intervals')])
def update_graph_funnel(n_intervals):
    conn = MySQLdb.connect(host="localhost", user="root", db="qpipe")
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(p.sales_cycle_id) as Total,
sc.name FROM projects as p 
RIGHT JOIN sale_cycles as sc 
ON p.sales_cycle_id = sc.id 
GROUP BY sc.id ORDER BY Total DESC''')
    rows = cursor.fetchall()
    cursor.close()

    df3 = pd.DataFrame([[ij for ij in i] for i in rows])
    df3.rename(columns={0: 'Total', 1: 'Name'}, inplace=True)

    funnel = []
    funnel.append(go.Funnel(
        y=df3['Name'],
        x=df3['Total'],
    ))

    return {'data': funnel, }

@app.callback(Output('Bar-graph', 'figure'),
              inputs=[Input('interval-component', 'n_intervals')])
def update_graph_bar_client(n_intervals):
    conn = MySQLdb.connect(host="localhost", user="root", db="qpipe")
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*), c.name FROM projects as p 
INNER JOIN customers as c ON p.customer_id = c.id 
WHERE MONTH(p.created_at) = MONTH(CURRENT_DATE()) AND 
Year(p.created_at) = YEAR(CURRENT_DATE()) GROUP BY c.name ORDER BY COUNT(*) DESC''')
    rows = cursor.fetchall()
    cursor.close()

    df3 = pd.DataFrame([[ij for ij in i] for i in rows])
    df3.rename(columns={0: 'Total', 1: 'Name'}, inplace=True)

    client = []
    client.append(go.Bar(
        x=df3['Name'],
        y=df3['Total'],
    ))

    return {'data': client, }


@app.callback(dash.dependencies.Output('page-1-content', 'children'),
              [dash.dependencies.Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)


@app.callback(dash.dependencies.Output('page-2-content', 'children'),
              [dash.dependencies.Input('page-2-radios', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-bar':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/sales-funnel':
        return page_funnel_layout
    elif pathname == '/client-ranks':
        return page_client_layout
    elif pathname == '/sales':
        return page_sales_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True)
