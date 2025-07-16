FROM python:3.11-slim

WORKDIR /app

# Update system packages to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Install Hatch
RUN pip install --upgrade pip hatch

# Copy project files
COPY . /app

# Install dependencies via Hatch
RUN hatch env create

# Default command (can be changed as needed)
CMD ["hatch", "run", "python", "-m", "src.cli.main"]