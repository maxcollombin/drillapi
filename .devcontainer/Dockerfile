FROM mcr.microsoft.com/devcontainers/python:1-3.12

# Install common system packages useful for development (adjust as needed)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    make \
    libpq-dev \
    curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER vscode
