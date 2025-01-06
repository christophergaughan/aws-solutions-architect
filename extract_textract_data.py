#!/usr/bin/env python3

import boto3
import time
import pandas as pd
import re

# ---------------
# CONFIGURATION
# ---------------
BUCKET_NAME = "vascculogic"
PDF_PREFIX = "pdf/"
OUTPUT_EXCEL_FILE = "extracted_fields.xlsx"

# ---------------
# AWS CLIENTS
# ---------------
s3_client = boto3.client("s3")
textract_client = boto3.client("textract")

# ---------------
# FUNCTIONS
# ---------------

def list_pdfs_in_s3(bucket_name, prefix):
    """
    Return a list of all PDF file keys under the given prefix in an S3 bucket.
    """
    pdf_keys = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                if key.lower().endswith('.pdf'):
                    pdf_keys.append(key)
    return pdf_keys

def analyze_document_sync(bucket_name, document_key):
    """
    Synchronous call to Textract's analyze_document API.
    Works for documents up to 5 MB in size (passed as Bytes).
    """
    # 1) Download the PDF from S3 to memory
    pdf_obj = s3_client.get_object(Bucket=bucket_name, Key=document_key)
    file_content = pdf_obj['Body'].read()

    # 2) Call Textract analyze_document with TABLES and FORMS features
    response = textract_client.analyze_document(
        Document={'Bytes': file_content},
        FeatureTypes=['TABLES', 'FORMS']
    )
    return response

def get_text_from_blocks(blocks):
    """
    Return a single string of text from all LINE blocks.
    """
    text_lines = []
    for block in blocks:
        if block['BlockType'] == 'LINE':
            text_lines.append(block['Text'])
    return "\n".join(text_lines)

def extract_fields_from_text(full_text):
    """
    Extract fields from the entire PDF text:
      - Black Box warning (Y/N + any snippet found)
      - Compound name
      - Approval date
      - Section 14 data (study number, N, dose, efficacy, safety, discontinuation)
    """
    results = {
        "Black Box warning": None,
        "Black Box text": "",
        "Compound": None,
        "Approval": None,
        "Study": [],
        "N for each study": [],
        "Dose for each study": [],
        "Clinical Efficacy": [],
        "Clinical Safety": [],
        "Clinical discontinuation": []
    }

    # 1) BLACK BOX WARNING
    if "BLACK BOX WARNING" in full_text.upper():
        results["Black Box warning"] = "Y"
        # Attempt to capture text that follows "BLACK BOX WARNING"
        match = re.search(r'(BLACK BOX WARNING.*?)(\n\n|\Z)', full_text, re.IGNORECASE|re.DOTALL)
        if match:
            results["Black Box text"] = match.group(1).strip()
    else:
        results["Black Box warning"] = "N"

    # 2) COMPOUND NAME
    # This is a naive example; adapt to your actual PDF patterns
    # e.g., if there's a line "Compound Name: X"
    match = re.search(r'Compound Name:\s*(.*)', full_text, re.IGNORECASE)
    if match:
        results["Compound"] = match.group(1).strip()

    # 3) APPROVAL DATE
    # Similarly naive approach looking for "Approval Date: <some date>"
    match = re.search(r'Approval\s*Date:\s*(.*)', full_text, re.IGNORECASE)
    if match:
        results["Approval"] = match.group(1).strip()

    # 4) SECTION 14 DATA
    # We search for "Section 14" to the next mention of "Section 15" or end-of-doc
    section_14_data = ""
    match_sec14 = re.search(r'(Section\s*14.*?)(?=Section\s*15|$)', full_text, re.IGNORECASE|re.DOTALL)
    if match_sec14:
        section_14_data = match_sec14.group(1)
        # STUDY NUMBER
        study_nums = re.findall(r'Study\s*Number:\s*(\S+)', section_14_data, re.IGNORECASE)
        results["Study"].extend(study_nums)

        # N FOR EACH STUDY
        n_vals = re.findall(r'N\s*=\s*(\S+)', section_14_data, re.IGNORECASE)
        results["N for each study"].extend(n_vals)

        # DOSE
        doses = re.findall(r'Dose\s*=\s*(\S+)', section_14_data, re.IGNORECASE)
        results["Dose for each study"].extend(doses)

        # EFFICACY
        # Example: "Efficacy=Something"
        efficacy_matches = re.findall(r'Efficacy\s*=\s*(.*?)(;|\n|$)', section_14_data, re.IGNORECASE)
        results["Clinical Efficacy"].extend([em[0].strip() for em in efficacy_matches])

        # SAFETY
        safety_matches = re.findall(r'Safety\s*=\s*(.*?)(;|\n|$)', section_14_data, re.IGNORECASE)
        results["Clinical Safety"].extend([sm[0].strip() for sm in safety_matches])

        # DISCONTINUATION
        disc_matches = re.findall(r'Discontinuation\s*=\s*(.*?)(;|\n|$)', section_14_data, re.IGNORECASE)
        results["Clinical discontinuation"].extend([dm[0].strip() for dm in disc_matches])

    return results

def process_all_pdfs(bucket_name, prefix):
    """
    1. List PDFs in s3://{bucket_name}/{prefix}
    2. For each PDF:
       - Analyze with Textract (sync)
       - Extract text & parse fields
       - Build a row of data
    3. Save to Excel
    """
    pdf_keys = list_pdfs_in_s3(bucket_name, prefix)

    all_rows = []
    for pdf_key in pdf_keys:
        print(f"Processing {pdf_key} ...")
        try:
            # 1) Textract
            response = analyze_document_sync(bucket_name, pdf_key)

            # 2) Extract text
            blocks = response["Blocks"]
            full_text = get_text_from_blocks(blocks)

            # 3) Parse fields
            fields_dict = extract_fields_from_text(full_text)

            # 4) Build row
            row_data = {
                "PDF Key": pdf_key,
                "Black Box Warning (Y/N)": fields_dict["Black Box warning"],
                "Black Box Text": fields_dict["Black Box text"],
                "Compound Name": fields_dict["Compound"],
                "Approval Date": fields_dict["Approval"],
                "Study Number(s)": ", ".join(fields_dict["Study"]),
                "N for each study": ", ".join(fields_dict["N for each study"]),
                "Dose for each study": ", ".join(fields_dict["Dose for each study"]),
                "Clinical Efficacy": ", ".join(fields_dict["Clinical Efficacy"]),
                "Clinical Safety": ", ".join(fields_dict["Clinical Safety"]),
                "Clinical discontinuation": ", ".join(fields_dict["Clinical discontinuation"])
            }
            all_rows.append(row_data)

        except Exception as e:
            print(f"Error processing {pdf_key}: {e}")

    # 5) Convert to DataFrame & save to Excel
    df = pd.DataFrame(all_rows)
    df.to_excel(OUTPUT_EXCEL_FILE, index=False)
    print(f"\n=== Finished! {len(all_rows)} PDF(s) processed. ===")
    print(f"Results saved to: {OUTPUT_EXCEL_FILE}")

# ---------------
# MAIN
# ---------------
if __name__ == "__main__":
    process_all_pdfs(BUCKET_NAME, PDF_PREFIX)

