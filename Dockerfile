# ---- Stage 1 : Builder ----
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/packages

# ---- Stage 2 : Runtime ----
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/packages /app/packages
COPY app/ ./app/
ENV PYTHONPATH=/app/packages

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app/data

USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]