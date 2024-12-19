FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    python3-venv \
    curl \
    awscli \
    unzip \
    gnupg \
    software-properties-common \
    npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo ./aws/install \
    && rm -rf aws awscliv2.zip

# Default environment variables
ENV AWS_DEFAULT_REGION=us-east-1

# Copy project files
COPY . /workspace

# Make scripts executable
RUN chmod +x /workspace/aws/bin/*.sh

WORKDIR /workspace

