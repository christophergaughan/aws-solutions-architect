#!/bin/bash
set -e

# Ensure script runs from the correct directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to load AWS credentials from a .env file
load_env_credentials() {
    if [ -f .env ]; then
        echo "Loading AWS credentials from .env file..."
        export $(grep -v '^#' .env | xargs)
    fi
}

# Detect platform and set correct AWS CLI URL
if [ "$(uname -m)" == "aarch64" ]; then
    CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
elif [ "$(uname -m)" == "x86_64" ]; then
    CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
else
    echo "Unsupported platform: $(uname -m)"
    exit 1
fi

# Install AWS CLI if not already installed
if command -v aws &>/dev/null; then
    echo "AWS CLI is already installed. Skipping installation."
else
    echo "Installing AWS CLI..."
    curl "$CLI_URL" -o "awscliv2.zip"
    unzip -o awscliv2.zip
    sudo ./aws/install --update
    rm -rf aws awscliv2.zip
fi

# Load credentials from .env if not already set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    load_env_credentials
fi

# Verify AWS credentials
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Configuring AWS CLI with credentials..."
    aws configure set region us-east-1
    aws configure set output json
    aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
    aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
    echo "AWS CLI configured successfully."
else
    echo "ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are not set."
    echo "       Please export these variables or add them to a .env file."
    exit 1
fi

# Confirm AWS CLI version
echo "AWS CLI installation complete."
aws --version

