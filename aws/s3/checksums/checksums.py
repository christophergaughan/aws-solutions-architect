import boto3
import botocore

def get_s3_checksum(bucket_name, object_key, algorithm='MD5'):
    """
    Fetches the checksum of an object stored in an S3 bucket.
    
    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - object_key (str): The key (path) of the object in the S3 bucket.
    - algorithm (str): The checksum algorithm. Default is 'MD5'. Could be extended to CRC32, SHA256, etc.
    
    Returns:
    - checksum (str): The checksum (e.g., ETag) of the object.
    """
    # Initialize the S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Retrieve metadata for the object
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        if algorithm == 'MD5':
            # ETag typically contains the MD5 checksum (for non-multipart uploads)
            etag = response['ETag'].strip('"')
            print(f"MD5 Checksum (ETag) of {object_key}: {etag}")
            return etag
        elif algorithm == 'CRC32':
            # CRC32 can be computed manually by downloading the file and using a local CRC32 implementation.
            print("CRC32 calculation is not directly supported by AWS S3.")
            return None
        elif algorithm == 'SHA256':
            # Similarly, SHA256 must be calculated by downloading the file and hashing it locally.
            print("SHA256 calculation is not directly supported by AWS S3.")
            return None
        else:
            print(f"Unsupported algorithm: {algorithm}")
            return None
        
    except botocore.exceptions.ClientError as e:
        print(f"Error fetching object {object_key} from bucket {bucket_name}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    bucket_name = "your-s3-bucket-name"
    object_key = "path/to/your-file.txt"  # Replace with your actual file key

    # Fetch MD5 checksum (ETag)
    get_s3_checksum(bucket_name, object_key, algorithm='MD5')
