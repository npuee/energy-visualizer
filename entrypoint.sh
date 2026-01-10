echo "Starting Elering Visualizer..."
#!/bin/bash
set -e

# Activate virtualenv if present
if [ -f /app/venv/bin/activate ]; then
  source /app/venv/bin/activate
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
  echo "{\n  \"cache_ttl\": 3600,\n  \"server_port\": 8889,\n  \"eic_nicknames\": {}\n}" > /app/settings.json
  echo "settings.json not found, created default settings.json."
fi

# Load port from settings.json
PORT=$(python3 -c "import json; s=json.load(open('/app/settings.json')); print(s.get('server_port', 8889))" 2>/dev/null || echo 8889)

# Start the server
exec python3 -m waitress --host=0.0.0.0 --port=$PORT app:app
