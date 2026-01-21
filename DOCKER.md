# Docker Deployment Guide

This guide explains how to run the Scribify web application using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- OpenAI API key

## Quick Start

1. **Set up your environment**

   Copy the example environment file and add your OpenAI API key:

   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Start the application**

   ```bash
   docker compose up -d
   ```

3. **Access the web interface**

   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

4. **Stop the application**

   ```bash
   docker compose down
   ```

## Configuration

### Environment Variables

Configure the application using environment variables in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | - |
| `OPENAI_MODEL` | Transcription model to use | `gpt-4o-mini-transcribe` |
| `OPENAI_TIMEOUT` | API timeout in seconds | `300` |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |

### Port Configuration

By default, the application runs on port 8000. To change this, edit the `ports` section in `compose.yaml`:

```yaml
ports:
  - "3000:8000"  # Change 3000 to your desired port
```

## Docker Compose Commands

### Build and start

```bash
docker compose up -d --build
```

### View logs

```bash
# All logs
docker compose logs -f

# Last 100 lines
docker compose logs -f --tail=100
```

### Check status

```bash
docker compose ps
```

### Restart the service

```bash
docker compose restart
```

### Stop and remove containers

```bash
docker compose down
```

### Stop and remove containers, volumes, and images

```bash
docker compose down -v --rmi all
```

## Docker Best Practices Implemented

### Security

- **Non-root user**: Application runs as `appuser` (UID 1000)
- **Read-only filesystem**: Container filesystem is read-only where possible
- **Dropped capabilities**: Unnecessary Linux capabilities are dropped
- **No new privileges**: Prevents privilege escalation
- **Security options**: `no-new-privileges` is enabled

### Performance

- **Multi-stage build**: Reduces final image size
- **Layer caching**: Optimized Dockerfile for faster builds
- **Resource limits**: CPU and memory limits prevent resource exhaustion
- **Health checks**: Automatic container health monitoring

### Reliability

- **Restart policy**: Containers restart automatically unless stopped
- **Health checks**: Application health is monitored
- **Logging**: JSON file logging with rotation (10MB max, 3 files)
- **Volume persistence**: Data persists across container restarts

## Volumes

The application uses two volumes for data persistence:

- `scribify-uploads`: Temporary storage for uploaded audio files
- `scribify-results`: Storage for transcription results

### Inspecting volumes

```bash
docker volume ls
docker volume inspect scribify_scribify-uploads
```

### Backing up volumes

```bash
# Backup uploads
docker run --rm -v scribify_scribify-uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# Backup results
docker run --rm -v scribify_scribify-results:/data -v $(pwd):/backup alpine tar czf /backup/results-backup.tar.gz -C /data .
```

## Health Checks

The container includes automatic health checks:

- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 10 seconds
- **Retries**: 3

Check health status:

```bash
docker compose ps
docker inspect --format='{{.State.Health.Status}}' scribify-web
```

## Resource Limits

Default resource limits:

- **CPU limit**: 2.0 cores
- **Memory limit**: 2GB
- **CPU reservation**: 0.5 cores
- **Memory reservation**: 512MB

Adjust these in `compose.yaml` under `deploy.resources`.

## Networking

The application uses a custom bridge network (`scribify-network`) for isolation. Services communicate within this network.

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs scribify-web

# Check if API key is set
docker compose config | grep OPENAI_API_KEY
```

### Permission issues

The application runs as UID 1000. Ensure volume permissions are correct:

```bash
docker compose down
docker volume rm scribify_scribify-uploads scribify_scribify-results
docker compose up -d
```

### Out of memory errors

Increase memory limit in `compose.yaml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G
```

### Slow transcription

Increase timeout in `.env`:

```env
OPENAI_TIMEOUT=600
```

## Production Deployment

For production deployments, consider:

1. **Use secrets management**
   ```yaml
   secrets:
     openai_api_key:
       external: true
   ```

2. **Enable HTTPS** with a reverse proxy (nginx, Traefik, Caddy)

3. **Set up monitoring** (Prometheus, Grafana)

4. **Configure backups** for volumes

5. **Use environment-specific configs**

6. **Implement rate limiting** at the proxy level

7. **Set up log aggregation** (ELK stack, Loki)

## Development

For development with hot-reload:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up
```

Create `compose.dev.yaml`:

```yaml
services:
  scribify-web:
    volumes:
      - ./whisper_cli:/app/whisper_cli
      - ./web_app.py:/app/web_app.py
    command: uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once running, access the auto-generated API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

For issues and questions:
- Check the main README.md
- Review Docker logs: `docker compose logs -f`
- Verify your environment configuration
