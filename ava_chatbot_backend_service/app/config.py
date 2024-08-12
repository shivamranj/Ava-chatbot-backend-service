from dotenv import load_dotenv
import os

load_dotenv()


REDIS_URL = os.getenv('REDIS_URL') 
API_KEY = os.getenv('API_KEY') 

