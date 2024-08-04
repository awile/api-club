# 2. Dockerize
This section will go over how we can dockerize our project for development and to prepare for deployment.


### Table of Contents
1. [Create a Dockerfile](#create-a-dockerfile)
2. [Run dockerfile](#run-dockerfile)
3. [Create a docker-compose file](#create-a-docker-compose-file)
4. [Add a postgres database](#add-a-postgres-database)
5. [Update Makefile](#update-makefile)
6. [Challenge](#challenge)


### Create a Dockerfile
First we need to create a Dockerfile to define how our image should be built. If you aren't familiar with docker, or need a refresher on how tit works then I highly recommended reviewing [basic concepts](https://docs.docker.com/guides/docker-concepts/building-images/understanding-image-layers/).

```Dockerfile
FROM python:3.12.2-alpine3.19

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY ./app /app

CMD ["fastapi", "run", "app/main.py"]
```
Above is our dockerfile which will configure our app setup, explaining line by line looks like:
1. First, we will use a base image that has python 3.12.2 installed and configured (we use alpine linux to reduce size)
2. We copy our dependency file into the container (notice we don't need our development dependencies cached for running this)
3. We install all our application dependencies
    - We tell pip to not create a cache directory `--no-cache-dir`
    - This prevents pip from saving files for faster install the second time
    - Since docker containers are best treated as immutable, we won't reinstall and no cache will save space
4. We copy our application code into the container

### Run dockerfile
Now that we have our dockerfile, we can build our image and run it.
To do this, we will use the following command to build our image and name it `api`:
```bash
docker build -t api .
```
Now that we built our image, let's run it in the background `-d` and call it `api_server`:
```bash
docker run -d --name api_server api
```
With `docker ps` running we can see:
```bash
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS                    NAMES
cab9975e4bad   api                    "fastapi run app/mai…"   43 seconds ago   Up 42 seconds                            api_server
```
And we can see our logs with `docker logs api_server` and that our server started running:
```bash
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
However, if we try to connect to server we will get a connection refused error.
```bash
$ curl http://localhost:8000
curl: (7) Failed to connect to localhost port 8000 after 0 ms: Couldn't connect to server
```
This is because we need to expose the port in our container to our host machine.
We can do that by running the following commands:
```bash
$ docker stop api_server
$ docker rm api_server
$ docker run -d --name api_server -p 8000:8000 api
```
Above we stop and remove the container, then run it again with the `-p` flag to expose the port.
Now we see that our server is running with the port exposed:
```bash
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS          PORTS                    NAMES
6d21f43717c0   api                    "fastapi run app/mai…"   2 seconds ago   Up 1 second     0.0.0.0:8000->8000/tcp   api_server
```
Then we can connect to our server:
```bash
$ curl http://localhost:8000
{"status":"ok"}
```

### Create a docker-compose file
This worked well but was a lot of commands to run. We can simplify this by using a `docker-compose.yml` file.
```yaml
services:
  api_server:
    conatiner_name: api_server
    image: api
    ports:
      - "8000:8000"
```
Make sure to stop and remove the container from the previous step, then run the following command:
```bash
docker compose up -d
```
This will start our containers in the background and if we run docker ps we will see that our container is built and named the same as before:
```bash
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS                    NAMES
930022a1ebc5   api                    "fastapi run app/mai…"   42 seconds ago   Up 42 seconds   0.0.0.0:8000->8000/tcp   api_server
```
We can also see our logs with the following command:
```bash
$ docker compose logs
api_server  | INFO:     Started server process [1]
api_server  | INFO:     Waiting for application startup.
api_server  | INFO:     Application startup complete.
api_server  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
And we can connect to our server:
```bash
$ curl http://localhost:8000
{"status":"ok"}
```
Then we can stop our server with the following command and we can see our container has been removed
```bash
$ docker compose down
$ docker ps -a
CONTAINER ID   IMAGE                   COMMAND                  CREATED       STATUS                        PORTS                    NAMES
```

### Add a postgres database
Now that we have our server running, we can add a postgres database to our docker-compose file.
```yaml
services:
  api_server:
    ...

  db:
    container_name: db
    image: postgres:16.3
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: api
```

Notice, we expose the port `5432` for our database and set the environment variables for the database which automatically intialize a database and user based on the variables.
Now we can run our server and database with the following command:
```bash
docker compose up -d
```

Now we can connect to the localpostgres database with the following command and the password `postgres` when asked:
```bash
$ psql -h localhost -d postgres -U postgres
Password for user postgres:
psql (16.3)
Type "help" for help.

postgres=#
```

### Update Makefile
To make this easier to type we will add commands to our Makefile to run our docker-compose commands.
```makefile
start:
    docker compose up -d

stop:
    docker compose down

logs:
    docker compose logs -f
```

Then we can run our server with the following command:
```bash
$ make start
$ make logs
$ make stop
```

### Challenge
1. Currently, we will lose all our postgres data when we stop our container. How can we persist our data?
   - Hint: Look into docker volumes [documentation](https://docs.docker.com/storage/volumes/)
2. How can we ssh into our running api server container?
