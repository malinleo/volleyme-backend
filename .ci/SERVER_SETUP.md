# Server Setup Guide (Google Cloud)

How it works:

```
git push ──► GitHub Actions
              ├─ job "build":  OIDC token ──► Workload Identity Federation ──► GCP access token
              │                docker build (.ci/Dockerfile) ──► push to Artifact Registry
              └─ job "deploy": SSH into VM ──► docker compose pull / migrate / up -d --wait
VM (volleyme-dev1) ──► pulls images from Artifact Registry using its own service account
```

Values used below:

```bash
PROJECT_ID=agile-fort-310814
PROJECT_NUMBER=459921666432
REGION=europe-north2                     # Artifact Registry location
ZONE=europe-north2-a                     # VM zone
VM=volleyme-dev1
REPO=volleyme                            # Artifact Registry docker repo
GH_REPO=malinleo/volleyme-backend
DEPLOY_SA=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com
VM_SA=${PROJECT_NUMBER}-compute@developer.gserviceaccount.com
DEPLOY_PATH=/opt/volleyme
DOMAIN=volleyme.xyz
```

Image: `europe-north2-docker.pkg.dev/agile-fort-310814/volleyme/backend:<tag>`

## 1. GCP: let GitHub Actions push images (run locally)

```bash
gcloud services enable artifactregistry.googleapis.com iamcredentials.googleapis.com sts.googleapis.com

# Service account that GitHub Actions will impersonate
gcloud iam service-accounts create github-deployer --display-name="GitHub Actions deployer"

# It may only push to this one repository
gcloud artifacts repositories add-iam-policy-binding $REPO --location=$REGION \
  --member="serviceAccount:$DEPLOY_SA" --role=roles/artifactregistry.writer

# Workload Identity Pool + OIDC provider that trusts GitHub tokens of THIS repo only
gcloud iam workload-identity-pools create github --location=global --display-name="GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc volleyme-backend \
  --location=global --workload-identity-pool=github \
  --display-name="volleyme-backend repo" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository == '${GH_REPO}'"

# Allow identities from that repo to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding $DEPLOY_SA \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/${GH_REPO}"
```

## 2. GCP: let the VM pull images (run locally)

```bash
gcloud artifacts repositories add-iam-policy-binding $REPO --location=$REGION \
  --member="serviceAccount:$VM_SA" --role=roles/artifactregistry.reader
```

The VM's default access scopes (`devstorage.read_only`) are enough for pulling.

Optional: auto-delete old images, keep the 10 most recent:

```bash
cat > /tmp/gar-cleanup.json <<'EOF'
[
  {"name": "keep-recent", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 10}},
  {"name": "delete-old",  "action": {"type": "Delete"}, "condition": {"olderThan": "30d"}}
]
EOF
gcloud artifacts repositories set-cleanup-policies $REPO --location=$REGION --policy=/tmp/gar-cleanup.json --no-dry-run
```

## 3. VM: install Docker

```bash
gcloud compute ssh $VM --zone $ZONE
```

On the VM (Debian 13):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## 4. VM: deploy user for GitHub Actions

Locally, generate a dedicated key pair (no passphrase):

```bash
ssh-keygen -t ed25519 -N '' -C github-actions-deploy -f ~/.ssh/volleyme_deploy
```

On the VM:

```bash
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG docker deploy
sudo -u deploy mkdir -m 700 /home/deploy/.ssh
echo "<contents of ~/.ssh/volleyme_deploy.pub>" | sudo -u deploy tee /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys

# Docker credential helper for Artifact Registry (uses the VM service account via metadata server)
sudo -u deploy gcloud auth configure-docker europe-north2-docker.pkg.dev --quiet
```

Check from your machine: `ssh -i ~/.ssh/volleyme_deploy deploy@34.51.136.155 docker ps`

## 5. VM: deploy directory

On the VM:

```bash
sudo mkdir -p /opt/volleyme/{nginx,certbot/conf,certbot/www,data/postgres,data/jwt}
sudo chown -R deploy:deploy /opt/volleyme
```

Copy files from this repo's `.ci/` folder (run locally from the repo root):

```bash
gcloud compute scp --zone $ZONE .ci/docker-compose.yml .ci/nginx/nginx.conf .ci/ssh_banner .ci/cleanup-images.sh $VM:/tmp/
```

On the VM:

```bash
sudo -u deploy cp /tmp/docker-compose.yml /opt/volleyme/docker-compose.yml
sudo -u deploy cp /tmp/nginx.conf         /opt/volleyme/nginx/nginx.conf
sudo -u deploy mkdir -p /opt/volleyme/.ci
sudo -u deploy install -m 755 /tmp/cleanup-images.sh /opt/volleyme/.ci/cleanup-images.sh
sudo cp /tmp/ssh_banner /etc/motd
```

