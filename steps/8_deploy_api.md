# 8. Deploy API


### Table of Contents
1. [Get a server](#get-a-server)
2. [Install Docker](#install-docker)
3. [Push Docker Images to Server](#push-docker-images-to-server)
4. [Push Docker Compose file to server](#push-docker-compose-file-to-server)
5. [Add Firewall Rules](#add-firewall-rules)
6. [Test server](#test-server)
7. [Challenge](#challenge)


### Get a server
You can use any kind of server you want for this, wether it's a VPS, a cloud server or even your own computer.
For this example we will assume it's a linux server and this guide will be using a Digital Ocean droplet.

Follow this guide to create a new droplet: [Digital Ocean Droplet](https://docs.digitalocean.com/products/droplets/how-to/create/)


### Install Docker
First, ssh into your server:
```bash
$ ssh root@<your-server-ip>
```

Then we need to run commands to install both `Docker` and `Docker Compose`.
```bash
$ sudo apt-get update
$ sudo apt-get install ca-certificates curl
$ sudo install -m 0755 -d /etc/apt/keyrings
$ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$ sudo chmod a+r /etc/apt/keyrings/docker.asc
$ echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
$ sudo apt-get update
$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

We can now check if Docker is installed by running:
```bash
$ docker --version
$ docker-compose --version
```


### Push Docker Images to Server
To push our Docker image to our server we will leverage to docker commands:
- `docker save` to save the image to a tar file
- `docker load` to load the image from the tar file

This will let use build & prepare the image on our local machine and then push it to the server.
But first we need to build for our server architecture, in this case `linux/amd64`.
```bash
$ docker buildx build --platform linux/amd64 -t api:latest .
$ docker save api:latest | ssh -C root@<server-ip> docker load
```

On your server, you should now see the image:
```bash
$ docker image ls
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
api           latest    db17bc8d8858   2 minutes ago   148MB
```

Now let's do the same for our nginx image:
```bash
$ cd nginx/
$ docker buildx build --platform linux/amd64 -t nginx_app:latest -f Dockerfile.nginx .
$ docker build . -t nginx_app -f Dockerfile.nginx
$ docker save nginx_app:latest | ssh -C root@<server-ip> docker load
```

### Push Docker Compose file to server
Now that we have our images on the server we need to push our `docker-compose.prod.yml` file.
```bash
$ scp docker-compose.prod.yml root@<server-ip>:/root/
```

Now that we have both our docker image and our docker compose file on the server we can start our app.
But let's first test to see a call to our api server, run this on your local machine;
```bash
$ curl http://<server-ip>/
curl: (7) Failed to connect to ...
$ curl https://<server-ip>/
curl: (7) Failed to connect to ...
```

Then to start our service, run on your server:
```bash
$ docker compose -f docker-compose.prod.yml up -d
```

Let's test again to see if our app is running, from our local machine:
```bash
$ curl https://<server-ip>/
curl: (60) SSL: no alternative certificate subject ...
$ curl http://<server-ip>/
<html>
<head><title>301 Moved Permanently</title></head>
<body>
```

Now our service is running on our server but we can't access it since we don't have ssl certificates setup.

### Add Firewall Rules
Now before we open up access to our unsecured api let's add some firewall rules to our server to ensure only we can access it.
To do this we will only allow http access from our ip address to the server (not if you use ipv4 it will likely be shared so make sure you trust the network, but prefer ipv6).

Got to [https://whatismyipaddress.com/](https://whatismyipaddress.com/) to get your ip address v6 (IPv6).
Then follow this guide to add a firewall rule to your server: [Digital Ocean Firewall](https://docs.digitalocean.com/products/networking/firewalls/how-to/configure-rules/)

The firewall rules should look something like this:

| Type   | Protocol | Port Range | Sources     |
|--------|----------|------------|-------------|
| HTTP   | TCP      | 80         | <your_IPv6> |
| HTTPS  | TCP      | 443        | <your_IPv6> |
| SSH    | TCP      | 21         | <your_IPv6> |


Then make sure to apply this to your droplet.
**Note:** This will help save you from someone calling your API a lot and giving you a large bandwidth bill.

### Test server
Now that we have our firewall rules setup we can test our server again.
But to not have to immediately setup ssl certificates we can temporary expose our service through http.

Go to your `nginx.conf` file and update the `https` redirect section to the following:
```nginx
server {
  listen 80 default_server;
  server_name _;

  location / {
      proxy_pass http://api-club;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

Then rebuild and push the nginx image to the server, on your local machine:
```bash
$ docker buildx build --platform linux/amd64 -t nginx_app:latest -f Dockerfile.nginx .
$ docker save nginx_app:latest | ssh -C root@<server-ip> docker load
```

Now, on your server we will see multiple nginx docker images.
We can restart with the latest by running docker compose up again.
After that we will want to prune (or remove) unused images to save server space.
```bash
$ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
nginx_app    latest    4e8bd24f61c2   2 minutes ago   11.8MB
<none>       <none>    c69662913f7d   10 minutes ago   11.8MB
api          latest    a0e8ccb47ec8   53 minutes ago   142MB
$ docker compose -f docker-compose.prod.yml up -d
[+] Running 2/2
 ✔ Container nginx       Started
 ✔ Container api_server  Running
 $ docker image prune -f
 $ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
nginx_app    latest    4e8bd24f61c2   2 minutes ago   11.8MB
api          latest    a0e8ccb47ec8   53 minutes ago   142MB
 ```

Note how above only our nginx container was restarted, this is because the api container didn't change.

Now let's test our server again, from our local machine:
```bash
$ curl http://<server-ip>/
{"status":"ok"}
```

And now our api is running on our server and we can access it through http.

Note: I would recommend reversing the changes to the nginx.conf file and in the next step we will configure a domain with ssl.


### Challenge
1. Test what happens to you make an api call when restarting the server.
2. Install `sqlite3` on your server and try to access the database.
