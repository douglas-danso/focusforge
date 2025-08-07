FROM python:3.11-slim

WORKDIR /app

# Update system packages, install dependencies, and install Hatch
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip hatch

# Copy project files
COPY README.md ./
COPY pyproject.toml ./
COPY app/ ./app/
COPY main.py ./

# Install dependencies using Hatch
RUN hatch env create

# Expose port
EXPOSE 8000

# Use Hatch dev script for development with auto-reload
CMD ["hatch", "run", "dev"]
