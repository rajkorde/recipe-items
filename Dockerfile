FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install uv && uv venv .venv && uv pip install --system -r pyproject.toml

EXPOSE 8000

CMD ["sh", "-c", "marimo run frontend.py --host 0.0.0.0 --port ${PORT:-8000}"]
