import requests
import psycopg2
import time
from configparser import ConfigParser
import csv


def checks_export(ip_value):
    try:
        FILE = 'config.ini'
        CONFIG = ConfigParser()
        CONFIG.read(FILE)
        
        conn = psycopg2.connect(
            host = CONFIG['database']['hostname'],
            dbname = CONFIG['database']['database'],
            user = CONFIG['database']['username'],
            password = CONFIG['database']['pwd'],
            port = CONFIG['database']['port_id'])
        cur = conn.cursor()


        sql_part_one = "SELECT * FROM checks WHERE ip='"
        sql_part_two = "' ORDER BY time_of_check"
        sql = sql_part_one + ip_value + sql_part_two
        file = ip_value +'.csv'

        file_path = r'Path to the export folder'+ file

        cur.execute(sql)
        results = cur.fetchall()

        headers = [i[0] for i in cur.description]

        csvFile = csv.writer(open(file_path, 'w', newline=''), delimiter = ',', lineterminator= '\r\n', quoting = csv.QUOTE_ALL, escapechar = '\\')

        csvFile.writerow(headers)
        csvFile.writerows(results)

        conn.commit()
    except Exception as error:
        print(error)

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
