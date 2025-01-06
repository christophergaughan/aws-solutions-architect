import boto3
import json
import time
import os

# AWS S3 and Textract setup
s3_bucket = "vascculogic"  # Bucket name only (no "/")
prefix = "pdf/"  # Prefix for the folder containing PDFs
analysis_output_bucket = "vascculogic"  # Bucket for Textract output
output_prefix = "textract_analysis/output/"
region = "us-east-1"  # Replace with your region

# Initialize clients
s3_client = boto3.client('s3', region_name=region)
textract_client = boto3.client('textract', region_name=region)

def list_pdfs(bucket_name, prefix=""):
    """List all PDFs in the given S3 bucket with a specific prefix."""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        print(f"No files found in {bucket_name}/{prefix}")
        return []
    pdf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
    return pdf_files

def start_textract_job(bucket, file_name):
    """Start a Textract job for a given file."""
    response = textract_client.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': file_name}},
        FeatureTypes=["TABLES", "FORMS"],
        OutputConfig={'S3Bucket': analysis_output_bucket, 'S3Prefix': output_prefix}
    )
    return response['JobId']

def check_job_status(job_id):
    """Check the status of a Textract job."""
    while True:
        response = textract_client.get_document_analysis(JobId=job_id)
        status = response['JobStatus']
        if status in ['SUCCEEDED', 'FAILED']:
            return status
        print(f"Job {job_id} is {status}. Waiting...")
        time.sleep(5)

def download_textract_output(bucket, prefix, local_dir="./output"):
    """Download Textract output from S3."""
    os.makedirs(local_dir, exist_ok=True)
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in response:
        print(f"No output files found in {bucket}/{prefix}")
        return
    for obj in response['Contents']:
        file_name = obj['Key'].split('/')[-1]
        s3_client.download_file(bucket, obj['Key'], f"{local_dir}/{file_name}")

def parse_textract_output(file_path):
    """Parse the Textract output for the required fields."""
    with open(file_path, 'r') as f:
        textract_data = json.load(f)
    
    extracted_data = {
        "Black Box Warning": "",
        "Compound": "",
        "Approval": "",
        "Studies": []
    }
    
    for block in textract_data.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            text = block['Text']
            if "BLACK BOX WARNING" in text.upper():
                extracted_data["Black Box Warning"] = text
            elif "COMPOUND" in text.upper():
                extracted_data["Compound"] = text
            elif "APPROVAL" in text.upper():
                extracted_data["Approval"] = text
        elif block['BlockType'] == 'TABLE':
            # Parse table data for Studies, N, Dose, etc.
            pass  # Implement table parsing logic here
    
    return extracted_data

# Main script
if __name__ == "__main__":
    pdf_files = list_pdfs(s3_bucket, prefix)
    print(f"Found {len(pdf_files)} PDF files to process.")

    for pdf_file in pdf_files:
        print(f"Processing file: {pdf_file}")
        job_id = start_textract_job(s3_bucket, pdf_file)
        print(f"Started Textract job with ID: {job_id}")

        status = check_job_status(job_id)
        if status == 'SUCCEEDED':
            print(f"Textract job {job_id} succeeded. Downloading output...")
            download_textract_output(analysis_output_bucket, output_prefix)
        else:
            print(f"Textract job {job_id} failed.")

    print("Parsing Textract output...")
    output_files = [f"./output/{file}" for file in os.listdir("./output") if file.endswith(".json")]
    for output_file in output_files:
        parsed_data = parse_textract_output(output_file)
        print(f"Results for {output_file}:")
        print(json.dumps(parsed_data, indent=2))

