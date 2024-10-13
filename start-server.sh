#!/bin/sh
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "Error running migrations"
    exit 1
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000
