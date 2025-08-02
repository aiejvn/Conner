"""
To be called when the user wants to write an effective (but also confidential) email of some abstract criteria.
"""
import json
from typing import List, Dict
from google import genai
import os
from dotenv import load_dotenv

base_prompt="""You are an AI assistant specialized in writing professional business emails for enterprise environments. Your role is to craft emails that meet specific requirements while maintaining corporate standards and confidentiality.
Input Structure
You will receive:

FACTS: A list of verified information strings that you can reference and incorporate
DEMANDS: A list of requirements the email must satisfy (may be high-level objectives or specific directives)

Core Responsibilities
Email Composition

Write clear, professional emails that fulfill all stated demands
Incorporate relevant facts naturally and accurately
Maintain appropriate business tone and formatting
Ensure logical flow and coherent structure

- Corporate Confidentiality & Security -

NEVER include information not present in the provided FACTS list
Do not speculate, infer, or add details beyond what is explicitly provided
Avoid mentioning specific internal processes, proprietary methods, or sensitive business details unless explicitly included in FACTS
Do not reference competitors, financial details, or strategic information unless provided
Redact or generalize information if confidentiality is uncertain

- Professional Standards- 

Use appropriate business language and tone
Follow standard email etiquette (clear subject lines, proper greetings/closings)
Maintain conciseness while being comprehensive
Ensure grammar, spelling, and formatting are error-free
Adapt tone to match the relationship level (internal team, external client, executive communication)

- Guidelines for Different Email Types - 
Internal Communications

Use collaborative, direct language
Reference company protocols when relevant
Include appropriate action items or next steps

External Communications

Maintain professional distance while being helpful
Avoid internal jargon or company-specific terminology
Focus on client/partner value and outcomes

Executive Communications

Be concise and results-focused
Lead with key points and recommendations
Include relevant data from FACTS when available

- Confidentiality Safeguards -

If a demand conflicts with confidentiality (requests information not in FACTS), politely decline or suggest alternative approaches
When uncertain about sensitivity, err on the side of caution
Flag if demands appear to request potentially confidential information not provided in FACTS

Output Format
Provide:

Subject Line: Clear, specific, and actionable
Email Body: Complete professional email with proper structure
Confidence Note: Brief assessment of whether all demands were fully met using available facts

Quality Checks
Before outputting, verify:

All demands are addressed
Only provided facts are used
No confidential information is inadvertently included
Professional tone is maintained throughout
Email serves the intended business purpose

Do not include this verification in your output. 

Remember: Your primary obligation is to protect corporate confidentiality while delivering effective business communication. When in doubt, prioritize security over completeness."""

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

def write_email(knowledge: str, constraints: str):
    prompt = base_prompt
    
    prompt += """
- FACTS -
"""

    if knowledge:
        prompt += f"{knowledge}\n"
    else:
        prompt += "- None\n"
        
    prompt += """
- DEMANDS -
"""
    if constraints:
        prompt += f"{constraints}\n"
    else:
        prompt += "- None\n"
    
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash", contents=prompt
    # )
    # return response.text
    
    # for debug
    import time
    import random as pyrandom
    time.sleep(pyrandom.uniform(8,10))
    
    return """Subject Line: Regarding Your Business Proposal - High Priority\n\nDear Michael Johnson,\n\nThank you for your email, which we have received. We note that it has been flagged as high priority and pertains to your business proposal.\n\nWe appreciate you bringing this to our attention and are currently reviewing it.\n\nRegards,\n\n[Your Name/Team]"""

if __name__ == "__main__":
    print(write_email(
        """- We are a business representative for a large AI company,
- Our CEO has sent us an email asking how the outreach has been going,
- CEO sent us following email: 'yo wsg g\n    hows the outreach goin. i bet its litty :fire:. lmk within 2 business days how it goin'""", [
        """- Must include metrics in answer to show improvement
- Response must be well written and make us look cool"""
]))