#!/usr/bin/env python3

import json
import csv
import re

# The columns you want in your final CSV
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

def load_textract_json(filename: str):
    """Load the Textract JSON output into a Python dict."""
    with open(filename, "r") as f:
        data = json.load(f)
    return data

def group_text_by_page(textract_data):
    """
    Return a dict of page -> list of lines (strings).
    Also keep track of the block metadata if needed.
    """
    pages = {}
    for block in textract_data.get('Blocks', []):
        block_type = block.get('BlockType')
        
        # We only care about lines for a simple approach.
        if block_type == "LINE":
            page_number = block.get('Page', 1)
            text = block.get('Text', "")
            
            if page_number not in pages:
                pages[page_number] = []
            pages[page_number].append(text)
    
    return pages

def extract_top_of_first_page_data(lines_page_1):
    """
    Use textual heuristics or regex to find:
      - Black Box Warning
      - Compound name
      - Approval date
    from the lines on page 1.
    """

    black_box_warning = "N"  # default to No
    black_box_warning_text = ""

    compound = ""
    approval_date = ""
    
    # Example heuristics:
    for line in lines_page_1:
        lower_line = line.lower()
        
        # 1) Black Box Warning
        if "black box warning" in lower_line:
            black_box_warning = "Y"
            black_box_warning_text = line  # maybe store the full line or subsequent lines

        # 2) Compound name (brand + generic)
        # Let’s assume we see something like "Compound: Aspirin (acetylsalicylic acid)"
        # This is obviously just an example; your doc might differ.
        if "compound:" in lower_line:
            # Grab everything after 'Compound:'
            # e.g., "Compound: Aspirin (acetylsalicylic acid)"
            match = re.search(r"compound:\s*(.+)", lower_line)
            if match:
                compound = match.group(1)
                
        # 3) Approval date
        # Suppose the doc has "Approval Date: December 19, 2020" on page 1
        # This is a simplistic pattern. Real docs might require more robust logic:
        if "approval date:" in lower_line:
            match = re.search(r"approval date:\s*(.+)", lower_line)
            if match:
                approval_date = match.group(1)
    
    # Combine black_box_warning Y/N with optional text
    if black_box_warning == "Y" and black_box_warning_text:
        black_box_warning = f"Y - {black_box_warning_text}"
    
    return black_box_warning, compound, approval_date

def extract_section_14_data(all_pages):
    """
    For fields that appear in "section 14":
      - Study number
      - N for each study
      - Dose for each study
      - Clinical Efficacy
      - Clinical Safety
      - Clinical Discontinuation
    
    We must figure out which *page(s)* contain Section 14. 
    Maybe we search all pages for 'SECTION 14' or '14 CLINICAL STUDIES', 
    then parse from there on. We’ll do a simplistic example.
    """

    study_number = ""
    n_each_study = ""
    dose_each_study = ""
    clinical_efficacy = ""
    clinical_safety = ""
    clinical_discontinuation = ""

    # 1) Identify which pages belong to "Section 14"
    section_14_pages = []
    for page_number, lines in all_pages.items():
        # if we see "14 CLINICAL STUDIES" or something like that
        # add that page to our list
        text_join = " ".join(lines).lower()
        if "section 14" in text_join or "14 clinical" in text_join:
            section_14_pages.append(page_number)
    
    # 2) Gather text in those pages
    # For simplicity, we’ll combine them all into one big text chunk
    section_14_text = []
    for p in section_14_pages:
        section_14_text.extend(all_pages[p])
    combined_14_text = "\n".join(section_14_text).lower()
    
    # 3) Use your heuristics to find each piece of data
    # Example: "Study: 12345" => study_number
    match_study = re.search(r"study[:\s]+(\S+)", combined_14_text)
    if match_study:
        study_number = match_study.group(1)
    
    # Example: "N= 456" => n_each_study
    match_n = re.search(r"\bn\s*=\s*(\d+)", combined_14_text)
    if match_n:
        n_each_study = match_n.group(1)
    
    # Example: "Dose: 50 mg" => dose_each_study
    match_dose = re.search(r"dose[:\s]+([\w\s]+mg)", combined_14_text)
    if match_dose:
        dose_each_study = match_dose.group(1)
    
    # Clinical Efficacy => maybe we just find a line after "Clinical Efficacy" heading
    # This is obviously naive. In real doc, you'd parse paragraphs or tables carefully.
    match_efficacy = re.search(r"clinical efficacy[:\s]+(.+?)(?=clinical safety|$)", combined_14_text, flags=re.DOTALL)
    if match_efficacy:
        clinical_efficacy = match_efficacy.group(1).strip()

    # Clinical Safety
    match_safety = re.search(r"clinical safety[:\s]+(.+?)(?=clinical discontinuation|$)", combined_14_text, flags=re.DOTALL)
    if match_safety:
        clinical_safety = match_safety.group(1).strip()

    # Clinical Discontinuation
    match_disc = re.search(r"clinical discontinuation[:\s]+(.+)", combined_14_text, flags=re.DOTALL)
    if match_disc:
        clinical_discontinuation = match_disc.group(1).strip()

    return (study_number, n_each_study, dose_each_study,
            clinical_efficacy, clinical_safety, clinical_discontinuation)

def parse_textract_response(textract_data):
    """
    Overall function:
      1) Group lines by page.
      2) Extract top-of-first-page fields.
      3) Extract section 14 fields.
      4) Return a dict that matches FIELDNAMES.
    """

    # Group text by page
    pages = group_text_by_page(textract_data)
    
    # Default dictionary
    parsed_data = {
        "Black Box Warning": "",
        "Compound": "",
        "Approval": "",
        "Study": "",
        "N for each study": "",
        "Dose for each study": "",
        "Clinical Efficacy": "",
        "Clinical Safety": "",
        "Clinical Discontinuation": ""
    }
    
    # 1) Extract top-of-page-1 data (if it exists)
    page_1_lines = pages.get(1, [])
    (bb_warn, compound, approval_date) = extract_top_of_first_page_data(page_1_lines)
    
    parsed_data["Black Box Warning"] = bb_warn
    parsed_data["Compound"] = compound
    parsed_data["Approval"] = approval_date
    
    # 2) Extract section 14 data
    (study_number,
     n_each_study,
     dose_each_study,
     clin_eff,
     clin_safe,
     clin_disc) = extract_section_14_data(pages)

    parsed_data["Study"] = study_number
    parsed_data["N for each study"] = n_each_study
    parsed_data["Dose for each study"] = dose_each_study
    parsed_data["Clinical Efficacy"] = clin_eff
    parsed_data["Clinical Safety"] = clin_safe
    parsed_data["Clinical Discontinuation"] = clin_disc
    
    return parsed_data

def main():
    # 1) Load the Textract JSON
    textract_data = load_textract_json("output.json")
    
    # 2) Parse
    row_data = parse_textract_response(textract_data)
    
    # 3) Write to CSV
    csv_filename = "extracted_data.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(row_data)
    
    print(f"Data extracted and written to {csv_filename}")

if __name__ == "__main__":
    main()

