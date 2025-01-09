#!/usr/bin/env python3

import json
import csv
import re

# CSV columns we want
FIELDNAMES = [
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

def parse_textract(json_data):
    """
    Parse the raw Textract JSON to find:
      - Black Box Warning
      - Compound
      - Approval
      - Study
      - N for each study
      - Dose for each study
      - Clinical Efficacy
      - Clinical Safety
      - Clinical Discontinuation
    Returns a dict keyed by our FIELDNAMES.
    """

    # Initialize defaults
    parsed_data = {
        "Black Box Warning": "N",       # assume 'N' unless we find evidence
        "Compound": "",
        "Approval": "",
        "Study": "",
        "N for each study": "",
        "Dose for each study": "",
        "Clinical Efficacy": "",
        "Clinical Safety": "",
        "Clinical Discontinuation": ""
    }

    # We'll gather all recognized lines
    all_lines = []
    for block in json_data.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            line_text = block.get("Text", "")
            all_lines.append(line_text)

    # --- EXAMPLE: Look for 'Boxed Warning' or 'Black Box Warning' ---
    # If we see that phrase, we set "Black Box Warning" = "Y"
    # (We do NOT set it true for 'Warnings and Precautions')
    for line in all_lines:
        lower_line = line.lower()
        if "boxed warning" in lower_line or "black box warning" in lower_line:
            parsed_data["Black Box Warning"] = "Y"
            break  # Once found, no need to keep searching

    # --- EXAMPLE: Look for brand/generic mention (KEYTRUDA) ---
    # We'll just do a naive check for "keytruda" and "pembrolizumab" on the same line.
    # Real logic might parse brand vs. generic more carefully.
    for line in all_lines:
        lower_line = line.lower()
        if "keytruda" in lower_line and "pembrolizumab" in lower_line:
            parsed_data["Compound"] = "KEYTRUDA (pembrolizumab)"
            break

    # --- EXAMPLE: Look for "Initial U.S. Approval: YYYY" ---
    # We'll parse out the piece after the colon, if present.
    # Commonly it's something like "Initial U.S. Approval: 2014"
    for line in all_lines:
        lower_line = line.lower()
        if "initial u.s. approval" in lower_line:
            parts = line.split(":")
            if len(parts) > 1:
                # e.g. "Initial U.S. Approval" is parts[0], then "2014" is parts[1]
                parsed_data["Approval"] = parts[1].strip()
            break

    # ---------------------------------------------------------------------
    # The following fields ("Study", "N for each study", "Dose for each study",
    # "Clinical Efficacy", "Clinical Safety", "Clinical Discontinuation")
    # are placeholders. Typically, you'd parse them by locating a "Section 14"
    # or some other heading in your doc, then applying heuristics or regex to find data.
    # Here, we just demonstrate possible examples.
    # ---------------------------------------------------------------------

    # Example: "Study"
    # Suppose the doc might say "Study Number: ABC123"
    for line in all_lines:
        match = re.search(r"study number:\s*(\S+)", line, flags=re.IGNORECASE)
        if match:
            parsed_data["Study"] = match.group(1)
            break

    # Example: "N for each study"
    # Suppose we might see "N= 345" in the doc
    for line in all_lines:
        match = re.search(r"\bn\s*=\s*(\d+)", line, flags=re.IGNORECASE)
        if match:
            parsed_data["N for each study"] = match.group(1)
            break

    # Example: "Dose for each study"
    # Suppose we might see "Dose: 50 mg" somewhere
    for line in all_lines:
        match = re.search(r"dose:\s*(\S+\s*mg)", line, flags=re.IGNORECASE)
        if match:
            parsed_data["Dose for each study"] = match.group(1)
            break

    # Example: "Clinical Efficacy"
    # Suppose there's a line "Clinical Efficacy: Superior to PBO by 20%"
    for line in all_lines:
        match = re.search(r"clinical efficacy:\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            # We’ll store the entire substring after “Clinical Efficacy:”
            parsed_data["Clinical Efficacy"] = match.group(1).strip()
            break

    # Example: "Clinical Safety"
    for line in all_lines:
        match = re.search(r"clinical safety:\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            parsed_data["Clinical Safety"] = match.group(1).strip()
            break

    # Example: "Clinical Discontinuation"
    for line in all_lines:
        match = re.search(r"clinical discontinuation:\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            parsed_data["Clinical Discontinuation"] = match.group(1).strip()
            break

    # Done extracting
    return parsed_data


def main():
    # 1) Load the Textract JSON from file
    json_filename = "output_01072025.json"
    with open(json_filename, "r", encoding="utf-8") as f:
        textract_json = json.load(f)

    # 2) Parse it to extract fields
    row_data = parse_textract(textract_json)

    # 3) Write a single-row CSV with our fields
    csv_output = "extracted_data_01072025.csv"
    with open(csv_output, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(row_data)

    print(f"Extraction complete! Saved to {csv_output}")
    print("Extracted fields:", row_data)


if __name__ == "__main__":
    main()

