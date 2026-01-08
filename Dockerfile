# Use official Python 3 image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port (from settings.json, default 8889)
EXPOSE 8889

# Run the app with WSGI (Waitress)
CMD ["python3", "wsgi.py"]
