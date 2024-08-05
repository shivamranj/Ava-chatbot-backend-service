import google.generativeai as genai
from app.config import API_KEY  

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_response(user_message: str) -> str:
    response = model.generate_content(user_message)
    return response.text