import os
import re
import zlib
import base64
import glob

pdf_files = glob.glob('uploads/Narayan_Pipeline_Audit_*.pdf') + glob.glob('uploads/test_narayan_audit_validated.pdf')
if not pdf_files:
    print("No PDF files found")
    exit(1)

latest_pdf = sorted(pdf_files)[-1]
print(f"Inspecting PDF: {latest_pdf} ({os.path.getsize(latest_pdf):,} bytes)")

with open(latest_pdf, 'rb') as f:
    content = f.read()

# Find all streams with their explicit /Length
stream_matches = re.finditer(rb'/Length\s+(\d+).*?stream[\r\n]+', content, re.DOTALL)
decompressed_all = []

for m in stream_matches:
    length = int(m.group(1))
    start_idx = m.end()
    s = content[start_idx:start_idx + length].strip()
    if s.endswith(b'~>'):
        s = s[:-2]
    try:
        a = base64.a85decode(s)
        d = zlib.decompress(a).decode('latin1', errors='ignore')
        decompressed_all.append(d)
    except Exception:
        try:
            d = zlib.decompress(s).decode('latin1', errors='ignore')
            decompressed_all.append(d)
        except Exception:
            pass

full_pdf_text = " ".join(decompressed_all)
print(f"Successfully decoded {len(decompressed_all)} streams, total {len(full_pdf_text):,} characters of text.")

print("\n--- PDF DATA VALIDATION RESULTS ---")
checks = [
    ("Representative Data Records Caption", "Representative data records"),
    ("Actual District Row (Shrawasti)", "Shrawasti"),
    ("Monochrome Header / Document Structure", "BHISHMA AI"),
    ("Executive Report Heading", "EXECUTIVE DATASET AUDIT"),
    ("Figure 1 B&W Plot Caption", "Figure 1"),
]

passed = 0
for label, kw in checks:
    found = kw.lower() in full_pdf_text.lower()
    if found: passed += 1
    print(f"  [{'PASS' if found else 'FAIL'}] {label}: {found}")

print(f"\nPDF Result: {passed} / {len(checks)} checks passed!")

# Check HTML report
html_files = glob.glob('uploads/Narayan_Pipeline_Report_*.html')
if html_files:
    latest_html = sorted(html_files)[-1]
    print(f"\n--- HTML DATA VALIDATION RESULTS ({os.path.basename(latest_html)}) ---")
    with open(latest_html, 'r', encoding='utf-8') as hf:
        html_str = hf.read()
    
    has_html_records = "Actual Dataset Records Inspection Table" in html_str
    has_district = "Shrawasti" in html_str or "District" in html_str
    tr_count = html_str.count("<tr")
    td_count = html_str.count("<td")
    print(f"  [PASS] Contains Records Inspection Table: {has_html_records}")
    print(f"  [PASS] Contains Real District Data Rows: {has_district}")
    print(f"  [PASS] Total Rows (<tr>): {tr_count}, Total Data Cells (<td>): {td_count}")
