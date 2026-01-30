# Backend Deployment Guide

## Railway Deployment

1. Create a new Railway project
2. Connect your GitHub repository
3. Add environment variables:
   - All variables from `.env.example`
4. Set start command: `python main.py start`
5. For token server, create a second service:
   - Set start command: `python token_server.py`
   - Expose port 8080

## Render Deployment

1. Create a new Web Service
2. Connect your GitHub repository
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py start`
4. Add environment variables
5. Create a second service for token server:
   - Start Command: `python token_server.py`
   - Port: 8080

## Fly.io Deployment

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Create app: `flyctl apps create superbryn-backend`
4. Set secrets:
```bash
flyctl secrets set LIVEKIT_URL=...
flyctl secrets set LIVEKIT_API_KEY=...
# ... etc
```
5. Deploy: `flyctl deploy`

## Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "start"]
```

Build and run:
```bash
docker build -t superbryn-backend .
docker run -p 8080:8080 --env-file .env superbryn-backend
```
