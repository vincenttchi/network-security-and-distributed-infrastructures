# Image for the bootstrap node
FROM python:3.11-slim

WORKDIR /app

# Shares requirements.txt with the p2p node to keep Flask versions aligned
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bootstrap.py .

EXPOSE 5000

CMD ["python", "bootstrap.py"]
