# django-fastapi

# Project Setup and Usage Guide

## Prerequisites

### Install `make` on Linux / macOS

#### Linux (Debian/Ubuntu-based):
```bash
sudo apt update && sudo apt install -y make
```

#### macOS (Using Homebrew):
```bash
brew install make
```

### Install Docker and Docker Compose

#### Linux (Debian/Ubuntu-based):
```bash
sudo apt update && sudo apt install -y docker.io docker-compose
```

#### macOS (Using Homebrew):
```bash
brew install docker docker-compose
```

Ensure that the Docker daemon is running before proceeding.

---

## Project Setup (Local)

### 1. Create `.env` File
Create a `.env` file in the root directory near `docker-compose.local.yml` and add the following environment variables:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=k1core
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin
```

### 2. Create Backend Configuration File
Create a `.env` file in the `backend` directory (near `Makefile`) with the following configuration: </br>
Generate a secret key for `AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY` using the following command:
```bash
python3 -c "import secrets; print(f'AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY={secrets.token_hex(32)}')"
```
```env
DEBUG=False
STATE=prod
SECRET_KEY=<DJANGO_SECRET_EKY>
DATABASE__URI=postgres://admin:admin@localhost:5432/k1core
BROKER__URI=amqp://admin:admin@localhost/
AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY=<AUTHENTICATION__ACCESS_TOKEN__SECRET_KEY>
```

### 3. Create Workers Configuration
Create a `.env` file for each worker (Blockchair and CoinMarketCap) near their respective `Makefile`:

```env
BROKER_URI=amqp://admin:admin@localhost:5672
TIMEOUT=5
# Optional Proxy
# PROXY=<PROXY>
```

---

## Running the Project Locally

### 1. Start Required Services
Run the following command to start the required services (PostgreSQL, RabbitMQ, etc.):
```bash
docker compose -f docker-compose.local.yml up -d
```

### 2. Setup Project Components
Run the following command to set up all required dependencies:
```bash
make setup-local
make start-local
```

### 3. Start Backend Locally
```bash
make start-local
```

### 4. Start Workers
For each worker (Blockchair and CoinMarketCap), run:
```bash
make setup-local
make start
```

## Project Setup (Dev)
### Create Configuration Files `.env`
Create a `.env` file in the root directory near `docker-compose.dev.yml` and add the following environment variables:

```env
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DB=<your_database_name>
RABBITMQ_DEFAULT_USER=<your_rabbitmq_user>
RABBITMQ_DEFAULT_PASS=<your_rabbitmq_password>

BACKEND__DEBUG=False
BACKEND__STATE=prod
BACKEND__TCP_PORT=8200
BACKEND__SECRET_KEY=<your_backend_secret_key>
BACKEND__AUTHENTICATION_ACCESS_TOKEN_SECRET_KEY=<your_authentication_secret_key>

WORKER_BLOCKCHAIR__TIMEOUT=60
WORKER_BLOCKCHAIR__PROXY=<your_proxy_url>

WORKER_COINMARKETCAP__TIMEOUT=60
```

```bash
docker compose -f docker-compose.dev.yml up -d --build
```


## Additional Commands

- **Stop all services**:
  ```bash
  docker compose -f docker-compose.local.yml down
  ```
- **Check logs for multiple services (backend, rabbitmq, postgres)**:
  ```bash
  docker compose -f docker-compose.local.yml logs -f backend rabbitmq postgres
  ```
