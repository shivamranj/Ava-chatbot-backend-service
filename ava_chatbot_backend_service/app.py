from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

# API_KEY = 'AIzaSyCBkXVZRbtBg5f7NaAl299qCSWntdTzEHs'

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

def generate_response(user_message: str) -> str:
    response = model.generate_content(user_message)
    return response.text

@app.post("/chat")
async def chat(message: Message):
    user_message = message.message
    bot_reply = generate_response(user_message)
    return {"reply": bot_reply}

def main():
    print("FastAPI application is running...")


