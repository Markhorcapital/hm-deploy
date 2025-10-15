# Using Custom Hummingbot Image - Quick Reference

This guide helps you use your custom Hummingbot Docker image (e.g., with crypto.com connector) with hm-deploy and HM-API.

## Quick Setup (Step-by-Step)

### Step 1: Build Your Custom Hummingbot Image

Make sure Docker Desktop is running, then:

```bash
cd /Users/zia/Downloads/Markhor/markhorHB/hummingbot
docker build -t hummingbot-custom:local .
```

**Wait for the build to complete** - this may take several minutes.

### Step 2: Setup hm-deploy

```bash
cd /Users/zia/Downloads/Markhor/markhorHB/hm-deploy
bash setup.sh
```

This will:
- Create a `.env` file with `HUMMINGBOT_IMAGE=hummingbot-custom:local`
- Pull dashboard and API images (but NOT the default hummingbot image)
- Start all services using docker-compose

### Step 3: Verify the Configuration

Check that your `.env` file contains the custom image setting:

```bash
cat /Users/zia/Downloads/Markhor/markhorHB/hm-deploy/.env | grep HUMMINGBOT_IMAGE
```

You should see:
```
HUMMINGBOT_IMAGE=hummingbot-custom:local
```

### Step 4: Access the Dashboard

Open your browser and go to:
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## What Changed?

### Modified Files

1. **hm-deploy/setup.sh**
   - Adds `HUMMINGBOT_IMAGE=hummingbot-custom:local` to the `.env` file
   - Skips pulling `hummingbot/hummingbot:latest` from Docker Hub

2. **HM-API/setup.sh**
   - Adds `HUMMINGBOT_IMAGE=hummingbot-custom:local` to the `.env` file
   - Skips pulling the default hummingbot image

3. **hm-deploy/README.md**
   - Added section explaining custom image usage

## How It Works

When you deploy a bot through the dashboard:

1. The dashboard sends a request to HM-API
2. HM-API reads the `HUMMINGBOT_IMAGE` environment variable from `.env`
3. HM-API creates a new Docker container using your custom image (`hummingbot-custom:local`)
4. Your bot runs with the crypto.com connector available

## Updating Your Custom Image

If you make changes to your hummingbot code, rebuild the image:

```bash
cd /Users/zia/Downloads/Markhor/markhorHB/hummingbot
docker build -t hummingbot-custom:local .
```

**Note**: You'll need to stop and restart any running bots for them to use the new image.

## Troubleshooting

### Issue: Bot fails to start with "image not found"

**Solution**: Make sure you've built the image:
```bash
docker images | grep hummingbot-custom
```

You should see `hummingbot-custom:local` in the list. If not, run the build command from Step 1.

### Issue: Bot is using the old image

**Solution**: 
1. Stop and remove the bot container
2. Rebuild your custom image with the same tag
3. Redeploy the bot from the dashboard

### Issue: Want to switch back to the default image

**Solution**: Edit the `.env` file and change:
```bash
HUMMINGBOT_IMAGE=hummingbot/hummingbot:latest
```

Then restart the services:
```bash
docker compose restart
```

## Verifying Your Setup

### Check if the custom image exists:
```bash
docker images | grep hummingbot-custom
```

### Check the environment variable:
```bash
cd /Users/zia/Downloads/Markhor/markhorHB/hm-deploy
cat .env | grep HUMMINGBOT_IMAGE
```

### Check running services:
```bash
docker compose ps
```

### Check if a bot is using your custom image:
```bash
docker ps --format "{{.Names}}\t{{.Image}}" | grep hummingbot
```

You should see containers with `hummingbot-custom:local` as the image.

## Additional Notes

- The custom image tag (`hummingbot-custom:local`) is hardcoded in the setup scripts
- If you want to use a different tag, edit both `setup.sh` files before running them
- The image is stored locally and won't be pushed to Docker Hub unless you explicitly do so
- Each time you rebuild with the same tag, Docker will replace the old image

## Need Help?

- Check HM-API logs: `docker compose -f /Users/zia/Downloads/Markhor/markhorHB/hm-deploy/docker-compose.yml logs hummingbot-api`
- Check bot logs: `docker logs <bot-container-name>`
- Verify Docker is running: `docker info`

