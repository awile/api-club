# 3. Hot Reloading Code for Development
Last step we dockerized our FastAPI application and created a dockerized database with docker compose.
However, our current setup is missing a few key features that we make development much easier.

### Table of Contents
1. [Docker volumes](#docker-volumes)
2. [Hot reloading](#docker-working-directory)
5. [Challenge](#challenge)


### Docker volumes
When we run our docker container, we copy our application code into the container.
However, if we make a change to our code it won't be reflected in the container.
That is because we copied the code into the container and it is not linked to our local filesystem.

Test it out by starting your docker container and printing out the app.main file.
```bash
docker compose up -d
docker compose exec api_server bash
cat app/main.py
```

Now change the response `{"status": "ok"}` to `{"status": "changed"}` and save the file.
if you call the endpoint or print out the file again you will see the change is not reflected.

We can solve this with docker volumes which can bind a local directory to a directory in the container.
By adding the following to our docker container we can restart with docker compose and then see that the change is reflected above.
```yaml
services:
    api_server:
      container_name: api_server
      image: api
      volumes:
        - ./app:/app
      ...
```


### Docker working directory
Let's change our status endpoint `app/main.py` to  `{"status": "okay"}` and restart our container.
```bash
$ docker compose down
$ docker compose up -d
$ curl http://localhost:8000
{"status":"okay"}
```
We see that the status is now changed to `okay` even though we didn't rebuild our docker image.
However, if we change the status back to `ok` and don't restart our container, we will still see the status as `okay`. There are two issue preventing this from working as expected:

1. First, we are running fastapi in production mode which doesn't support hot reloading.

   To fix this we can override our command in our docker-compose file to run fastapi in development mode.
   ```yaml
    services:
    api_server:
      container_name: api_server
      image: api
      command: "fastapi dev --host 0.0.0.0"
    ...
    ```
    If we check the logs after starting our container we will see that fastapi is running in development mode.
    ```bash
    $ docker compose up -d
    $ docker logs api_server -f
    ╭────────── FastAPI CLI - Development mode ───────────╮
    │                                                     │
    │  Serving at: http://0.0.0.0:8000                    │
    │                                                     │
    │  API docs: http://0.0.0.0:8000/docs                 │
    │                                                     │
    │  Running in development mode, for production use:   │
    │                                                     │
    │  fastapi run                                        │
    │                                                     │
    ╰─────────────────────────────────────────────────────╯
    ```

2. Second, we are running our server from the root directory which is not best practices and causes issues with detecting changes in our mounted volume (i.e. our local code).

   To fix this we can set the working directory in Dockerfile to `/code`
   ```Dockerfile
    FROM python:3.12.2-alpine3.19

    WORKDIR /code

    COPY ./requirements.txt /code/app/requirements.txt

    RUN pip install --no-cache-dir -r /code/app/requirements.txt

    COPY ./app /code/app

    CMD ["fastapi", "run", "app/main.py"]
   ```
   We will also need to update our docker-compose file to reflect this change.
   ```yaml
    services:
      api_server:
        container_name: api_server
        image: api
        command: "fastapi dev --host 0.0.0.0"
        volumes:
          - ./app:/code/app
        ...
   ```


Now if we restart our container then make a change we will see it reflected in our server and the logs.
```bash
$ docker compose down $ docker compose up -d
$ curl http://localhost:8000
{"status":"ok"}
$ curl http://localhost:8000
{"status":"okay"}
```


### Challenge
1. Why do we set the host when running `fastapi dev --host 0.0.0.0` but not `fastapi run`? And what happens if we don't set the host?
