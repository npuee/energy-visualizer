
# Use official Python 3 Alpine image for minimal size
FROM python:3.11-alpine AS builder



# Set work directory
WORKDIR /app

# Copy requirements first (for cache efficiency and so RUN can use it)
COPY requirements.txt ./

# Install build dependencies, pip packages, and cleanup in one layer
RUN apk add --no-cache gcc musl-dev libffi-dev \
    && pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --prefix=/install -r requirements.txt \
    && apk del gcc musl-dev libffi-dev \
    && rm -rf /root/.cache /root/.pip /tmp/*


COPY app.py ./
COPY energy.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY entrypoint.sh ./

FROM python:3.11-alpine
WORKDIR /app


# Remove unnecessary files and locales (only those that exist)
RUN rm -rf /usr/share/doc /usr/share/man /usr/share/locale || true

# Copy installed packages from builder
COPY --from=builder /install /usr/local

COPY app.py ./
COPY energy.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY entrypoint.sh ./

# No need to remove build tools in final image (not installed)

# Expose the port (from settings.json, default 8889)
EXPOSE 8889

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
