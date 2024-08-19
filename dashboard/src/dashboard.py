import time, json, sys
import streamlit as st
import extra_streamlit_components as stc
import redis
import datetime
import hashlib

from Exchange import QueueExchange
from Logger import LogService

from functions import *
    
st.set_page_config(layout="wide")

# RECEBE E VALIDA O COOKIE
cookie_manager = stc.CookieManager()
cookie = cookie_manager.get(cookie="sistemas.token")
print(f"COOKIE: {cookie}", flush=True)

if not cookie:
    print("COOKIE INEXISTENTE")
    cookies = cookie_manager.get_all()
    print("ALL COOKIES: ", cookies, flush=True)
    st.error("AUTENTICAÇÃO INEXISTENTE")
    print(cookies, flush=True)
    time.sleep(10)
    sys.exit(1)

# CONFIGURA O LOGGER
if "prev_logger" not in st.session_state:
    try:
        logger = LogService(amqps= env["amqps"],
                            system= "dailyInfo", 
                            service= "dashboard", 
                            logType= "logs", 
                            logLocal= True, 
                            client=env["nome_cliente"])
        logger.heartBeat()
        logger.logMsg("SERVICE DAILYINFO DASHBOARD STARTING")
        st.session_state["prev_logger"] = logger
    except Exception as e:
        print("SERVICE LOGGER DOWN: ", e, flush=True)
        time.sleep(10)
        sys.exit(1)
else:
    logger = st.session_state["prev_logger"]

# CONFIGURA O SERVIDOR REDIS
rd = None
print("CONFIGURANDO SERVIDOR REDIS")
if "prev_rd" not in st.session_state:
    env = {}
    try:
        rd = redis.Redis("redis", 6379)
        envjs = rd.get("system_config")
        if envjs is None:
            print("CHAVE system_config NAO ENCONTRADA")
            time.sleep(10)
            sys.exit(1)
        env = json.loads(envjs)
        st.session_state["prev_env"] = env
        st.session_state["prev_rd"] = rd
        print(f"SERVICE CONFIGURED FOR CLIENT {env['nome_cliente']}", flush=True)
    except Exception as e:
        print("SERVICE REDIS DOWN: ", e, flush=True)
        time.sleep(10)
        sys.exit(1)
else:
    rd  = st.session_state["prev_rd"]
    env = st.session_state["prev_env"]

if not ':' in cookie or len(cookie.split(':')) != 2:
    logger.logMsgError("FORMATO COOKIE INVALIDO")
    time.sleep(10)
    sys.exit(1)
usr_email, usr_token = cookie.split(":")
# VERIFICA IDENTIFICACAO
usr_authjs = rd.get(f"usr_{usr_email}")
if usr_authjs is None:
    logger.logMsgError(f"AUTENTICACAO INEXISTENTE PARA {usr_email}")
    time.sleep(10)
    sys.exit(1)

try:
    usr_auth = json.loads(usr_authjs)
except:
    st.write(usr_authjs)

if  not (str(usr_token) == str(usr_auth["uuid_original"][:18])):
    logger.logMsgError("AUTENTICACAO INVALIDA NIVEL 1")
    logger.logMsg(f"[{usr_auth['uuid_original'][:18]}] != [{usr_token}]")
    time.sleep(10)
    sys.exit(1)

# VALIDA O SECRET COM O SECURITY DO USUARIO, SE NAO BATER, DESLOGA
secretSrc = cookie + usr_auth["uuid_original"] + rd.get("sid").decode("utf-8")
print(f"SECRET SRC: {secretSrc}", flush=True)
security  = usr_auth["security"]
print(f"SECURITY: {security}", flush=True)
secret = hashlib.sha256(secretSrc.encode("UTF-8")).hexdigest()
print(f"SECRET: {secret}", flush=True)
if  not (str(secret) == str(security)):
    logger.logMsgError("AUTENTICACAO INVALIDA NIVEL 2")
    logger.logMsg(f"[{secret}] != [{security}] Cookie [{cookie}]")
    time.sleep(10)
    sys.exit(1)

# CRIA AS ABAS DO DASHBOARD
infoGrafico, histograma = st.tabs(['Informações do Sistema', 'Histograma'])

data = getInfoStatus()

# MONTA AS OPÇÕES DE VPS NA SELECTBOX NA SIDEBAR
hostnames = getHostnames()
hostnames = [hostname[0] for hostname in hostnames]
hostnames.insert(0,'Todas')
hostnames = pd.DataFrame(hostnames, columns=['hostname'])

# SIDEBAR
st.sidebar.title('Selecione o VPS')
vps = st.sidebar.selectbox('', hostnames)

# BUSCA NO REDIS AS INFORMAÇÕES PARA O DASHBOARD
dadosDashboard = rd.get("dashboard").decode("utf-8")
dadosDashboard = json.loads(dadosDashboard)

# BOTÃO PARA ATUALIZAR OS DADOS
if st.sidebar.button(f"Atualizar"):
    dadosDashboard['status'] = "Atualizando"
    dadosDashboardJS = json.dumps(dadosDashboard)
    rd.set("dashboard", dadosDashboardJS)
    st.rerun()
    
# CONDIÇÃO PARA TRAVAR A TELA ENQUANTO AGUARDA A ATUALIZAÇÃO DOS DADOS.
if dadosDashboard['status'] == "Atualizando":
    st.sidebar.markdown(
        f"<h2 style='font-size:1em;'>📊 Atualizando aguarde...</h2>",
        unsafe_allow_html=True
    )
    while True:
        dadosDashboard = rd.get("dashboard").decode("utf-8")
        if dadosDashboard['status'] == "Atualizado":
            st.rerun()
            break
        time.sleep(1)

# GRAFICOS
with infoGrafico:
    st.title('Dashboard DailyInfo')
    col1, col2, col3 = st.columns(3)
    grafico1 = col1.empty()
    grafico2 = col2.empty()
    grafico3 = col3.empty()

    grafico1.write('CPU')
    grafico2.write('Memória')
    grafico3.write('Disco')
    
    graficoCPU(grafico1, data)
    graficoMemoria(grafico2, data)
    graficoDisco(grafico3, data)

# HISTOGRAMA
with histograma:
    st.title('Histograma')
    
    plotHistogram(vps)