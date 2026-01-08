
# Energy Daily Visualizer

This project is a Flask server and Plotly frontend for visualizing daily energy consumption from the Estfeed/Elering API. It supports caching, nicknames/colors for meters, and a modern UI.

- ![Screenshot](https://raw.githubusercontent.com/npuee/energy-visualizer/refs/heads/master/docs/Screenshot.png)

## Features
## Manually Refresh Data

To force a fresh fetch from the API (bypassing the cache), open this URL in your browser or use curl:

```
http://localhost:8889/data?clear_cache=1
```

Or with curl:

```bash
curl "http://localhost:8889/data?clear_cache=1"
```

This will clear the cache and trigger a new data fetch on the next request.
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

You can use the provided `run.sh` script to create a default `settings.json` (if missing), build the Docker image, and run the container:

```bash
chmod +x run.sh
./run.sh
```

This will:
- Create a default `settings.json` if it does not exist (edit it with your real credentials!)
- Build the Docker image
- Run the container, mounting your `settings.json` for configuration

Alternatively, you can build and run manually:

```bash
docker build -t energy-visualizer:latest .
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
