import boto3
import os

# S3 Bucket configuration
bucket_name = os.getenv('BUCKET_NAME')  # Fetch the bucket name from environment variables
region = os.getenv('AWS_REGION', 'us-east-1')  # Fetch the region, default to us-east-1

# Initialize the S3 resource
s3 = boto3.resource('s3', region_name=region)

# Delete all objects in the specified bucket
def delete_objects(bucket_name):
    bucket = s3.Bucket(bucket_name)
    response = bucket.objects.all().delete()  # Deletes all objects in the bucket

    print(f"All objects in bucket '{bucket_name}' have been deleted.")
    return response

# Call the delete_objects function
delete_objects(bucket_name)
