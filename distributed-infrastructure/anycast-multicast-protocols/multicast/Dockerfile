# Creating base image
FROM python:3.11-slim AS base
RUN apt-get update && apt-get install -y tcpdump
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Multicast Receiver docker container config.
FROM base AS receiver
COPY multicast_receiver.py .

# Multicast Sender docker container config.
FROM base AS sender
COPY multicast_sender.py .
