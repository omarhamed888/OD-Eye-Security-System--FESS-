# Docker Setup Guide

## Quick Start

### 1. Build and Start All Services

```bash
docker-compose up -d
```

This will start:
- Redis (cache)
- Kafka (event streaming)
- FESS (detection application)
- Prometheus (metrics collection)
- Grafana (visualization)

### 2. Check Service Health

```bash
docker-compose ps
```

Expected output:
```
NAME               STATUS              PORTS
fess-detector      Up (healthy)        0.0.0.0:8000->8000/tcp
fess-redis         Up (healthy)        0.0.0.0:6379->6379/tcp
fess-kafka         Up (healthy)        0.0.0.0:9092->9092/tcp
fess-prometheus    Up                  0.0.0.0:9090->9090/tcp
fess-grafana       Up                  0.0.0.0:3000->3000/tcp
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fess
```

### 4. Stop Services

```bash
# Stop and keep data
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove all data (volumes)
docker-compose down -v
```

---

## Development Mode

### Run with Hot-Reload

The `docker-compose.yml` already mounts `./src` for hot-reload:

```bash
docker-compose up
```

Any changes to `src/` files will be immediately reflected (if your app supports hot-reload).

### Rebuild After Dependency Changes

```bash
docker-compose build fess
docker-compose up -d fess
```

---

## Production Deployment

### 1. Build Optimized Image

```bash
docker build -t fess:1.0.0 .
```

### 2. Run Production Compose

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  fess:
    image: fess:1.0.0
    env_file: .env.production
    volumes:
      - ./known_faces:/app/known_faces:ro  # Read-only
      - ./logs:/app/logs
```

Then run:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Scale Detectors

```bash
docker-compose up -d --scale fess=3
```

---

## Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| FESS API | http://localhost:8000 | - |
| Health Check | http://localhost:8000/health | - |
| Metrics | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Redis | localhost:6379 | - |
| Kafka | localhost:9092 | - |

---

## Common Operations

### Access Container Shell

```bash
docker-compose exec fess bash
```

### Check Redis

```bash
# Ping Redis
docker-compose exec redis redis-cli ping

# List keys
docker-compose exec redis redis-cli KEYS '*'

# Get value
docker-compose exec redis redis-cli GET 'face:some_id'
```

### Check Kafka

```bash
# List topics
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Create topic
docker-compose exec kafka kafka-topics.sh --create --topic test.topic --bootstrap-server localhost:9092

# Consume messages
docker-compose exec kafka kafka-console-consumer.sh --topic motion.detection.events --from-beginning --bootstrap-server localhost:9092
```

### View Metrics

```bash
curl http://localhost:8000/metrics
```

### Check Health

```bash
curl http://localhost:8000/health | jq
```

---

## Troubleshooting

### Container Won't Start

```bash
# View logs
docker-compose logs fess

# Check specific error
docker-compose logs fess | grep -i error
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check from FESS container
docker-compose exec fess redis-cli -h redis ping
```

### Kafka Connection Issues

```bash
# Check Kafka logs
docker-compose logs kafka

# Test broker connectivity
docker-compose exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Port Already in Use

```powershell
# Windows: Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Clear All Data

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi fess:latest
```

### Permission Issues

```bash
# Fix known_faces permissions
chmod -R 755 known_faces/

# Fix logs permissions
chmod -R 755 logs/
```

---

## Performance Optimization

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  fess:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Build Optimization

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t fess:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t fess:latest .
```

---

## Monitoring & Alerts

### Prometheus Queries

Access Prometheus at http://localhost:9090 and try:

```promql
# Detection rate
rate(fess_detections_total[5m])

# P95 latency
histogram_quantile(0.95, rate(fess_detection_latency_seconds_bucket[5m]))

# Cache hit rate
rate(fess_face_cache_hits_total[5m]) / (rate(fess_face_cache_hits_total[5m]) + rate(fess_face_cache_misses_total[5m]))
```

### Grafana Setup

1. Access Grafana: http://localhost:3000
2. Login: `admin/admin`
3. Add Prometheus data source:
   - URL: `http://prometheus:9090`
4. Import dashboard (create custom or use template)

---

## Backup & Restore

### Backup

```bash
# Backup Redis data
docker-compose exec redis redis-cli BGSAVE

# Export volumes
docker run --rm -v fess_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data

# Backup Kafka
docker run --rm -v fess_kafka-data:/data -v $(pwd):/backup alpine tar czf /backup/kafka-backup.tar.gz /data
```

### Restore

```bash
# Restore Redis
docker run --rm -v fess_redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz

# Restart services
docker-compose restart redis
```

---

## Security Best Practices

### 1. Use Secrets

```yaml
services:
  fess:
    secrets:
      - redis_password
      - kafka_password

secrets:
  redis_password:
    file: ./secrets/redis_password.txt
```

### 2. Network Isolation

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### 3. Non-Root User

Already configured in Dockerfile:
```dockerfile
USER fess
```

---

## Next Steps

1. ✅ Configure monitoring dashboards in Grafana
2. ✅ Set up alerting rules in Prometheus
3. ✅ Add model files to `checkpoints/`
4. ✅ Configure camera streams
5. ✅ Test with production workload
6. ✅ Set up log aggregation (ELK/Loki)
7. ✅ Configure backup automation

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Redis Documentation](https://redis.io/docs/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
