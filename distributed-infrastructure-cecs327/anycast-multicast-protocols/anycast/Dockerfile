FROM python:3.11-slim

RUN apt-get update && apt-get install -y tcpdump

WORKDIR /app

COPY server.py .
COPY client.py .
