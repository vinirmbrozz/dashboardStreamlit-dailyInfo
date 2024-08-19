import psycopg2
import redis
import json
import time
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import altair as alt
import streamlit as st
import datetime
import matplotlib.pyplot as plt
import altair as alt

## OPERATIONAL VALUES FROM REDIS
########################################################################################
redis_conn = None
try:
    redis_conn = redis.Redis(host='redis',port='6379')
    env        = redis_conn.get('system_config')
    if env:
        env    = json.loads(env)
    else:
        print("REDIS KEY system_config FAILED CONFIG")
        time.sleep(20)
        sys.exit(0)

except Exception as ex:
    print('REDIS SERVICE OFFLINE', ex)
    time.sleep(15)            # WAIT FOR SERVICE BEFORE RESTART
    sys.exit(0)

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
    
def plotHistogram(vps):
    data = getLogHostname(vps)
    data['Cpu'] = [float(cpu.replace('%', '')) for cpu in data['Cpu']]
    data['Horas'] = [hora.split(' ')[1] for hora in data['Dia e Hora']]
    data['Hora'] = [hora.split(':')[0] for hora in data['Horas']]
    
    chart = alt.Chart(data).mark_circle().encode(
        x=alt.X('Hora:O', axis=alt.Axis(title='Hora do Dia', labelAngle=0)),
        y=alt.Y('Cpu:Q', axis=alt.Axis(title='Uso da CPU (%)')),
        color='Hostname:N',
        tooltip=['Dia e Hora', 'Cpu', 'Hostname']
    ).interactive()
    
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
    
def getLogHostname(vps):
    conn = connectDataBase()
    cur = conn.cursor()
    data = datetime.datetime.now()
    data = data.strftime('%Y-%m-%d')
    if vps == 'Todas':
        cur.execute(f"SELECT payload FROM logs.daily_info WHERE log_date >= '{data}'")
    else:
        cur.execute(f"SELECT payload FROM logs.daily_info WHERE hostname = '{vps}' and log_date >= '{data}'")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    df = pd.DataFrame([json.loads(row[0]) for row in rows])
    
    return df

def getHostnames():
    conn = connectDataBase()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT hostname FROM status.daily_info")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def getInfoStatus():
    conn = connectDataBase()
    cur = conn.cursor()
    cur.execute("SELECT payload FROM status.daily_info")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    df = pd.DataFrame([json.loads(row[0]) for row in rows])
    
    # Atualizando status do dashboard após buscar informações no banco de dados
    status = redis_conn.get("dashboard").decode("utf-8")
    status = json.loads(status)
    status['status'] = "Atualizado"
    status = json.dumps(status)
    redis_conn.set("dashboard", status)
    
    return df


# {"Dia e Hora": "26-02-2024 21:46:43", "Hostname": "psa-vps-14", "IP": "45.61.55.253", "Cpu": "97.3%", "Memoria": "1334.9:3929.7:66.0%", "Disco": "50.2:78.6:32.7%", "numeroLinha": 14}

def graficoCPU(graficoCPU, data):
    data['Cpu'] = [float(cpu.replace('%', '')) for cpu in data['Cpu']]
    
    corEscala = px.colors.diverging.RdYlGn[::-1]
    figBarras = px.bar(data,
                       x='Hostname',
                       y='Cpu',
                       title='Uso de CPU',
                       labels={'Hostname': 'Hostname', 'Cpu': 'Uso de CPU'},
                       color='Cpu',
                       color_continuous_scale=corEscala)
    
    figBarras.update_layout(yaxis=dict(range=[0, 100]))
    
    graficoCPU.plotly_chart(figBarras, use_container_width=True)
    
def graficoMemoria(graficoMemoria, data):
    data['Memoria'] = [float(memoria.split(':')[2].replace('%', '')) for memoria in data['Memoria']]
    
    # Calculando uma escala de cores personalizada
    cor_escala = px.colors.diverging.RdYlGn[::-1]

    # Criando o gráfico de barras com Plotly Express
    figBarras = px.bar(data, 
                    x='Hostname', 
                    y='Memoria', 
                    title='Uso de Memória',
                    labels={'Hostname': 'Hostname', 'Memoria': 'Uso de Memória'}, 
                    color='Memoria', 
                    color_continuous_scale=cor_escala)
    figBarras.update_layout(yaxis=dict(range=[0, 100]))
    
    graficoMemoria.plotly_chart(figBarras, use_container_width=True)
    
def graficoDisco(graficoDisco, data):
    data['Disco'] = [float(disco.split(':')[2].replace('%','')) for disco in data['Disco']]
    
    # Calculando uma escala de cores personalizada
    cor_escala = [(0, 'green'), (0.5, 'yellow'), (1, 'red')]

    # Criando o gráfico de barras com Plotly Express
    figBarras = px.bar(data, 
                    x='Hostname', 
                    y='Disco', 
                    title='Uso de Disco',
                    labels={'Hostname': 'Hostname', 'Disco': 'Uso de Disco'}, 
                    color='Disco', 
                    color_continuous_scale=cor_escala)
    figBarras.update_layout(yaxis=dict(range=[0, 100]))
    
    graficoDisco.plotly_chart(figBarras, use_container_width=True)