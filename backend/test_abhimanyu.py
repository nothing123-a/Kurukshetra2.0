import requests
import json
import sys

def safe_print(text):
    sys.stdout.write(str(text).encode('ascii', 'replace').decode('ascii') + '\n')
    sys.stdout.flush()

base = 'http://127.0.0.1:8000'

safe_print("=== 1. Testing Abhimanyu Descriptive Dataset Q&A (Groq) ===")
q1 = "Analyze the healthcare indicators in this dataset and identify the top anomalous districts with statistical evidence."
r1 = requests.post(f"{base}/api/groq/chat", json={"message": q1}).json()
safe_print(f"Success: {r1.get('success')}")
safe_print(f"Agent Name: {r1.get('agent_name')}")
safe_print(f"Model Used: {r1.get('model')}")
safe_print("Response Snippet:")
safe_print(r1.get("response", "")[:350])
safe_print("...")

safe_print("\n=== 2. Testing Graph & Visualization Generation ===")
q2 = "Show graph and visualize the divergence in infant mortality and healthcare capacity as per my problem statement."
r2 = requests.post(f"{base}/api/groq/chat", json={"message": q2}).json()
safe_print(f"Has Chart: {bool(r2.get('chart'))}")
if r2.get("chart"):
    safe_print(f"Chart Title: {r2['chart'].get('title')}")
    safe_print(f"Chart Filename: {r2['chart'].get('filename')}")
    safe_print(f"Chart Download URL: {r2['chart'].get('download_url')}")
    safe_print(f"Chart Base64 Present: {len(r2['chart'].get('base64', '')) > 100}")

safe_print("\n=== 3. Testing Detailed Black & White PDF Report with Borders and Graph ===")
q3 = "Generate a detailed black and white PDF report summary of this dataset with borders and graph."
r3 = requests.post(f"{base}/api/groq/chat", json={"message": q3}).json()
safe_print(f"Has Report: {bool(r3.get('report'))}")
if r3.get("report"):
    rep = r3["report"]
    safe_print(f"Report Filename: {rep.get('filename')}")
    safe_print(f"Report Download URL: {rep.get('download_url')}")
    safe_print(f"Theme: {rep.get('theme')}")
    
    # Download and validate the PDF file
    pdf_res = requests.get(f"{base}{rep['download_url']}")
    safe_print(f"HTTP Status of PDF: {pdf_res.status_code}")
    safe_print(f"Size in bytes: {len(pdf_res.content)}")
    safe_print(f"Valid PDF Header (%PDF): {pdf_res.content[:4] == b'%PDF'}")
    
    with open("test_final_bw_validated.pdf", "wb") as f:
        f.write(pdf_res.content)
    safe_print("Saved and verified PDF: test_final_bw_validated.pdf")
