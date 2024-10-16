FROM python:3.12.2-alpine3.19

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /code

COPY ./app /code/app

COPY ./alembic.ini /code/alembic.ini

COPY ./start-server.sh /code/start-server.sh

CMD ["./start-server.sh"]
