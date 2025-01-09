#!/usr/bin/env python3

import json

def main():
    with open("output_01072025.json", "r") as f:
        data = json.load(f)
    
    parsed_data = {
        "Black Box Warning": "N",  # default no
        "Compound": "",
        "Approval": "",
        "Study": "",
        "N for each study": "",
        "Dose for each study": "",
        "Clinical Efficacy": "",
        "Clinical Safety": "",
        "Clinical Discontinuation": ""
    }

    # Debug: print out lines
    all_lines = []
    for block in data.get('Blocks', []):
        if block.get('BlockType') == "LINE":
            text = block.get('Text', '')
            all_lines.append(text)
    
    print("\nDEBUG: All recognized lines from Textract:\n")
    for line in all_lines:
        print(line)
    print("\n----------\n")

    # Now let's do some example matching
    for line in all_lines:
        lower_line = line.lower()

        # Check for "Initial U.S. Approval"
        if "initial u.s. approval" in lower_line:
            # e.g., "Initial U.S. Approval: 2014"
            # parse out the year or date
            parts = line.split(":")
            if len(parts) > 1:
                parsed_data["Approval"] = parts[1].strip()

        # Check for the brand name
        if "keytruda" in lower_line and "pembrolizumab" in lower_line:
            parsed_data["Compound"] = "KEYTRUDA (pembrolizumab)"

        # Check for a known heading that might signal a black box warning
        # E.g., "WARNINGS AND PRECAUTIONS" could imply or not. 
        # Real black-box text might appear as "WARNING: This drug may..."
        if "warning" in lower_line:
            parsed_data["Black Box Warning"] = "Y"
            # Optionally store the actual text:
            # parsed_data["Black Box Warning"] = f"Y - Found text: {line}"

    # Print or write to CSV
    print("Parsed Data:\n", parsed_data)

if __name__ == "__main__":
    main()

