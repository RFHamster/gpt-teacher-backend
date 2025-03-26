#!/bin/bash
# entrypoint.sh

# Ativa o modo de debug para facilitar troubleshooting
set -e

# Comando para rodar o servidor com hot reload, workers e timeout estendido
exec uv run gunicorn app.main:app \
    --workers 4 \
    --threads 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --reload \
    --timeout 1800 \
    --log-level debug