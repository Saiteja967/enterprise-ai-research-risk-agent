FROM node:24-bookworm-slim AS web
WORKDIR /source/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --create-home --uid 10001 analyst
COPY backend/ backend/
COPY alembic.ini .
COPY data/ data/
COPY --from=web /source/frontend/dist frontend/dist
RUN mkdir -p .runtime && chown analyst:analyst .runtime
USER analyst
EXPOSE 8000
CMD ["sh", "-c", "python -m backend.risk.bootstrap && exec uvicorn backend.risk.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
