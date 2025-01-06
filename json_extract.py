import pandas as pd

# Load the existing Excel file
input_excel = 'textract_results.xlsx'

# Read the Excel file into a DataFrame
df = pd.read_excel(input_excel)

# Select only the first two columns
filtered_df = df[['Text', 'Confidence']]

# Save the refined data back to a new Excel file
output_excel = 'filtered_textract_results_VO.xlsx'
filtered_df.to_excel(output_excel, index=False)

print(f"Filtered data saved to {output_excel}")

