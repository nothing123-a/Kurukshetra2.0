import os
import pandas as pd
from pdf_bw_report import generate_black_and_white_pdf

df = pd.read_csv('uploads/district_health.csv')
print(f"Loaded district_health.csv: {df.shape[0]} rows, {df.shape[1]} cols")

out_pdf = 'uploads/test_narayan_audit_validated.pdf'
generate_black_and_white_pdf(df, out_pdf, 'district_health.csv', 'Narayan')

print("PDF successfully generated:", out_pdf)
print("File size:", os.path.getsize(out_pdf), "bytes")

# Inspect PDF internal objects
with open(out_pdf, 'rb') as f:
    pdf_bytes = f.read()

import zlib, re

# Find each object with a stream
objects = re.findall(rb'<<.*?>>\s*stream[\r\n]+(.*?)[\r\n]+endstream', pdf_bytes, re.DOTALL)
print(f"Total streams found in PDF: {len(objects)}")

all_text = ""
for i, s in enumerate(objects):
    try:
        dec = zlib.decompress(s).decode('latin1', errors='ignore')
        all_text += dec + " "
    except Exception:
        pass

print(f"Total decompressed text length: {len(all_text)}")

# Check key dataset indicators in the decompressed text
print("\nVerifying real dataset content inside PDF:")
indicators = [
    "Dataset Records Inspection Table",
    "Representative data records",
    "Executive Summary",
    "Descriptive Statistics",
    "Quantitative Visualizations",
    "Statistical Outliers",
    "Narayan"
]

for ind in indicators:
    found = ind.lower() in all_text.lower()
    print(f"  [{'PASS' if found else 'FAIL'}] '{ind}': {found}")

# Check actual district names from the dataset
districts = list(df['District_Name'].head(8))
print(f"\nVerifying actual district rows from dataset inside PDF:")
found_districts = []
for d in districts:
    if str(d).lower() in all_text.lower():
        found_districts.append(d)
        print(f"  [PASS] Found district: '{d}'")

print(f"Total districts verified in PDF table: {len(found_districts)} / {len(districts)}")
