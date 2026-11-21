FROM python:3.11-slim AS builder
WORKDIR /app
COPY . .
RUN python -m pip install --no-cache-dir pygbag==0.9.3 && python -m task5.build_web

FROM python:3.11-slim
WORKDIR /app
COPY requirements-server.txt ./
RUN python -m pip install --no-cache-dir -r requirements-server.txt
COPY . .
COPY --from=builder /app/build/web-source/build/web /app/build/web
ENV PYTHONUTF8=1 SQLITE_DB_PATH=/data/game.db WEB_BUILD_DIR=/app/build/web
RUN useradd --uid 10001 --create-home game && mkdir /data && chown game:game /data
USER game
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/api/health', timeout=3)"
CMD ["sh", "-c", "uvicorn task5.server.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]