import psycopg2
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import datetime

def connectDataBase():
    # Connect to the database
    conn = psycopg2.connect(
        host='66.232.106.250',
        database='softgo',
        user='softgo',
        password='L0idenice',
        port=54333
    )
    return conn

def getInfoStatus():
    conn = connectDataBase()
    cur = conn.cursor()
    cur.execute("SELECT payload FROM status.daily_info")
    rows = cur.fetchall()
    print(type(rows))
    cur.close()
    conn.close()
    
    df = pd.DataFrame([json.loads(row[0]) for row in rows])
    
    return df


# {"Dia e Hora": "26-02-2024 21:46:43", "Hostname": "psa-vps-14", "IP": "45.61.55.253", "Cpu": "97.3%", "Memoria": "1334.9:3929.7:66.0%", "Disco": "50.2:78.6:32.7%", "numeroLinha": 14}

def graficoCPU():
    data = getInfoStatus()
    data2 = getLogHostname('psa-vps-6')
    print(data2)
    
    
def getLogHostname(vps):
    conn = connectDataBase()
    cur = conn.cursor()
    data = datetime.datetime.now() - datetime.timedelta(days=2)
    data = data.strftime('%Y-%m-%d')
    cur.execute("SELECT payload FROM logs.daily_info WHERE hostname = %s and log_date >= %s", (vps, data))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    df = pd.DataFrame([json.loads(row[0]) for row in rows])
    
    return df
        
graficoCPU()


data = datetime.datetime.now()
data = data.strftime('%Y-%m-%d')
print(data)