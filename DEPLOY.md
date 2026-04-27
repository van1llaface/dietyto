# Deploying Dietyto

## What was created

```
├── backend/
│   ├── Dockerfile          ← Python + FastAPI container
│   └── requirements.txt    ← Updated with all dependencies
├── frontend/
│   ├── Dockerfile          ← Nginx container serving HTML
│   └── nginx.conf          ← Proxies /api/* → backend:8000
├── docker-compose.yml      ← Orchestrates both containers
└── .dockerignore
```

## How it works

- **Frontend container** (nginx): serves `index.html` on port 80 and proxies any `/api/*` request to the backend
- **Backend container** (uvicorn): runs FastAPI on port 8000 (internal only)
- The frontend auto-detects: on `localhost` it calls `http://localhost:8000` directly, in production it uses `/api/`

---

## Option A: Deploy to a VPS (DigitalOcean, Hetzner, Linode, etc.)

### 1. Get a server
- Any Linux VPS with Docker installed (~$5/mo)
- Example: DigitalOcean → Create Droplet → Ubuntu 24.04 → Docker from Marketplace

### 2. Clone and run
```bash
ssh root@YOUR_SERVER_IP

git clone https://github.com/YOUR_USERNAME/lngvt.git
cd lngvt
docker compose up -d --build
```

### 3. Done
- Your app is live at `http://YOUR_SERVER_IP`
- To add HTTPS, put Cloudflare in front (free) or add Caddy/Certbot

### 4. Update later
```bash
cd lngvt
git pull
docker compose up -d --build
```

---

## Option B: Deploy to Render (free tier)

### Backend
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Note the URL (e.g. `https://dietyto-api.onrender.com`)

### Frontend
1. Render → New → Static Site
2. Connect same repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Publish Directory**: `.`
4. Add environment variable or update `index.html` API URL to point to your backend URL

---

## Option C: Deploy to Railway

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. It auto-detects the `docker-compose.yml`
3. Add a custom domain in settings
4. Done — Railway handles HTTPS automatically

---

## Adding HTTPS (for VPS)

Easiest: Put Cloudflare in front (free):
1. Buy a domain (~$10/year on Namecheap/Cloudflare)
2. Point DNS to your server IP via Cloudflare
3. Cloudflare handles SSL automatically

Alternative: Replace nginx with Caddy (auto HTTPS):
```yaml
# Replace frontend service in docker-compose.yml with:
  caddy:
    image: caddy:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./frontend:/srv
      - caddy_data:/data
```
