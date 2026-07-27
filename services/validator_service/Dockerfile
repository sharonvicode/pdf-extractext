FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && \
    uv sync --no-dev

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
