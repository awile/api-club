# 7. Reverse Proxy


### Table of Contents
1. [A warning](#a-warning)
2. [Create Reverse Proxy](#create-reverse-proxy)
3. [Create Production Docker File](#create-production-docker-file)
4. [Create Production Docker Compose](#create-production-docker-compose)
5. [Test Reverse Proxy Locally](#test-reverse-proxy-locally)
6. [Challenge](#challenge)


### A Warning
From here on, we will be running a "production" system in a manner that many would rightfully consider wrong.
The system we setup is not meant to handle large traffic or critical workflows.
It also does not demonstrate best practices for any software job you may have or hope to have.

But for a system that can server a small amount of users for cheap, it will do the job!
And let's be real, you don't have a large user base or you wouldn't be reading this tutorial.


### Create Reverse Proxy
A reverse proxy is a server (or in our case a process) that accepts client requests and forwards them to the appropriate backend server.
This is useful for routing between multiple servers, load balancing, and security by not directly exposing services to the internet (see more here: [Reverse Proxy](https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/)).

We will use Nginx to create our reverse proxy.
To start, create a new directory in the root of the project called `nginx/` and create a new file called `nginx.conf`.

First, we need to define an upstream block which will can be one or more servers to route to.
In this case, we will be routing to our API server using within docker.
This is why our server address is `api_server` (using dockers internal name routing) and running on port 8000.
```nginx
upstream api-club {
  server api_server:8000;
}
```

Next, we need to define our server block for routing to our API server.
We are listening on port 443 (for https, 80 for http) and setting the server name to `apiclub.com`.
This means our server will only handle requests for the domain name `http://apiclub.com`.

Breaking down the location block:
- `location /` - matches all requests the start with `/` which is all of them, this could be `/tasks` or anything else
- `proxy_pass http://api-club;` - forwards the request to the upstream server defined above i.e. our API dockerized service
- `proxy_set_header Host $host;` - passes the host sent from the original request, important if we want to server multiple domains on the same server or handle requests differently based on the host
- The last two headers are for passing the users ip address and the original request ip address, useful for logging, analytics, and security
```nginx
server {
  listen 443 ssl;
  server_name apiclub.com;

  location / {
      proxy_pass http://api-club;
      proxy_set_header Host $host; # Forwarded host
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

Next we want to redirect all http requests to https.
```nginx
server {
  listen 80 default_server;
  server_name _;

  location / {
      return 301 https://$host$request_uri;
  }
}
```

And finally we can wrap this in a file called `Dockerfile.nginx` to build our nginx server.
```Dockerfile
FROM nginx:mainline-alpine-slim

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
```

### Create Production Docker File
Next, we need to update our Dockerfile for running our API server in production.
The main change we need to make is running db migrations before starting the server.
To do this let's create a new file called `start-server.sh` in the root of the project.
```bash
#!/bin/sh
alembic upgrade head
if [ $? -ne 0]; then
    echo "Error running migrations"
    exit 1
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This runs the alembic upgrade command to apply any new migrations to the database.
If the command fails, we exit with an error code.
Finally, we start the server using uvicorn, which is an ASGI server we will talk about later but you can read more about it [here](https://www.uvicorn.org/).

Next, we need to update our Dockerfile to copy this file and run it.
```Dockerfile
...
COPY ./alembic.ini /code/alembic.ini

COPY ./start-server.sh /code/start-server.sh

CMD ["./start-server.sh"]
```

We also need to make sure our new start-server bash script is executable.
```bash
$ chmod +x start-server.sh
```


### Create Production Docker Compose
Now we have a way to route to our api server and a way to run it in production.
The last step is to create a docker compose file for running these services together in production.
First, create a new file called `docker-compose.prod.yml` in the root of the project.
```yaml
services:
   api_server:
     container_name: api_server
     image: api
     volumes:
       - ./data:/code/data
     environment:
       DB_FILE_PATH: /data/api.db
     networks:
       - api

   nginx:
     container_name: nginx
     image: nginx_app
     ports:
       - "443:443"
       - "80:80"
     networks:
       - api

networks:
  api:
    driver: bridge
```

We can run this and our api and reverse proxy will start, but we won't be able to access the api server since we don't have a domain name or ssl setup.

### Test Reverse Proxy Locally
To test our routing we can use a unix tool called `traceroute`.
```bash
$ traceroute apiclub.com
traceroute: unknown host apiclub.com
```

But since we don't have a domain name setup we can't test this locally.
(note this url may exist at somepoint but we can still override this or any other domain locally)
To override the domain we need to edit our `/etc/hosts` file.
```bash
$ sudo nano /etc/hosts
127.0.0.1       apiclub.com
```
Then add the following line to the bottom of the file.

Now if we run our traceroute command again we should see the request being routed to localhost.
```bash
$ traceroute apiclub.com
traceroute to apiclub.com (127.0.0.1), 64 hops max, 40 byte packets
 1  localhost (127.0.0.1)  0.987 ms  0.048 ms  0.040 ms
```

But we still can't access the api server since we don't have ssl setup.
To do that we will use a tool called `mkcert` which will create a local certificate authority and generate a certificate for localhost.
```bash
$ brew install mkcert
$ mkcert -install
Created a new local CA 💥
Sudo password:
The local CA is now installed in the system trust store! ⚡️
$ cd nginx/ && mkcert apiclub.com
Created a new certificate valid for the following names 📜
 - "localhost"

The certificate is at "./apiclub.com.pem" and the key at "./apiclub.com-key.pem" ✅

It will expire on 13 January 2027 🗓
```

This will create to files `apiclub.com.pem` and `apiclub.com-key.pem` which we can use for ssl.
Now we just need to add them to our `nginx.conf` file and our `Dockerfile.nginx`.
```nginx
server {
  listen 443 ssl;
  server_name apiclub.com;

  ssl_certificate /etc/nginx/apiclub.com.pem;
  ssl_certificate_key /etc/nginx/apiclub.com-key.pem;

  location / {
  ...
}
```

```Dockerfile
...
COPY ./nginx/localhost.pem /etc/nginx/apiclub.com.pem

COPY ./nginx/localhost-key.pem /etc/nginx/apiclub.com-key.pem
```

And with that we can test out our app in a few steps:
1. Build the nginx config `docker build . -t nginx_app -f Dockerfile.nginx`
2. Build the api server `docker build . -t api`
3. Run the production docker compose `docker compose -f docker-compose.prod.yml up`


And to verify it's working we can use curl to make a request to our api server.
```bash
$ curl https://apiclub.com/
{"status":"ok"}%
```


### Challenge
1. Add a the api service under another domain and have nginx route to it.
