FROM python:3.11

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
