import pandas as pd
import sqlite3
import os 
def run_query(query):
    with sqlite3.connect(os.path.join(os.getcwd(), 'data', 'michigan_drug.db')) as conn:
        df = pd.read_sql(query, conn)
    return df

def df_to_table(df):
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]