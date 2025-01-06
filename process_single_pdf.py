import boto3
import json

# Define the S3 bucket and file
s3_bucket = "vascculogic"
s3_key = "pdf/processed_20230408.pdf"

# Initialize Textract client
textract = boto3.client('textract')

# Function to process the PDF using Textract
def process_pdf(bucket, key):
    try:
        print(f"Processing file: s3://{bucket}/{key}")
        
        # Call Textract on the PDF
        response = textract.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            FeatureTypes=['TABLES', 'FORMS']
        )
        
        # Save the response to a JSON file
        output_file = "textract_single_output.json"
        with open(output_file, "w") as f:
            json.dump(response, f, indent=4)
        
        print(f"Textract processing complete. Output saved to {output_file}")
    
    except Exception as e:
        print(f"Error processing file s3://{bucket}/{key}: {e}")

# Process the specific PDF
process_pdf(s3_bucket, s3_key)

