
# Elering Daily Visualizer

This project is a Flask server and Plotly frontend for visualizing daily energy consumption from the Estfeed/Elering API. It supports caching, nicknames/colors for meters, and a modern UI.

 ![Screenshot](https://raw.githubusercontent.com/npuee/energy-visualizer/refs/heads/master/docs/Screenshot.png)


## Quick Start (Local)

1. Install dependencies:
	```bash
	python3 -m pip install -r requirements.txt
	```
2. You can keep a local `settings.json` for overrides, but the container will create a default `settings.json` at runtime when missing. See `app/settings.example.json` for defaults.
3. Copy `.env.example` to `.env` and fill in your Elering API credentials:
		- `AUTH_CLIENT_ID=your_client_id_here`
		- `AUTH_CLIENT_SECRET=your_client_secret_here`
4. Run the server:
		- Use the provided helper script (recommended):
			```bash
			chmod +x scripts/run.sh
			./scripts/run.sh
			# then open http://localhost:8889
			```
			- `scripts/run.sh` will:
				- build the Docker image from the project root,
				- mount a host `settings.json` into the container if present (read-only), and
				- pass `--env-file .env` to the container if `.env` exists.
		- For production (without Docker) run with Waitress:
			```bash
			python3 -m waitress --host=0.0.0.0 --port=8889 app:app
			```
		- For development use the Flask dev server:
			```bash
			python3 -m flask run --host=0.0.0.0 --port=8889
			```


## Docker Usage

You can use the provided `scripts/run.sh` script to build the Docker image and run the container:

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

Note: `scripts/run.sh` builds the Docker image (from the project root) before starting the container.


This will:
- Build the Docker image
- Run the container (the container will create a default `settings.json` if one is not provided)
- Mount your host `settings.json` into the container if present (so you can keep secrets/config out of the image)
- Load Elering API credentials from your `.env` file


Alternatively, you can build and run manually (or use `scripts/build.sh` for multi-arch builds):

```bash
docker build -t energy-visualizer:latest .
docker run -p 8889:8889 --env-file .env energy-visualizer
```

For multi-arch images, use the provided `scripts/build.sh` which uses `docker buildx`:

```bash
chmod +x scripts/build.sh
./scripts/build.sh --push myuser/energy-visualizer latest  # pushes multi-arch to registry
``` 


## Configuration



### Environment Variables for Elering API

Set your Elering API credentials in a `.env` file (see `.env.example`):
- `AUTH_CLIENT_ID` (your Elering API client ID)
- `AUTH_CLIENT_SECRET` (your Elering API client secret)

Edit `settings.json` to set:
- `cache_ttl` (seconds)
- `eic_nicknames` for meter display names and colors
- `basic_auth_user` and `basic_auth_password` (optional, enables HTTP Basic Auth for all endpoints)

Notes about layout and files:
- Application Python package: `app/` (contains `__init__.py`, `energy.py`, `settings.example.json`)
- Startup entrypoint (container): `scripts/entrypoint.sh` (creates `/app/settings.json` if missing and starts Waitress)
- Build/run helpers: `scripts/run.sh`, `scripts/build.sh` (multi-arch)
- Templates: `templates/`, Static assets: `static/`

### HTTP Basic Authentication

If you set `basic_auth_user` and `basic_auth_password` in your `settings.json`, all endpoints will require HTTP Basic Auth.

- Most browsers and API clients (curl, Postman, etc.) will prompt for a username and password.
- Use the values you set in `settings.json`.
- Example curl usage:
	```bash
	curl -u admin:changeme http://localhost:8889/
	```
- If credentials are missing or incorrect, the server will respond with HTTP 401 Unauthorized.

**Note:** If you do not set these fields, authentication is not required.

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

### How to Get Elering API Credentials

1. Go to [Estfeed Elering API Guide](https://estfeed.elering.ee/account-settings/efkp-api-guide)
2. Log in with your account.
3. Follow the instructions to create an API client:
		- Register a new API client.
		- Copy your `client_id` and `client_secret`.
4. Store these credentials in your `.env` file (see `.env.example`) so they are loaded as environment variables by the application:
	```env
	AUTH_CLIENT_ID=your_client_id_here
	AUTH_CLIENT_SECRET=your_client_secret_here
	```


## Security

- `settings.json` is in `.gitignore` and should not be committed to version control.
- Do not share your API credentials.

## License
MIT
