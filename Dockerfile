FROM python:3.12.2

COPY ./app /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["fastapi", "run", "app/main.py"]
