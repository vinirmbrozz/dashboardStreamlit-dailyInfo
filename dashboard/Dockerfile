FROM python:3.10

WORKDIR /app
COPY requirements.txt ./
RUN  pip install -r requirements.txt

COPY src .
COPY utils .

CMD [ "streamlit", "run", "dashboard.py" ]