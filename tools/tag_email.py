"""
To be called when the user wants to 'tag' all emails of some abstract criteria.
"""
import json
from typing import List, Dict
from google import genai
import os
from dotenv import load_dotenv
from tag_email_prompt import base_prompt

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def tag_emails(emails: List[Dict], rules: List[str]) -> List[Dict]:
    tagged_emails = []

    for email in emails:
        prompt = base_prompt
        prompt += f"""
EMAIL: {email}
TAGS:
"""
        if rules:
            for rule in rules:
                prompt += f"- {rule}\n"
        else:
            prompt += "- None"       
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        tag = response.text
        email["tags"] += [tag.strip()]
        tagged_emails.append(email)

    return tagged_emails

if __name__ == '__main__':
    # Load example emails from ./emails folder
    email_files = [f for f in os.listdir('./emails') if f.endswith('.json')]
    emails = []
    for file in email_files:
        with open(f'./emails/{file}', 'r') as f:
            emails.append(json.load(f))

    # Define tagging criteria
    criteria = ["High Priority - If an email is highly urgent and/or related to work", "To Respond Later - If an email is low priority AND it would be okay to ignore the email for now"]

    # Tag emails
    tagged_emails = tag_emails(emails, criteria)

    # Save modified emails to ./modified_emails folder
    os.makedirs('./modified_emails', exist_ok=True)
    for i, email in enumerate(tagged_emails):
        with open(f'./modified_emails/email{i+1}.json', 'w') as f:
            json.dump(email, f, indent=4)

    print("Emails have been tagged with new criteria and saved to ./modified_emails.")
