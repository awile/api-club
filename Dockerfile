FROM python:3.12.2

WORKDIR /code

COPY ./app /code/app

COPY ./requirements.txt /code/app/requirements.txt

RUN pip install --no-cache-dir -r /code/app/requirements.txt

CMD ["fastapi", "run", "app/main.py"]
