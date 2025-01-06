import json
import csv

# Load JSON data
with open('textract_output.json', 'r') as file:
    data = json.load(file)

# Extract words
words = [
    block['Text']
    for block in data['Blocks']
    if block['BlockType'] == 'WORD'
]

# Save to CSV
with open('textract_words.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Words"])
    for word in words:
        writer.writerow([word])

