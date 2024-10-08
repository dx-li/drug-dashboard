import ell
from utils import run_query, df_to_table
import json
import plotly.express as px
from dash import dcc, dash_table
from PIL import Image
from io import BytesIO
from typing import Tuple

@ell.simple(model="gpt-4o-mini", temperature=0.2)
def create_question_sql(question: str):
    """
    You are an expert data analyst and are familiar with the data in the Michigan controlled substance utilization database. The data schema {"patient" (2013-2022): PATIENT_COUNTY: Patient's county, PATIENT_STATE: Patient's state, DRUG_NAME_STRENGTH: Prescribed drug and strength, DEA_DRUG_SCHEDULE: DEA drug classification (2-5, stored as int), AHFS_DESCRIPTION: AHFS drug classification, PRESCRIPTION_COUNT: Number of prescriptions, PRESCRIPTION_QUANTITY: Total dosage units, Year: Year of data (stored as int). "patient_with_age" (2018-2022): Same as patient + AGE_RANGE: Patient's age group, PATIENT_COUNT: Unique patients, AVERAGE_DAYS_SUPPLY: Avg days of drug supply, DAYS_SUPPLY: Total drug supply days, AVERAGE_DAILY_MMEs: Avg daily dose in MMEs (only for opiate agonists and partial agonists), PRESCRIPTION_COUNT_GREATER_THAN_OR_EQUAL_TO_90_MMEs: Prescriptions ≥90 MMEs (ibid), PATIENT_ZIP: Patient's ZIP code (from 2021)}. Your job is to determine if the question is answerable and create a SQL query that retrieves the data that can be used to answer the question. You can assume that the database is stored in a SQLite database and that the database connection is already established. You may NOT modify the database; you can only query it. When warranted, you should covert data to categorical. You should also decide if the question warrants a plot. You are to respond in the form {"good_q:"Y/N", "SQL": "your query here", "chart":"Y/N"}. For example, if the question is "What is the total number of prescriptions dispensed in 2022?", you should return {"good_q:"Y", "SQL":"select sum(PRESCRIPTION_COUNT) as prescriptions from patient where year=2022", "chart":"N"}. If the question is "What is the total number of prescriptions dispensed in 2022 by drug schedule?", you should return {"good_q:"Y", "SQL":"select sum(PRESCRIPTION_COUNT) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE", "chart":"Y"}.
    """
    return f"{question}"

@ell.simple(model="gpt-4o-mini", temperature=0.2)
def create_question_chart(question: str, query:str, first_rows):
    """
    You are a plotly express expert and a fan of high quality visualizations. A colleague is trying to answer a question and needs your help creating a chart. He has come up with a SQL query already. You will create a chart based on the query and the data from the query. You can only make bar, scatter, line, or pie charts. You are to respond in the form {"type":"bar/scatter/line/pie", "kwargs":{kwargs}}. Where kwargs are valid arguments for the chart function you are using. For example, if the question is "What is the total number of prescriptions dispensed in 2022 by drug schedule?" and the query is "select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE", you should return {"type":"bar", "kwargs":{"x":"DEA_DRUG_SCHEDULE", "y":"prescriptions"}}.
    """
    return f"The question was: {question}. The query was: {query}. The first rows of the data are: {first_rows}"


@ell.simple(model="gpt-4o-mini", temperature=0.2)
def create_interpretation_table(question: str, query:str, df_split):
    """
    You are a data interpretation expert. A colleague is trying to answer a question and needs your help writing a response. He has come up with a SQL query already. You will write analysis of the resulting table. You are to respond in the form "{analysis}. I've based my response on this SQL query: {query}" For example, if the question is "What is the total number of prescriptions dispensed in 2022 by drug schedule?" and the query is "select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE", and the data is "prescriptions": [100, 200, 300], "DEA_DRUG_SCHEDULE": [2, 3, 4], you should return "The total number of prescriptions dispensed in 2022 by drug schedule is 100 for schedule 2, 200 for schedule 3, and 300 for schedule 4. I'm responding based on this SQL query: select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE"
    """
    return f"The question was: {question}. The query was: {query}. The SQL response is: {df_split}"

@ell.simple(model="gpt-4o-mini", temperature=0.2)
def create_interpretation_chart(question: str, query:str, chart: Image.Image):
    """
    You are a visualization/chart interpretation expert. A colleague is trying to answer a question and needs your help writing a response. He have already come up with a plot. Your role is to interpret the plot. You are to respond in the form "{analysis}. The data for analysis came from this SQL query: {query}" For example, if the question is "What is the total number of prescriptions dispensed in 2022 by drug schedule?" and the query is "select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE". You should return "{analysis}. I'm responding based on this SQL query: select sum(prescription_count) as prescriptions, DEA_DRUG_SCHEDULE from patient where year=2022 group by DEA_DRUG_SCHEDULE"
    """
    return f"The question was: {question}. The query was: {query}. The chart created is: {chart}"

def first_rows(df):
    return df.head(10).to_json(orient='records')

def make_plot(df, chart_type, **kwargs):
    if chart_type == 'bar':
        return px.bar(df, **kwargs)
    elif chart_type == 'scatter':
        return px.scatter(df, **kwargs)
    elif chart_type == 'line':
        return px.line(df, **kwargs)
    elif chart_type == 'pie':
        return px.pie(df, **kwargs)
    else:
        raise ValueError(f"Invalid chart type: {chart_type}")
    
def parse_sql_resp(response):
    try:
        parsed = json.loads(response)
        return (
            parsed.get('good_q', 'N') == 'Y',
            parsed.get('SQL', ''),
            parsed.get('chart', 'N') == 'Y'
        )
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from create_question_sql")
        return False, '', False
    
def parse_chart_resp(response):
    try:
        parsed = json.loads(response)
        return parsed.get('type', ''), parsed.get('kwargs', {})
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from create_question_chart")
        return '', {}
    
def answer_question(question) -> Tuple[str, dash_table.DataTable, dcc.Graph]:
    # Generate SQL query
    sql_response = create_question_sql(question)
    is_good_question, sql_query, needs_chart = parse_sql_resp(sql_response)
    
    if not is_good_question:
        return "Sorry, I can't answer that question with the data available.", None, None

    # Run the SQL query
    df = run_query(sql_query)
    
    if df.empty:
        return "Something went wrong. Try again or ask a different question", None, None

    if needs_chart:
        # Generate chart
        chart_response = create_question_chart(question, sql_query, first_rows(df))
        chart_type, chart_kwargs = parse_chart_resp(chart_response)
        
        fig = make_plot(df, chart_type, **chart_kwargs)
        png = fig.to_image(format="png")
        image = Image.open(BytesIO(png))
        interp = create_interpretation_chart(question, sql_query, image)
    else:
        interp = create_interpretation_table(question, sql_query, df.to_json(orient='split'))
        fig = None
    return interp, dash_table.DataTable(*df_to_table(df)), dcc.Graph(figure=fig) if needs_chart else None
