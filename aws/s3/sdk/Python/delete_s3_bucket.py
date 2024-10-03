import boto3
import os

# S3 Bucket configuration
bucket_name = os.getenv('BUCKET_NAME')  # Fetching bucket name from environment variables
region = os.getenv('AWS_REGION', 'us-east-1')  # Default to us-east-1 if not specified

# Initialize AWS S3 client and resource
s3 = boto3.resource('s3', region_name=region)
client = boto3.client('s3', region_name=region)

# Step 1: Delete all objects in the bucket
bucket = s3.Bucket(bucket_name)
bucket.objects.all().delete()
print(f"All objects in bucket {bucket_name} deleted successfully.")

# Step 2: Delete the bucket, handling us-east-1 differently even though there is no fiffereence in this case
if region == 'us-east-1':
    # For us-east-1, simply delete the bucket without any extra configuration
    response = client.delete_bucket(Bucket=bucket_name)
else:
    # For other regions, no additional config needed but the structure is here for future use
    response = client.delete_bucket(Bucket=bucket_name)

# Print the response
print(f"Bucket {bucket_name} deleted successfully!")
