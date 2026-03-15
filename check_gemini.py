import os
import google.generativeai as genai

# Use the same key as in app.py for testing
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAN270KrgKkQTtllZGpN-cj1fwFx70Lkv8")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Hello, system check. Are you working?")
    print("Gemini API Test result:")
    print(response.text)
    
    print("\nListing available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Gemini API Test failed: {e}")
