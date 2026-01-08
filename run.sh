#!/bin/bash
set -e

# Create settings.json if it does not exist
if [ ! -f settings.json ]; then
  cat > settings.json <<EOF
{
  "auth_data": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "grant_type": "client_credentials"
  },
  "cache_ttl": 3600,
  "server_port": 8889,
  "host": "0.0.0.0",
  "eic_nicknames": {
    "38ZEE-00261472-Y": { "nick": "Shortname.", "color": "#1f77b6" }
  }
}
EOF
  echo "Created default settings.json. Please edit it with your credentials."
else
  echo "settings.json already exists."
fi

# Build Docker image
docker build -t energy-visualizer .

# Run Docker container with WSGI (Waitress)
# Remove any previous container with the same name
docker rm -f energy-visualizer-run 2>/dev/null || true
docker run -d --name energy-visualizer-run -p 8889:8889 -v "$PWD/settings.json:/app/settings.json:ro" energy-visualizer python3 wsgi.py
