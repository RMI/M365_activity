import os
import openai
from dotenv import load_dotenv


load_dotenv('cred.env')


test = os.getenv('OPENAI_API_KEY')

openai.api_key = os.getenv("OPENAI_API_KEY")


openai.Model.list()



response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[],
  temperature=0.5,
  max_tokens=256
)