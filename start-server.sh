#!/bin/sh
alembic upgrade head
if [ $? -ne 0 ]; then
  echo "Migrations failed. Exiting."
  exit 1
fi

fastapi run app/main.py
