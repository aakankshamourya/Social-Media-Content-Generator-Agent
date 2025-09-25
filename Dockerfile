FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# keep project path importable
ENV PYTHONPATH=/app

WORKDIR /app

COPY . /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential gcc git curl make cmake \
    python3-dev libpq-dev default-libmysqlclient-dev \
    libxml2-dev libxslt1-dev libssl-dev libffi-dev \
    cargo \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel
RUN pip install streamlit
COPY requirements.txt .
RUN pip install -r requirements.txt
# If you're using a build backend like poetry-core, un-comment the next line:
# RUN pip install poetry-core

# install package in editable mode (will work once you add pyproject.toml or setup.py)
RUN pip install --no-cache-dir -e . --verbose

EXPOSE 8080

CMD ["python", "app.py"]
