FROM python:3.12-slim 

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENV PYTHONPATH=/app
EXPOSE 7860

CMD ["uv", "run", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860"]
