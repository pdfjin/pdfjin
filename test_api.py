import requests
url1 = "https://pdfjin-api-d33mroeryq-uc.a.run.app/pricing"
url2 = "https://pdfjin-api-97530578628.us-central1.run.app/pricing"
try:
    print(f"Testing {url1}: {requests.get(url1).status_code}")
except Exception as e:
    print(f"Error {url1}: {e}")

try:
    print(f"Testing {url2}: {requests.get(url2).status_code}")
except Exception as e:
    print(f"Error {url2}: {e}")
