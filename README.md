# hummingbot-deploy

Welcome to the Hummingbot Deploy project. This guide will walk you through the steps to deploy multiple trading bots using a centralized dashboard powered by the Hummingbot API and comprehensive backend services.

## Prerequisites

- Docker must be installed on your machine. If you do not have Docker installed, you can download and install it from [Docker's official site](https://www.docker.com/products/docker-desktop).
- If you are on Windows, you'll need to setup WSL2 and a Linux terminal like Ubuntu. Make sure to run the commands below in a Linux terminal and not in the Windows command prompt or Powershell.

## Architecture

This deployment includes:

- **Dashboard** (port 8501): Streamlit-based web UI for bot management and monitoring
- **Hummingbot API** (port 8000): FastAPI backend service for bot operations and data management
- **PostgreSQL Database** (port 5432): Persistent storage for bot configurations and performance data
- **EMQX Broker** (port 1883): MQTT broker for real-time bot communication and telemetry

All services are orchestrated using Docker Compose for seamless deployment and management.

## Using Custom Hummingbot Image

If you have modified the Hummingbot source code, you need to build a local Docker image and configure the deployment to use it:

### 1. Build Your Custom Hummingbot Image

Navigate to your hummingbot directory and build the Docker image:

```bash
cd /path/to/your/hummingbot
docker build -t hummingbot-custom:local .
```

This creates a local Docker image tagged as `hummingbot-custom:local` with your modifications.

### 2. Run the Setup Script

The setup script has been configured to automatically use `hummingbot-custom:local` instead of pulling from Docker Hub:

```bash
cd /path/to/hm-deploy
bash setup.sh
```

The script will:
- Create a `.env` file with `HUMMINGBOT_IMAGE=hummingbot-custom:local`
- Skip pulling the default hummingbot image from Docker Hub
- Use your local image when deploying bots

### 3. Verify the Configuration

After running setup, check that the `.env` file contains:

```bash
HUMMINGBOT_IMAGE=hummingbot-custom:local
```

Now when you deploy bots through the dashboard, they will use your custom image with the crypto.com connector.

**Note:** If you make changes to your hummingbot code, rebuild the image with the same tag:

```bash
cd /path/to/your/hummingbot
docker build -t hummingbot-custom:local .
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hummingbot/deploy.git
   cd deploy
   ```

## Running the Application

1. **Start and configure the Application**
   - Run the following command to download and start the app.
   - ```bash
     bash setup.sh
     ```
2. **Access the services:**
   - **Dashboard**: Open your web browser and go to `localhost:8501`. Replace `localhost` with the IP of your server if using a cloud server.
   - **API Documentation**: Access the Hummingbot API docs at `localhost:8000/docs`
   - **EMQX Dashboard**: Monitor MQTT broker at `localhost:18083` (admin/public)

3. **API Keys and Credentials:**
   - Go to the credentials page
   - You add credentials to the master account by picking the exchange and adding the API key and secret. This will encrypt the keys and store them in the master account folder.
   - If you are managing multiple accounts you can create a new one and start adding new credentials there.

4. **Create a config for PMM Simple**
   - Go to the tab PMM Simple and create a new configuration. Soon will be released a video explaining how the strategy works.

5. **Deploy the configuration**
   - Go to the Deploy tab, select a name for your bot and the configuration you just created.
   - The system will automatically use the configured Docker image (either `hummingbot-custom:local` if you built a custom image, or the default `hummingbot/hummingbot:latest`).
   - Press the button to create a new instance.

6. **Check the status of the bot**
   - Go to the Instances tab and check the status of the bot.
     - If it's not available is because the bot is starting, wait a few seconds and refresh the page.
     - If it's running, you can check the performance of it in the graph, refresh to see the latest data.
     - If it's stopped, probably the bot had an error, you can check the logs in the container to understand what happened.

7. **[Optional] Monitor Services**
   - **Hummingbot API**: Access full API documentation at `localhost:8000/docs`
   - **Database**: PostgreSQL running on `localhost:5432` (hbot/hummingbot-api)
   - **MQTT Broker**: EMQX dashboard at `localhost:18083` for real-time bot communication monitoring

## Authentication

Authentication is disabled by default. To enable Dashboard Authentication please follow the steps below: 

**Set Credentials (Optional):**

The dashboard uses `admin` and `abc` as the default username and password respectively. It's strongly recommended to change these credentials for enhanced security.:

- Navigate to the `deploy` folder and open the `credentials.yml` file.
- Add or modify the current username / password and save the changes afterward
  
  ```
  credentials:
    usernames:
      admin:
        email: admin@gmail.com
        name: John Doe
        logged_in: False
        password: abc
  cookie:
    expiry_days: 0
    key: some_signature_key # Must be string
    name: some_cookie_name
  pre-authorized:
    emails:
    - admin@admin.com
  ```  
### Enable Authentication

- Ensure the dashboard container is not running.
- Open the `docker-compose.yml` file within the `deploy` folder using a text editor.
- Locate the environment variable `AUTH_SYSTEM_ENABLED` under the dashboard service configuration.
  
  ```
  services:
  dashboard:
    container_name: dashboard
    image: hummingbot/dashboard:latest
    ports:
      - "8501:8501"
    environment:
        - AUTH_SYSTEM_ENABLED=True
        - BACKEND_API_HOST=hummingbot-api
        - BACKEND_API_PORT=8000
  ```
- Change the value of `AUTH_SYSTEM_ENABLED` from `False` to `True`.
- Save the changes to the `docker-compose.yml` file.
- Relaunch Dashboard by running `bash setup.sh`
  
### Known Issues
- Refreshing the browser window may log you out and display the login screen again. This is a known issue that might be addressed in future updates.


## Dashboard Functionalities

- **Config Generator:**
  - Create and select configurations for different v2 strategies.
  - Backtest and deploy the selected configurations.

- **Bot Management:**
  - Visualize bot performance in real-time.
  - Stop and archive running bots.

## Tutorial

To get started with deploying your first bot, follow these step-by-step instructions:

1. **Prepare your bot configurations:**
   - Select a controller and backtest your controller configs.

2. **Deploy a bot:**
   - Use the dashboard UI to select and deploy your configurations.

3. **Monitor and Manage:**
   - Track bot performance and make adjustments as needed through the dashboard.
