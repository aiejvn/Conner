from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("Key not found")
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_API_KEY)

class Node(BaseModel):
    tool: str
    reason: str
    confidence: float

response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        # TODO: When v1 is done, fix this prompt. Lol.
        {
            "role": "system", 
            "content": 
"""You are a smart assistant with many tools at your disposal. 
Follow the user's commands as best as you can, and include a brief, one-sentence explaining your thinking, as well as a confidence value between 0 and 1 expressing how confident you are in your reasoning."""},
        {
            "role": "user",
            "content": """Given the following message, who is going to a science fair? 
            
            Alice and Bob are going to a science fair on Friday.""",
        },
    ],
    text_format=Node,
)

event = response.output_parsed
print(event)