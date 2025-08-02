"""
To be called when the user wants to search for specific emails of some abstract criteria
"""
import json
from typing import List, Dict
from google import genai
import os
import ast
from dotenv import load_dotenv

base_prompt="""You are an AI assistant specialized in searching for relevant professional business emails for enterprise environments. Your role is to find and return all emails that meet specific requirements while maintaining corporate standards and confidentiality.
Input Structure
You will receive:

EMAILS: List of emails you must search
CRITERIA: List of rules all returned emails must meet

Output Format: 
Provide a list of all emails that apply, structued as '[email_id1.json, email_id2.json, ..., email_id_n.json]', where the email_id's are the ID numbers of the returned emails.
Only include this list in your answer and no other text."""

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def search_emails(emails: List[Dict], criteria: str) -> List[str]:
    prompt = base_prompt + "\n\nEMAILS:\n"

    if emails:
        for email in emails:
            prompt += f"- {str(email)}\n"
    else:
        prompt += "- None"    
        
    prompt += "\n\nCRITERIA:\n"
    if criteria:
            prompt += f"{criteria}\n"
    else:
        prompt += "- None\n"       
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    # Manually parse the output string list into a Python list
    try:
        email_ids = response.text.strip("[]").replace(" ", "").split(",")
        email_ids = [email_id.strip("'") for email_id in email_ids]
    except Exception as e:
        print("Could not parse the response into a list:")
        print(response.text)
        print(f"Error: {e}")
        return ""

    # Collect the contents of each email into one string
    collected_emails = ""
    for email_id in email_ids:
        email_path = f"./emails/{email_id}"
        if os.path.exists(email_path):
            with open(email_path, "r") as f:
                email_data = json.load(f)
                collected_emails += json.dumps(email_data, indent=4) + "\n"
        else:
            print(f"Email file {email_id} not found.")

    return collected_emails
    
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
    criteria = "- Look for all emails related to the Q3 marketing campaign."

    # Search for emails matching the criteria
    relevant_emails = search_emails(emails, criteria)

    # Output the IDs of emails that match the criteria
    print("Relevant emails:")
    print(relevant_emails)
