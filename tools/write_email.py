"""
To be called when the user wants to write an effective (but also confidential) email of some abstract criteria.
"""
import json
from typing import List, Dict
from google import genai
import os
from dotenv import load_dotenv
from write_email_prompt import base_prompt

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def write_email(knowledge: List[str], constraints: List[str]):
    prompt = base_prompt
    
    prompt += """
- FACTS -"""

    if knowledge:
        for fact in knowledge:
            prompt += f"- {fact}"
    else:
        prompt += "- None\n"
        
    prompt += """
- DEMANDS -"""
    if constraints:
        for constraint in constraints:
            prompt += f"- {constraint}"
    else:
        prompt += "- None\n"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text

if __name__ == "__main__":
    print(write_email([
        "We are a business representative for a large AI company",
        "Our CEO has sent us an email asking how the outreach has been going",
        "CEO sent us following email: 'yo wsg g\n    hows the outreach goin. i bet its litty :fire:. lmk within 2 business days how it goin'",
    ], [
        "Must include metrics in answer to show improvement"
        "Response must be well written and make us look cool"
    ]))