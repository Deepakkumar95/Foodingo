FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps, install Python packages, then remove build deps to keep image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements_live.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements_live.txt

COPY . /app

# Create a non-root user and drop privileges
RUN groupadd -r app && useradd -r -g app app && chown -R app:app /app

USER app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "live_app:app", "--host", "0.0.0.0", "--port", "8000"]
