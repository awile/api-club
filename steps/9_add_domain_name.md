# Add Domain Name

### Table of Contents
1. [Get a domain name](#get-a-domain-name)
2. [Point domain to server](#point-domain-to-server)
3. [Get SSL Certificates](#get-ssl-certificates)
4. [Setup SSL](#setup-ssl)
5. [Challenge](#challenge)


### Get a domain name
This can be any domain name you want from anywhere you want, but I try to find ones in the $1-2/year range.
I will be using the domain `badapi.club` for this step.

I bought this domain from [Namecheap](https://www.namecheap.com/), but I'm sure there are better places. Also, that is not an affiliate link, so use whatever you want!

### Point domain to server
Now that we have a domain name, we need to configure DNS to point to our server.
DNS is what converts our domain name to the IP address for our server.
So `https://badapi.club/task` will point to `https://<server-ip>/task`.

To do this we will need to create a set of DNS records that point our domain to our server.
Whoever you bought your domain from will likely provide a way to set DNS records with a guide.
And we could use this to point it directly at our server IP address, but since we are using Digital Ocean, we can use their DNS service.

That means we can set this up in two steps:
- Point our domain to Digital Ocean's nameservers
- Have Digital Ocean point our domain to our server's ip address

This will let us manage our DNS records from Digital Ocean's dashboard, which is nice.

For pointing namecheap to digital ocean we can follow this guide [here](https://www.namecheap.com/support/knowledgebase/article.aspx/10375/2208/how-do-i-link-a-domain-to-my-digitalocean-account/).
But all you do is tell you domain registar to point your domain to Digital Ocean's nameservers:
- ns1.digitalocean.com
- ns2.digitalocean.com
- ns3.digitalocean.com

*Note this could take up to 48 hours to take effect, but is usually is usually much faster.*

Then we can add a new domain to Digital Ocean's DNS service and point it to our server's ip address.
Digital Ocean has a guide for this [here](https://www.digitalocean.com/docs/networking/dns/how-to/add-domains/).

All we are doing is pointing our domain to our server's ip address by clicking our droplet's name in the dropdown.
We want to create two records:
- Create an *A record* with the name `@` and the value of our server's ip address

    This will route `https://badapi.club` to our server
- Create a *CNAME record* with the name `api` and the value of `@`

    This will route `https://api.badapi.club` to `https://badapi.club` then to our server's ip address from the previous record


Once this is setup and DNS propagates we can test our domain name by running:
```bash
$ curl http://badapi.club/
{"status":"ok"}
```

### Get SSL Certificates
We can now access our service through our domain name, but we are still using http.
To use https and have encrypted traffic we need to setup SSL certificates and to get those we need to verify we own the domain to a Certificate Authority.

Some Certificate Authorities charge money, but we can use [Let's Encrypt](https://letsencrypt.org/) to get free certificates. All we have to do is demonstrate to them that we own the domain.

Again Digital Ocean has a guide for this [ubuntu let's encrypt guide](https://www.digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-let-s-encrypt-ssl-certificates-on-ubuntu-20-04).

First, we need to install `snap` on our server, which will let us download and run applications like certbot.
Remember, we will need to refresh this certificate every 60-90 days, but we can automate this process with certbot.
```bash
$ sudo snap install core; sudo snap refresh core
$ sudo snap install --classic certbot
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Certbot is now installed and easily runnable, but to get our certificate we need our server to talk to Let's Encrypt.
And for that we need to relax our firewall rules and allow http/https traffic to ports 80/443 from all ip addresses.
| Type   | Protocol | Port Range | Sources            |
|--------|----------|------------|--------------------|
| HTTP   | TCP      | 80         | All IPv4, All IPv6 |
| HTTPS  | TCP      | 443        | All IPv4, All IPv6 |
| SSH    | TCP      | 21         | <your_IPv6>        |

Then we need to stop our application & and we can run certbot.
```bash
$ docker compose -f docker-compose.prod.yml stop
$ sudo certbot certonly --standalone -d badapi.club
Requesting a certificate for badapi.club

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/badapi.club/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/badapi.club/privkey.pem
```

If successful you will see that you have a certificate and key saved in the `/etc/letsencrypt/live/badapi.club/` directory.
- `fullchain.pem` is the certificate
- `privkey.pem` is the private key for the certificate


### Setup SSL
Now that we have our SSL certificate we can add them to our nginx configuration to allow https traffic.
Back in our nginx code we have an issue those we need to build our nginx image but the ceritifcates only exist on the server.

To handle this we can leverage docker volumes to access the ceritifcates on the server.
Open and update the `docker-compose.prod.yml` file to include a volume for the certificates
Note that we have to give docker access to the full `/etc/letsencrypt/` directory to access the certificates.
This is because the live certificates are designed using a symlink to the latest certificate, which doesn't place nice with docker.
```Dockefile
...
nginx:
      container_name: nginx
      image: nginx_app
      ports:
        - "443:443"
        - "80:80"
      volumes:
        - /etc/letsencrypt/:/etc/letsencrypt/
      networks:
        - api
...
```

Then we can remove our local certificates from the `Dockefile.nginx`:
```Dockerfile
FROM nginx:mainline-alpine-slim

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
```
and update the `nginx.conf` to use the certificates from the volume and the correct server name.
```nginx
server {
  listen 443 ssl;
  server_name badapi.club;

  ssl_certificate /etc/letsencrypt/live/badapi.club/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/badapi.club/privkey.pem;
  ...
}
```

Now we can rebuild and rerelease our nginx image from our local machine.
```bash
$ docker buildx build --platform linux/amd64 -t nginx_app:latest -f Dockerfile.nginx .
$ docker save nginx_app:latest | ssh -C root@badapi.club docker load
```

We will also need to copy the latest `docker-compose.prod.yml` file to the server.
```bash
$ scp docker-compose.prod.yml root@badapi.club:/root/
```

Then we can start our services on the server.
```bash
$ docker compose -f docker-compose.prod.yml up -d
```

Now we can test our service with https.
```bash
$ curl https://badapi.club/
{"status":"ok"}
```

It works! Our api is live and accessible through our domain name with https.

### Challenge
1. Can you automate your ceritifcate renewal with certbot?
2. Can you serve an html webpage instead of json?
