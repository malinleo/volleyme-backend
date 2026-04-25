# Server Setup Guide

## 1. Authenticate Docker with Selectel CR

Use your Selectel Container Registry credentials.

On the server:

```bash
docker login cr.selcloud.ru -u <token_name> -p <token_password>
```

Verify it works:

```bash
docker pull cr.selcloud.ru/volleyme-prod/backend:latest
```

## 2. Prepare deploy directory

```bash
export DEPLOY_PATH=/opt/volleyme-backend   # or wherever you prefer

sudo mkdir -p $DEPLOY_PATH/{nginx,certbot/conf,certbot/www,data/postgres,data/jwt}
sudo chown -R $USER:$USER $DEPLOY_PATH
```

Copy files from this repo's `.ci/` folder:

```bash
cp .ci/docker-compose.yml $DEPLOY_PATH/docker-compose.yml
cp .ci/nginx/nginx.conf   $DEPLOY_PATH/nginx/nginx.conf
```

## 3. SSL certificates (Let's Encrypt + Certbot)

Nginx must be running on port 80 for the HTTP-01 challenge.
The first time, certs don't exist yet so nginx will fail to start.
Use a temporary self-signed cert to bootstrap:

```bash
cd $DEPLOY_PATH

# Create a dummy cert so nginx can start
mkdir -p certbot/conf/live/volleyme.ru
openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
  -keyout certbot/conf/live/volleyme.ru/privkey.pem \
  -out certbot/conf/live/volleyme.ru/fullchain.pem \
  -subj "/CN=localhost"

# Start nginx (it will use the dummy cert)
docker compose up -d nginx

# Issue the real cert via HTTP-01 challenge
# Remove dummy cert and issue real one
rm -rf certbot/conf/live/volleyme.ru certbot/conf/archive/volleyme.ru certbot/conf/renewal/volleyme.ru.conf

docker compose --profile certbot run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  -d volleyme.ru \
  -d www.volleyme.ru \
  --email nearpin@mail.ru \
  --agree-tos \
  --no-eff-email

# Reload nginx to pick up the real cert
docker compose exec nginx nginx -s reload
```

### Auto-renewal (cron)

HTTP-01 renewal is fully automatic — no manual DNS records needed.
Add to crontab (`crontab -e`):

```
0 3 1,15 * * cd /opt/volleyme-backend && docker compose --profile certbot run --rm certbot renew && docker compose exec nginx nginx -s reload
```

This checks for renewal twice a month. Certbot only renews if the cert expires within 30 days.

## 4. Environment file

```bash
cp .ci/.env.sample $DEPLOY_PATH/.env
nano $DEPLOY_PATH/.env   # fill in real values, especially DB_PASSWORD
```

## 5. First launch

```bash
cd $DEPLOY_PATH

# Start postgres first
docker compose up -d postgres

# Generate JWT key pair
docker compose --profile setup run --rm volleyme-prepare

# Run migrations
docker compose --profile migrate run --rm volleyme-migrate

# Start everything
docker compose up -d
```

## 6. GitHub Actions secrets

Set these in the repo settings → Secrets and variables → Actions:

| Secret                | Value                            |
|-----------------------|----------------------------------|
| SERVER_HOST           | Your server IP                   |
| SERVER_USER           | SSH username (e.g. deploy)       |
| SERVER_SSH_KEY        | Private SSH key (ed25519)        |
| DEPLOY_PATH           | e.g. /opt/volleyme-backend       |
| SELECTEL_CR_USER      | Selectel CR token name           |
| SELECTEL_CR_PASSWORD  | Selectel CR token password       |

## 7. Verify

```bash
# Check all services are running
docker compose ps

# Check logs
docker compose logs --tail 20

# Test HTTPS
curl -k https://localhost/healthz
```
