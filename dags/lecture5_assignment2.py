from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import logging

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
    logging.info('json:', f_json)
    logging.info("Extract done")
    return f_json


def load(json_array):
    logging.info("load started")
    cur = get_Redshift_connection()
    sql = "BEGIN;DELETE FROM demi.weather_forecast;"
    for elem in json_array:
        if not row:
            continue
        date = elem['dt']
        temperature = elem['temp']['day']
        min_temperature = elem['temp']['min']
        max_temperature = elem['temp']['max']
        sql += f"INSERT INTO demi.name_gender VALUES ({date}, {temperature}, {min_temperature}, {max_temperature});"
    sql += "END;"
    cur.execute(sql)
    logging.info(sql)
    logging.info("load done")


def etl():
    response_json = extract_json()
    load(response_json)

dag_second_assignment = DAG(
	dag_id = 'lecture5_assignment2',
    catchup = False,
	start_date = datetime(2021,11,27), # 날짜가 미래인 경우 실행이 안됨
	schedule_interval = None)  # 적당히 조절

task = PythonOperator(
	task_id = 'perform_etl',
	python_callable = etl,
	dag = dag_second_assignment)
