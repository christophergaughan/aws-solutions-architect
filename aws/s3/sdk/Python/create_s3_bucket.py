import boto3
import os

# S3 Bucket configuration
bucket_name = os.getenv('BUCKET_NAME')  # Fetching bucket name from environment variables
region = 'us-east-1'  # Specify the region (us-east-1 doesn't require a LocationConstraint)

# Initialize AWS S3 client
client = boto3.client('s3', region_name=region)

# Create S3 bucket for us-east-1 without LocationConstraint
response = client.create_bucket(Bucket=bucket_name)

# Print the response
print(response)



