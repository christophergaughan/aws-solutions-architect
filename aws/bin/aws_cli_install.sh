#!/usr/bin/env bash
cd /workspace
curl -O https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
unzip awscli-exe-linux-x86_64.zip
sudo ./aws/install
cd $THEIA_WORKSPACE_ROOT
aws configure set region us-east-1
aws configure set output json
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY