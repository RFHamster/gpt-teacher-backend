FROM python:3.11-slim

WORKDIR /app/

RUN apt update && \
    apt-get -y install --no-install-recommends \
    curl \
    build-essential \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

# Copiar arquivos do projeto
COPY ../../pyproject.toml /app/
COPY ../../poetry.lock /app/

# Instalar dependências com base no ambiente
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        poetry install --no-root; \
    else \
        poetry install --no-root --only main; \
    fi


ARG GITHUB_TOKEN
# ARG BIOFY_DB_BRANCH=master
RUN echo "Instalando Biofy Packages (bf-db branch master)" >&2 && \
    pip install -U git+https://${GITHUB_TOKEN}@github.com/biofy/biofy-db.git@create_qdrant && \
    pip install -U git+https://${GITHUB_TOKEN}@github.com/biofy/biofy-utils.git@master

ENV PYTHONPATH=/app

ARG OCI_USER_ID
ARG OCI_TENANCY_ID
ARG OCI_FINGERPRINT
ARG OCI_API_KEY
ARG OCI_REGION

ENV OCI_USER_ID=$OCI_USER_ID
ENV OCI_TENANCY_ID=$OCI_TENANCY_ID
ENV OCI_FINGERPRINT=$OCI_FINGERPRINT
ENV OCI_API_KEY=$OCI_API_KEY
ENV OCI_REGION=$OCI_REGION


COPY ./app /app/app

ENV PYTHONPATH=/app

CMD ["python3", "-u", "app/main_document_ingest.py"]


