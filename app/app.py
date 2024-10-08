from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
import plotly.express as px
import pandas as pd
import sqlite3
from dotenv import load_dotenv
load_dotenv() 
import openai
from openai import OpenAI 
from typing import Tuple

import ell
from agents import answer_question
from utils import run_query, df_to_table


BEG_YEAR = 2013
END_YEAR = 2022



def get_graph_sched():
    query = f'select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE, year from patient group by year, DEA_DRUG_SCHEDULE order by year'
    df = run_query(query)
    fig = px.bar(df, x='DEA_DRUG_SCHEDULE', y='prescriptions', animation_frame='Year',
                   labels={'DEA_DRUG_SCHEDULE':'Drug Schedule', 'prescriptions':'Num. Prescriptions'},
                   )
    fig.update_layout(xaxis = dict(tickmode = 'array', tickvals = [1, 2, 3, 4, 5],
        ticktext = ['Schedule ' + str(i) for i in range(1, 6)]))
    return fig

app = Dash()

app.layout = [
    html.H1(children=f'Michigan controlled substance utilization {BEG_YEAR}-{END_YEAR}', style={'textAlign':'center'}),
    html.Div([
        html.P('Visualizations of data from https://www.michigan.gov/lara/bureau-list/bpl/health/maps/reports'),
    ]),
    html.H2(children='Total CS prescriptions dispensed by year'),
    html.P("Select drug type:"),
    dcc.Dropdown(['ALL'] + run_query('select distinct(drug_name_strength) as dns from patient')['dns'].to_list(), 'ALL', id='dropdown-total'),
    dcc.Graph(id='graph-total'),
    html.H2(children='Prescriptions dispensed by drug schedule'),
    # html.P("Select year:"),
    # dcc.Dropdown([i for i in range(BEG_YEAR, END_YEAR+1)], END_YEAR, id='dropdown-sched'),
    dcc.Loading(dcc.Graph(figure=get_graph_sched()), type='cube'),
    html.H2(children='Prescriptions dispensed by drug schedule with age breakdown'),
    html.P("Select year: (age breakout available from 2018)"),
    dcc.Dropdown([i for i in range(2018, END_YEAR+1)], END_YEAR, id='dropdown-sched-age'),
    dcc.Graph(id='graph-sched-age'),
    html.H2(children='Prescriptions dispensed by classification'),
    html.P("Select year: "),
    dcc.Dropdown([i for i in range(BEG_YEAR, END_YEAR+1)], END_YEAR, id='dropdown-type'),
    dcc.Graph(id='graph-type'),
    html.H2(children='Example rows from the database'),
    html.P("The database contains two tables, the patient table and the patient_with_age table. The patient table contains the following:"),
    html.Div([dash_table.DataTable(*df_to_table(run_query('select * from patient limit 100')), page_size=10, style_table={'overflowX': 'scroll'}),
    ]),
    html.P("The patient_with_age table contains the following:"),
    dash_table.DataTable(*df_to_table(run_query('select * from patient_with_age limit 100')), page_size=10, style_table={'overflowX': 'scroll'}),
    html.H2(children='AI Analyst'),
    html.P("Have more questions about the data? Ask our AI analyst! (Requires OpenAI API key in your .env file)"),
    html.Div([
        dcc.Input(id='openai-question', type='text', placeholder='Ask a question', size='200'),
    ]),
    html.Button('Submit', id='openai-button'),
    html.Div(id='openai-output'),
    dcc.Loading(id='openai-graph'),
    dcc.Loading(id='openai-table'),
]

@callback(
    Output('graph-total', 'figure'),
    Input('dropdown-total', 'value')
)
def update_graph_total(value):
    if value == 'ALL':
        query = 'select sum(prescription_count) as prescriptions, year from patient group by year order by year'
    else:
        query = f'select sum(prescription_count) as prescriptions, year from patient where drug_name_strength="{value}" group by year order by year'
    df = run_query(query)
    fig = px.bar(df, x='Year', y='prescriptions',
                   labels={'Year':'Year', 'prescriptions':'Num. Prescriptions'},
                   )
    fig.update_layout(xaxis=dict(dtick=1))
    return fig


@callback(
    Output('graph-sched-age', 'figure'),
    Input('dropdown-sched-age', 'value')
)
def update_graph_sched_age(value):
    query = f'select sum(prescription_count) as prescriptions, AGE_RANGE, DEA_DRUG_SCHEDULE from patient_with_age where year={value} group by DEA_DRUG_SCHEDULE, AGE_RANGE'
    df = run_query(query)
    df['AGE_RANGE'] = df['AGE_RANGE'].astype("category")
    age_order = ['Ages 4 and younger', 'Ages 5 To 17', 'Ages 18 To 24', 'Ages 25 To 34', 
             'Ages 35 To 44', 'Ages 45 To 54', 'Ages 55 To 64', 'Ages 65 and older']
    fig = px.bar(df, x='DEA_DRUG_SCHEDULE', y='prescriptions', color='AGE_RANGE',
                   labels={'DEA_DRUG_SCHEDULE':'Drug Schedule', 'prescriptions':'Num. Prescriptions', 'AGE_RANGE':'Age Group'},
                   barmode='group',
                   category_orders={'AGE_RANGE': age_order}
                   )
    fig.update_layout(xaxis = dict(tickmode = 'array', tickvals = [1, 2, 3, 4, 5],
        ticktext = ['Schedule ' + str(i) for i in range(1, 6)]))
    return fig

@callback(
    Output('graph-type', 'figure'),
    Input('dropdown-type', 'value')
)
def update_graph_type(value):
    query = f'select sum(prescription_count) as prescriptions, AHFS_DESCRIPTION from patient where year={value} group by AHFS_DESCRIPTION'
    df = run_query(query)
    df.loc[df['prescriptions']/df['prescriptions'].sum() < .04, 'AHFS_DESCRIPTION'] = 'Other'
    fig = px.pie(df, names='AHFS_DESCRIPTION', values='prescriptions',
                   labels={'AHFS_DESCRIPTION':'Classification', 'prescriptions':'Num. Prescriptions'},
                   )
    fig.update_traces(hole=.4)
    return fig

@callback(
    Output('openai-output', 'children'),
    Output('openai-table', 'children'),
    Output('openai-graph', 'children'),
    Input('openai-button', 'n_clicks'),
    State('openai-question', 'value')
)
def ai_chat(n_clicks, question) -> Tuple[str, dash_table.DataTable, dcc.Graph]:
    # Temporary testing code
    if not valid_api_key():
        return 'Invalid API key', None, None
    if question is None:
        return 'Please enter a question', None, None

    try:
        resp, table, graph = answer_question(question)
    except openai.RateLimitError as e:
        return f'Rate limit error. {e}', None, None
    return resp, table, graph

def valid_api_key():
    try:
        client = OpenAI()
        client.models.list()
    except openai.AuthenticationError:
        return False
    return True

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
