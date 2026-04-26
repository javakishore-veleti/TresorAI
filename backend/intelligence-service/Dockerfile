# Build context = repo root: docker build -f backend/intelligence-service/Dockerfile -t intelligence-service:dev .
FROM python:3.12-slim AS build
WORKDIR /app

# uv for fast deps
RUN pip install --no-cache-dir uv

COPY backend/intelligence-service/pyproject.toml ./
RUN uv pip install --system --no-cache --requirement pyproject.toml

FROM python:3.12-slim
WORKDIR /app

COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY backend/intelligence-service/app ./app
COPY backend/intelligence-service/tresorai ./tresorai

ENV PORT=8090
EXPOSE 8090
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
