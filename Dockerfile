FROM python:3.11-slim
WORKDIR /app
COPY requirements-server.txt ./
RUN python -m pip install --no-cache-dir -r requirements-server.txt
COPY . .
ENV PYTHONUTF8=1
CMD ["sh", "-c", "uvicorn task5.server.app:app --host 0.0.0.0 --port ${PORT:-8000}"]