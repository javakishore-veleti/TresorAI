FROM python:3.12-slim AS build
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/admin-api/pyproject.toml ./
RUN uv pip install --system --no-cache --requirement pyproject.toml

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY backend/admin-api/app ./app

ENV PORT=8091
EXPOSE 8091
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8091"]
