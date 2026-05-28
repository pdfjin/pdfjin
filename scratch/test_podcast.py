import requests
import io

pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n4 0 obj\n<< /Length 53 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000289 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n393\n%%EOF"

url = "https://pdfjin-api-97530578628.us-central1.run.app/ai-pdf-podcast"
files = {'files': ('dummy.pdf', pdf_content, 'application/pdf')}
try:
    print("Sending request...")
    response = requests.post(url, files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Success. Audio length: {len(response.content)} bytes")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
