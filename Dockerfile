FROM python:3.11-slim AS webbuild
WORKDIR /app
RUN python -m pip install --no-cache-dir pygbag==0.9.3
COPY . .
RUN python -m task5.build_web

FROM python:3.11-slim
WORKDIR /app
COPY requirements-server.txt ./
RUN python -m pip install --no-cache-dir -r requirements-server.txt
COPY . .
COPY --from=webbuild /app/build/web-source/build/web /app/web
ENV PYTHONUTF8=1 WEB_BUILD_DIR=/app/web
CMD ["sh", "-c", "exec uvicorn task5.server.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
