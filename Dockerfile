# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Postgres client + MariaDB dev libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev-compat \
    libmariadb-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .

# Prepare app folder and permissions
RUN mkdir -p /app/media \
    && useradd -m kyjuanbrown \
    && chown -R kyjuanbrown:kyjuanbrown /app

USER kyjuanbrown
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