> These files are NOT synced by CI. When you change `.ci/docker-compose.yml` or `nginx.conf`, copy them again.

## 6. Environment file

```bash
sudo -u deploy nano /opt/volleyme/.env
```

Start from `.sample.env` in the repo root. For production set at least:

```
DEBUG=false
DB_HOST=postgres
DB_PASSWORD=<strong random password>   # e.g. openssl rand -hex 24
```

## 7. Temporary self-signed certificate

nginx won't start without a certificate, and it can't get a real one before it is
running (HTTP-01 challenge on port 80). So the first deploy runs with a dummy cert,
the real one is issued in step 11. As `deploy` (`sudo -iu deploy`):

```bash
cd /opt/volleyme
mkdir -p certbot/conf/live/volleyme.xyz
openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
  -keyout certbot/conf/live/volleyme.xyz/privkey.pem \
  -out certbot/conf/live/volleyme.xyz/fullchain.pem \
  -subj "/CN=localhost"
```

## 8. JWT key pair

As `deploy`, before the first deploy (same as `bash/create_jwt_key_pair.sh`):

```bash
cd /opt/volleyme
ssh-keygen -t rsa -b 4096 -m PEM -N '' -f data/jwt/jwtRS256.key
openssl rsa -in data/jwt/jwtRS256.key -pubout -outform PEM -out data/jwt/jwtRS256.key.pub
```

Once an image exists in the registry you can use `docker compose --profile setup run --rm volleyme-prepare` instead.

## 9. GitHub Actions variables and secrets

Repo → Settings → Secrets and variables → Actions (or via `gh`):

| Kind     | Name             | Value                                                                                         |
|----------|------------------|-----------------------------------------------------------------------------------------------|
| Variable | GCP_WIF_PROVIDER | `projects/459921666432/locations/global/workloadIdentityPools/github/providers/volleyme-backend` |
| Variable | GCP_DEPLOY_SA    | `github-deployer@agile-fort-310814.iam.gserviceaccount.com`                                   |
| Secret   | SERVER_HOST      | `34.51.136.155`                                                                               |
| Secret   | SERVER_USER      | `deploy`                                                                                      |
| Secret   | SERVER_SSH_KEY   | contents of `~/.ssh/volleyme_deploy` (private key)                                            |

```bash
gh variable set GCP_WIF_PROVIDER --body "projects/459921666432/locations/global/workloadIdentityPools/github/providers/volleyme-backend"
gh variable set GCP_DEPLOY_SA    --body "github-deployer@agile-fort-310814.iam.gserviceaccount.com"
gh secret set SERVER_HOST    --body "34.51.136.155"
gh secret set SERVER_USER    --body "deploy"
gh secret set SERVER_SSH_KEY < ~/.ssh/volleyme_deploy
```

Old Selectel secrets (`SELECTEL_CR_*`) can be deleted.

## 10. First deploy

Push to `main` (or a `feature/ci*` branch). The workflow builds and pushes the
image, then on the VM runs `pull` → migrations → `up -d --wait`.
Postgres is started automatically through `depends_on`.

## 11. Real SSL certificate (Let's Encrypt + Certbot)

After the first deploy nginx is running with the dummy cert. As your own user (`malinleo`, has passwordless sudo), from `/opt/volleyme`; prefix `docker compose` with `sudo -u deploy` or run it as `deploy`:

```bash
cd /opt/volleyme

# certbot runs as root, so its files are root-owned: sudo is required
sudo rm -rf certbot/conf/live/volleyme.xyz certbot/conf/archive/volleyme.xyz certbot/conf/renewal/volleyme.xyz.conf

docker compose --profile certbot run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --cert-name volleyme.xyz \
  -d volleyme.xyz \
  -d www.volleyme.xyz \
  --email nearpin@mail.ru \
  --agree-tos \
  --no-eff-email

docker compose exec nginx nginx -s reload
```

### Cron (`crontab -e` as `deploy`)

```
0 3 1,15 * * cd /opt/volleyme && docker compose --profile certbot run --rm certbot renew && docker compose exec nginx nginx -s reload
0 4 * * *    /opt/volleyme/.ci/cleanup-images.sh >> /opt/volleyme/docker-cleanup.log 2>&1
```

Certbot only renews when the cert expires within 30 days.

## 12. Verify

```bash
cd /opt/volleyme
docker compose ps
docker compose logs --tail 20
curl https://volleyme.xyz/healthz/
```
