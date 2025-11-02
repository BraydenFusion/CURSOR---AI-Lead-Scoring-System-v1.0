#!/bin/bash
# Railway startup script - properly expands PORT environment variable

# Get PORT from environment, default to 8000 if not set
PORT=${PORT:-8000}

# Start uvicorn with the port
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

