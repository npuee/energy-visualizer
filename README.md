
# Energy Daily Visualizer

This project is a Flask server and Plotly frontend for visualizing daily energy consumption from the Estfeed/Elering API. It supports caching, nicknames/colors for meters, and a modern UI.

## Features
- Visualizes daily kWh per meter and total
- Caching (1 hour, file-backed)
- Configurable nicknames/colors for each EIC in `settings.json`
- Legend and hover show nicknames
- Timestamp of last data fetch
- Docker support

## Quick Start (Local)

1. Install dependencies:
	```bash
		python3 -m pip install -r requirements.txt
		```
2. Configure your settings in `settings.json` (see below).
3. Run the server:
		```bash
		python3 app.py
		# then open http://localhost:8889 (or the port in settings.json)
		```

## Docker Usage

1. Build the image:
	```bash
		docker build -t energy-visualizer .
		```
2. Run the container (mount your config if needed):
		```bash
		docker run -p 8889:8889 -v "$PWD/settings.json:/app/settings.json:ro" energy-visualizer
		```

## Configuration

Edit `settings.json` to set:
- `auth_data` for Elering API (see Elering docs)
- `cache_ttl` (seconds)
- `server_port` and `host`
- `eic_nicknames` for meter display names and colors


Example:
```json
{
	"auth_data": { "client_id": "...", "client_secret": "...", "grant_type": "client_credentials" },
	"cache_ttl": 3600,
	"server_port": 8889,
	"host": "0.0.0.0",
	"eic_nicknames": {
		"38ZEE-00261472-Y": { "nick": "Shortname.", "color": "#1f77b6" }
	}
}
```

## Security

- `settings.json` is in `.gitignore` and should not be committed to version control.
- Do not share your API credentials.

## License
MIT
