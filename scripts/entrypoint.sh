#!/bin/sh
set -e

echo "Starting Elering Visualizer..."

# Activate virtualenv if present
if [ -f /app/venv/bin/activate ]; then
  . /app/venv/bin/activate
fi

# Print environment info for debugging
python --version

# Check required environment variables
if [ -z "$AUTH_CLIENT_ID" ] || [ -z "$AUTH_CLIENT_SECRET" ]; then
  echo "ERROR: AUTH_CLIENT_ID and/or AUTH_CLIENT_SECRET environment variables are not set. Container will exit."
  exit 1
fi

# Ensure settings.json exists, create default if missing
if [ ! -f /app/settings.json ]; then
  if [ -f /app/app/settings.example.json ]; then
    cp /app/app/settings.example.json /app/settings.json
    echo "settings.json not found, copied default settings.example.json to /app/settings.json."
  else
    echo "settings.example.json not found in /app/app; creating minimal settings.json"
    cat > /app/settings.json <<'EOF'
{
  "cache_ttl": 3600,
  "server_port": 8889,
  "eic_nicknames": {}
}
EOF
  fi
fi

# Load port from settings.json
PORT=$(python3 -c "import json; s=json.load(open('/app/settings.json')); print(s.get('server_port', 8889))" 2>/dev/null || echo 8889)

# Start the server
exec python3 -m waitress --host=0.0.0.0 --port=$PORT app:app
