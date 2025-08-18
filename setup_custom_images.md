# 🚀 Custom Images Setup Guide

This guide shows how to build and deploy custom Hummingbot images instead of using the default Docker Hub images.

## 📋 Prerequisites

- Docker installed and running
- `hummingbot/`, `hummingbot-api/`, and `deploy/` directories available

## 🏗️ Build Custom Images

```bash
# Build custom Hummingbot image
cd hummingbot
docker build -t hummingbot/hummingbot:custom .

# Build custom Hummingbot API image
cd ../hummingbot-api
docker build -t hummingbot/hummingbot-api:custom .

# Verify images were built
docker images | grep hummingbot
```

## 🚀 Deploy

```bash
# Navigate to deploy directory
cd ../deploy

# Run setup (docker-compose.yml is already configured for custom images)
bash setup.sh
```

## ✅ Verify

```bash
# Check running containers
docker ps --format "table {{.Names}}\t{{.Image}}"

# Check bot image environment variable
docker exec hummingbot-api env | grep HUMMINGBOT_IMAGE

# Expected: HUMMINGBOT_IMAGE=hummingbot/hummingbot:custom
```

## 🎯 Test

1. Open dashboard: http://localhost:8501
2. Go to "Launch Bot V2" page  
3. Verify `hummingbot/hummingbot:custom` appears in dropdown
4. Create a bot to test custom image usage

## 📊 Complete Commands

```bash
# Build, deploy, and verify
cd hummingbot && docker build -t hummingbot/hummingbot:custom .
cd ../hummingbot-api && docker build -t hummingbot/hummingbot-api:custom .
cd ../deploy && bash setup.sh
docker ps --format "table {{.Names}}\t{{.Image}}"
```

