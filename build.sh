#!/bin/bash

# Set HOST environment variable to prevent Docker Compose warnings
export HOST=0.0.0.0

# Run docker compose build
docker compose build
