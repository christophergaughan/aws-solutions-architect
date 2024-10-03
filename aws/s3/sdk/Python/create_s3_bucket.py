import boto3
import os

# S3 Bucket configuration
bucket_name = os.getenv('BUCKET_NAME')  # Fetching bucket name from environment variables
region = 'us-east-1'  # Change region as needed

# Initialize AWS S3 client
client = boto3.client('s3', region_name=region)

# Create S3 bucket, handling us-east-1 differently
if region == 'us-east-1':
    # For us-east-1, do not specify a LocationConstraint
    response = client.create_bucket(Bucket=bucket_name)
else:
    # For all other regions, include the LocationConstraint
    response = client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': region
        }
    )

# Print the response
print(response)




