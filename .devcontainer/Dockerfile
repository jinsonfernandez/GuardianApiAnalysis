# Use the specified base image
FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt