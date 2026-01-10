# Unreleased (dev branch)
- Added entrypoint.sh for container startup and Waitress server management
- Dockerfile now uses entrypoint.sh as ENTRYPOINT and removes wsgi.py
- entrypoint.sh checks for required environment variables and creates default settings.json if missing
- Switched Bootstrap and Plotly dependencies in index.html to use local static files instead of CDN links


# Changelog

## 2026-01-09
- Added entrypoint.sh for container startup and Waitress server management
- Dockerfile now uses entrypoint.sh as ENTRYPOINT and removes wsgi.py
- entrypoint.sh checks for required environment variables and creates default settings.json if missing
- Elering API credentials are now set via .env file (see .env.example), not settings.json
- Updated README.md to document .env usage and Docker --env-file
- Updated run.sh and Docker instructions for .env
- Cleaned up settings.json (removed auth_data)
- Added a dedicated 'HTTP Basic Authentication' section to the README for clarity and usage instructions.
- Summary values (total, average, min, max, today) now use 2 digits after the decimal point instead of 3.
- HTTP Basic Auth documented in README.md and added to settings.example.json
- Fully optimized rewrite of energy.py (settings/cache handling, EIC matching, type hints, docs, modularity)
- Refactored static text in index.html to use a language.js file for all UI strings
- Added Estonian language support and user-friendly language switching (setLanguage/getLang)
- Updated documentation comment in static/language.js for new multi-language structure
- General improvements and bugfixes
- Added settings.example.json as a template for configuration
- Anonymized EIC nicknames in settings.example.json for safe sharing
- run.sh now exits with an error if settings.json does not exist, instead of creating a default file
- Aggressively slimmed Docker image with multi-stage build and removal of build dependencies (reducing image size from 169MB to 66MB)
- Only copy required files into Docker image for security and size
- Added multi-arch build.sh script (local build only, no push)
- run.sh now deletes old image before building, tags as :latest, and uses --restart always
- All template CSS moved to static/custom.css
- Plotly controls (zoom, screenshot, etc.) removed from chart
- Today's value excluded from min calculation in summary (shown as today_kwh)
- README: added screenshot, API credential instructions, and manual refresh info


## 2026-01-08
- Initial project setup: Flask app, Plotly frontend, caching, settings.json, Docker, .gitignore, README, and basic CI scripts.
- Added support for Elering/Estfeed API with OAuth2 credentials.
- Added color and nickname support for EICs in settings.json.
- Added Docker and run.sh for easy deployment.
