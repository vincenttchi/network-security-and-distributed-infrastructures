# Image for a P2P node
FROM python:3.11-slim

WORKDIR /app

# Install deps first so this layer caches when only node.py changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY node.py .

EXPOSE 5000

CMD ["python", "node.py"]
