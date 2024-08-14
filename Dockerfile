FROM python:3.12.2

WORKDIR /code

COPY ./app /code/app

COPY ./requirements.txt /code/app/requirements.txt

COPY ./alembic.ini /code/alembic.ini

RUN pip install --no-cache-dir -r /code/app/requirements.txt

CMD ["fastapi", "run", "app/main.py"]
