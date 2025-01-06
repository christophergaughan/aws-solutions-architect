import boto3
import csv

# AWS Clients
s3 = boto3.client('s3')
textract = boto3.client('textract', region_name='us-east-1')

# Define S3 bucket and folder
bucket_name = "vascculogic"
file_name = "pdf/processed_20230408.pdf"
# Define fields to extract
fields = [
    "Black Box Warning",
    "Compound",
    "Approval",
    "Study",
    "N for each study",
    "Dose for each study",
    "Clinical Efficacy",
    "Clinical Safety",
    "Clinical Discontinuation"
]

# Function to list all PDFs in the S3 folder
def list_pdfs(bucket, folder):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=folder)
    if "Contents" not in response:
        raise Exception("No files found in the specified S3 folder.")
    return [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".pdf")]

# Function to process a PDF with Textract
def process_pdf(s3_bucket, file_name):
    response = textract.analyze_document(
        Document={"S3Object": {"Bucket": s3_bucket, "Name": file_name}},
        FeatureTypes=["TABLES", "FORMS"]
    )

    # Extract text blocks from response
    blocks = response["Blocks"]
    text_data = []

    for block in blocks:
        if block["BlockType"] == "LINE":
            text_data.append(block["Text"])

    return "\n".join(text_data)

# Function to extract specific fields
def extract_fields(text):
    data = {}
    for field in fields:
        data[field] = "N/A"  # Default value

        # Simple matching logic for each field (expand as needed)
        if field == "Black Box Warning" and "WARNING" in text.upper():
            data[field] = "Yes"
        elif field == "Compound":
            # Example logic for extracting compound name
            lines = [line for line in text.split("\n") if "capsule" in line.lower()]
            data[field] = lines[0] if lines else "N/A"
        elif field == "Approval" and "Approval" in text:
            data[field] = text.split("Approval:")[1].split("\n")[0].strip()
        elif field == "Study" and "Section 14" in text:
            data[field] = "Study Found"  # Simplified logic
        # Add similar logic for other fields...

    return data

# Main script logic
try:
    # List PDFs dynamically from S3
    pdf_files = list_pdfs(s3_bucket, s3_folder)
    if not pdf_files:
        raise Exception("No PDF files found in the specified folder.")
    
    print(f"Found {len(pdf_files)} PDF files in {s3_folder}")

    # Process PDFs and write to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["PDF Name"] + fields)
        writer.writeheader()

        for pdf_file in pdf_files:
            print(f"Processing {pdf_file}...")
            text = process_pdf(s3_bucket, pdf_file)
            extracted_data = extract_fields(text)
            extracted_data["PDF Name"] = pdf_file
            writer.writerow(extracted_data)

    print(f"Extraction completed. Data saved to {output_csv}")

except Exception as e:
    print(f"Error: {e}")

