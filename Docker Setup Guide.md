# 🐳 Docker Deployment

## Quick Start with Docker

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- SerpAPI key ([Sign up](https://serpapi.com))

---

## Option 1: Docker Compose (Recommended)

**Step 1: Clone and configure**
```bash
git clone https://github.com/yourusername/TrendArbitrage.git
cd TrendArbitrage

# Create .env file with your API key
echo "SERPAPI_KEY=your_serpapi_key_here" > .env
```

**Step 2: Build and run**
```bash
docker-compose up -d
```

**Step 3: Access dashboard**
```
http://localhost:8501
```

**Management commands:**
```bash
# View logs
docker-compose logs -f

# Stop container
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run CLI command
docker-compose exec trendarbitrage python main.py --keywords "yoga mat"
```

---

## Option 2: Docker CLI

**Build image:**
```bash
docker build -t trendarbitrage:latest .
```

**Run web dashboard:**
```bash
docker run -d \
  --name trendarbitrage \
  -p 8501:8501 \
  -e SERPAPI_KEY=your_key_here \
  -v $(pwd)/data/output:/app/data/output \
  -v $(pwd)/data/frontend:/app/data/frontend \
  -v $(pwd)/logs:/app/logs \
  trendarbitrage:latest
```

**Run CLI command:**
```bash
docker run --rm \
  -e SERPAPI_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  trendarbitrage:latest \
  python main.py --keywords "phone case,yoga mat"
```

---

## Data Persistence

**Volumes mounted by default:**
- `./data/output` → CSV reports
- `./data/frontend` → JSON files for frontend
- `./logs` → Application logs
- `./config` → Configuration files

**Access reports:**
```bash
# Reports are saved on your host machine
ls data/output/
cat data/output/report.csv
```

---

## Configuration

**Customize `config/config.yaml`:**
```yaml
trends:
  geo: "MX"  # Change country code
  timeframe: "today 6-m"  # Shorter analysis period

scraping:
  delay_between_requests: 5  # Slower requests (avoid rate limits)
  
scoring:
  min_interest_score: 30  # Higher quality filter
```

**Apply changes:**
```bash
docker-compose restart
```

---

## Troubleshooting

**Container won't start:**
```bash
# Check logs
docker-compose logs trendarbitrage

# Common issue: Missing SERPAPI_KEY
# Solution: Ensure .env file exists with valid key
```

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead
```

**Out of SerpAPI credits:**
```bash
# Check your usage at https://serpapi.com/dashboard
# Free tier = 100 searches/month
```

---

## Production Deployment

**Deploy to cloud platforms:**

### Render.com
1. Create account at [render.com](https://render.com)
2. New Web Service → Connect GitHub repo
3. Set environment variable: `SERPAPI_KEY`
4. Deploy (automatic from Dockerfile)

### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### DigitalOcean App Platform
1. Upload repository to GitHub
2. Create new App → Docker source
3. Add environment variable: `SERPAPI_KEY`
4. Deploy

---

## Advanced Usage

**Run with custom config:**
```bash
docker run --rm \
  -e SERPAPI_KEY=your_key \
  -v $(pwd)/custom-config.yaml:/app/config/config.yaml \
  trendarbitrage:latest \
  python main.py --config /app/config/config.yaml
```

**Run temporal analysis:**
```bash
docker-compose exec trendarbitrage \
  python main.py --keywords "bluetooth headphones" --temporal
```

**Export to host:**
```bash
# Results automatically saved to ./data/output/
# No need to copy from container
```

---

## Resource Limits

**Limit CPU and memory:**
```yaml
# docker-compose.yml
services:
  trendarbitrage:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

**For production:**
- 512MB RAM minimum
- 1 CPU core recommended
- 1GB disk space for logs/data