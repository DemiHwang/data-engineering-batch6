from airflow import DAG
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import logging
import json

VARIABLE_OPEN_WEATHER_MAP_KEY = 'openweathermap'
SEOUL_LATTITUDE = 37.53
SEOUL_LONGITUDE = 127.02

def get_Redshift_connection():
    hook = PostgresHook(postgres_conn_id='lecture_redshift')
    return hook.get_cursor()

def extract_json(exclude_parts='minutely,hourly'):
    TEMPLATE_URL = "https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}"

    logging.info("Call open weather map API")
    f = requests.get(
        TEMPLATE_URL.format(
            lat=SEOUL_LATTITUDE,
            lon=SEOUL_LONGITUDE,
            part=exclude_parts,
            api_key=Variable.get('openweathermap')
        )
    )
    f_json = f.json()
    logging.debug(json.dumps(f_json))
    logging.info("Extract done")
    return f_json


def load(json_array):
    logging.info("load started")
    cur = get_Redshift_connection()
    sql = "BEGIN;DELETE FROM demi.weather_forecast;"
    for elem in json_array['daily']:
        if not elem:
            continue
        date = datetime.utcfromtimestamp(elem['dt']).strftime('%Y-%m-%d')
        temperature = elem['temp']['day']
        min_temperature = elem['temp']['min']
        max_temperature = elem['temp']['max']
        sql += f"INSERT INTO demi.temp_weather_forecast VALUES ('{date}', {temperature}, {min_temperature}, {max_temperature});"
    sql += "END;"
    cur.execute(sql)
    logging.info(sql)
    logging.info("load done")


def etl():
    response_json = extract_json()
    load(response_json)


DAG_ID = "lecture5_assignment2"
default_args = {
    "concurrency": 1,
    "catchup": False,
    "start_date": datetime(2021, 11, 27)
}

with DAG(DAG_ID, default_args=default_args, schedule_interval=None) as dag:
    create_and_replicate_table = RedshiftSQLOperator(
        task_id='create_and_replicate_table',
        sql=[
            """
            CREATE TABLE IF NOT EXISTS demi.weather_forecast (
                date date PRIMARY KEY,
                temperature double precision,
                min_temperature double precision,
                max_temperature double precision,
                created_date timestamp without time zone DEFAULT getdate()
            );
            """,
            "DROP TABLE IF EXISTS demi.temp_weather_forecast;",
            "CREATE TABLE demi.temp_weather_forecast AS SELECT * FROM demi.weather_forecast;",
        ]
    )

    weathermap_to_redshift = PythonOperator(
        task_id='perform_etl',
        python_callable=etl,
    )

    drop_duplicates = RedshiftSQLOperator(
        task_id='drop_duplicates',
        sql=[
            "BEGIN;",
            "DELETE FROM demi.weather_forecast;",
            """
            INSERT INTO demi.weather_forecast
            SELECT date, temperature, min_temperature, max_temperature, created_date
            FROM (
                SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY date ORDER BY created_date DESC) seq
                FROM demi.temp_weather_forecast)
                WHERE seq = 1;
            END
            """,
        ]
    )

    replicate_table >> weathermap_to_redshift >> drop_duplicates
