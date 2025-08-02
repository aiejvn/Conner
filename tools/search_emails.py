"""
To be called when the user wants to search for specific emails of some abstract criteria
"""
import json
from typing import List, Dict
from google import genai
import os
from dotenv import load_dotenv
from search_email_prompt import base_prompt

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def search_emails(emails: List[Dict], criteria: List[str]) -> List[str]:
    relevant_emails = []
    prompt = base_prompt + "\n\nEMAILS:\n"

    if emails:
        for email in emails:
            prompt += f"- {str(email)}\n"
    else:
        prompt += "- None"    
        
    prompt += "\n\nCRITERIA:\n"
    if criteria:
        for rule in criteria:
            prompt += f"- {rule}\n"
    else:
        prompt += "- None"       
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text # List enough. json.loads refuses to parse this.
    
if __name__ == '__main__':
    # Load example emails from ./emails folder
    email_files = [f for f in os.listdir('./emails') if f.endswith('.json')]
    emails = []
    for file in email_files:
        with open(f'./emails/{file}', 'r') as f:
            email_data = json.load(f)
            email_data['id'] = file.split('.')[0]  # Add ID based on filename
            emails.append(email_data)

    # Define criteria for emails that can be reasonably deleted
    criteria = [
        "Look for all emails related to the Q3 marketing campaign."
    ]

    # Search for emails matching the criteria
    relevant_emails = search_emails(emails, criteria)

    # Output the IDs of emails that match the criteria
    print("Relevant emails:")
    print(relevant_emails)
