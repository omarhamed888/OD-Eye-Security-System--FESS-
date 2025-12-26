#!/bin/bash
set -e
set -x

echo "🚀 Starting FESS Container..."

# Wait for dependencies
echo "⏳ Waiting for Redis..."
until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; do
  echo "   Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready"

echo "⏳ Waiting for Kafka..."
until timeout 5 bash -c "echo > /dev/tcp/${KAFKA_BOOTSTRAP_SERVERS%%:*}/${KAFKA_BOOTSTRAP_SERVERS##*:}" 2>/dev/null; do
  echo "   Kafka is unavailable - sleeping"
  sleep 5
done
echo "✅ Kafka connection available"

# Download models if not present (optional)
if [ ! -f "/app/checkpoints/rtmdet_tiny.pth" ]; then
  echo "📥 RTMDet model not found in /app/checkpoints/"
  echo "⚠️  Model download skipped (add URL in entrypoint.sh if needed)"
  echo "ℹ️  The detector will fail without model files"
fi

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/known_faces

echo "✅ All dependencies ready"
echo "🎬 Starting FESS application..."

# Execute the main command
exec "$@"
