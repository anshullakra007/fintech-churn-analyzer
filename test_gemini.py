import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hi")
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:", str(e))
