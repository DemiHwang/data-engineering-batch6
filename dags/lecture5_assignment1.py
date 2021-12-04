from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import logging

def get_Redshift_connection():
    hook = PostgresHook(postgres_conn_id='lecture_redshift')
    return hook.get_cursor()

def extract(url):
    logging.info("Extract started")
    f = requests.get(url)
    logging.info("Extract done")
    return (f.text)


def transform(text):
    logging.info("transform started")
    # ignore the first line - header
    lines = text.split("\n")[1:]
    logging.info("transform done")
    return lines


def load(lines):
    logging.info("load started")
    cur = get_Redshift_connection()
    sql = "BEGIN;DELETE FROM demi.name_gender;"
    for l in lines:
        if l != '':
            (name, gender) = l.split(",")
            sql += f"INSERT INTO demi.name_gender VALUES ('{name}', '{gender}');"
    sql += "END;"
    cur.execute(sql)
    logging.info(sql)
    logging.info("load done")


def etl():
    link = "https://s3-geospatial.s3-us-west-2.amazonaws.com/name_gender.csv"
    data = extract(link)
    lines = transform(data)
    load(lines)



DAG_ID = "lecture5_assignment1"
default_args = {
    "concurrency": 1,
    "catchup": False,
    "start_date": datetime(2021, 11, 27)
}

with DAG(DAG_ID, default_args=default_args, schedule_interval=None) as dag:
    task = PythonOperator(
        task_id = 'perform_etl',
        python_callable = etl,
    )
