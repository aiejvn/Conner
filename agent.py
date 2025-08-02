from openai import OpenAI
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
from time import sleep
from typing import List, Dict
import os
import uuid
import json

from agent_prompt import base_prompt
from tools.search_emails import search_emails
from tools.tag_email import tag_emails
from tools.write_email import write_email

debug_read_reason = "I'll search for emails from external sources to identify the most important sender."
debug_write_reason = "Michael Johnson's email is high priority and involves a significant business proposal."

def load_emails() -> List[Dict]:
    email_files = [f for f in os.listdir('./emails') if f.endswith('.json')]
    emails = []
    for file in email_files:
        with open(f'./emails/{file}', 'r') as f:
            email_data = json.load(f)
            email_data['id'] = file.split('.')[0]  # Add ID based on filename
            emails.append(email_data)
    return emails

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

class Node(BaseModel):
    tool: str
    reason: str
    confidence: float
    uuid: str
    parent_uuid: str
    progress: float
    tool_result: str
    
    def get(self, trait: str, default: str):
        """
        Implements dict.get(val, default) for Node attributes.
        Returns the value of the specified trait if it exists, otherwise returns the default value.
        """
        return getattr(self, trait, default)
        


class Agent:
    def __init__(self):
        load_dotenv()
        if 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("Key not found")
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.conversation = [
            {
                "role": "system", 
                "content": base_prompt
            }
        ]
        self.conv_nodes = []
        
    def get_response_one(self, input: str):
        """
        Get a response from the agent for a query.
        In: text
        Out: Node JSON
        """
        parent_uuid = self.conv_nodes[-1].get("uuid", "root") if self.conv_nodes else "root"
        self.conversation.append({
            "role": "user",
            "content": input
        })
        # response = self.client.responses.parse(
        #     model="gpt-4o-2024-08-06",
        #     input=self.conversation,
        #     text_format=Node
        # )
        
        # last_response = ""
        # emails = load_emails()
        # match response.output_parsed.tool:
        #     case 'search_emails':
        #         print("Searching emails...")
        #         print(response.output_parsed.reason)
        #         # gemini_response = client.models.generate_content(
        #         #     model="gemini-2.5-flash",
        #         #     contents=f"Translate the following reasoning into a set of criteria to apply to a search. Output must be in point form. {response.output_parsed.reason}"
        #         # )
        #         # print(gemini_response.text)
        #         # last_response = search_emails(emails, gemini_response.text)
        #         last_response = search_emails(emails, "debug")
        #     case 'tag_emails':
        #         print("Tagging emails...")
        #         # gemini_response = client.models.generate_content(
        #         #     model="gemini-2.5-flash",
        #         #     contents=f"Translate the following reasoning into a set of tags and the criteria for each tag to apply. Output must be in point form (e.g. 'Delegate - all internal emails about unimportant tasks'). {response.output_parsed.reason}"
        #         # )
        #         # print(gemini_response.text)
        #         # last_response = tag_emails(emails, gemini_response.text)
        #         last_response = tag_emails(emails, "debug")
        #     case 'write_email':
        #         print("Writing an email...")
        #         # knowledge = client.models.generate_content(
        #         #     model="gemini-2.5-flash",
        #         #     contents=f"Extract all known facts from the following reasoning. Output must be in point form.\n{response.output_parsed.reason}"
        #         # )
        #         # constraints = client.models.generate_content(
        #         #     model="gemini-2.5-flash",
        #         #     contents=f"Extract all restrictions on our solution from the following reasoning. Output must be in point form.\n{response.output_parsed.reason}"
        #         # )
        #         # print(knowledge.text, constraints.text)
        #         # last_response = write_email(knowledge.text, constraints.text)
        #         last_response = write_email("debug", "debug")
        #     case _:
        #         print(f"Tried using tool: {response.output_parsed.tool}")
        #         last_response = response.output_parsed.reason

        # Deterministic flow replacing OpenAI calls, dor debug pruposes
        if len(self.conv_nodes) == 0:
            tool = 'search_emails'
            reason = debug_read_reason
            confidence = 0.8
            tool_result = search_emails(load_emails(), "debug")
        elif len(self.conv_nodes) == 1:
            tool = 'search_emails'
            reason = debug_read_reason
            confidence = 0.9
            tool_result = search_emails(load_emails(), "debug")
        else:
            tool = 'write_email'
            reason = debug_write_reason
            confidence = 1.0
            tool_result = write_email("debug", "debug")

        # Generate UUID for the new node
        node_uuid = str(uuid.uuid4())

        # Create Node instance
        node = Node(
            tool=tool,
            reason=reason,
            confidence=confidence,
            uuid=node_uuid,
            parent_uuid=parent_uuid,
            progress=confidence,
            tool_result=tool_result
        )
        self.conv_nodes.append(node)

        # Save Node as JSON to ./nodes
        with open(f"./nodes/{node_uuid}.json", "w") as f:
            json.dump(node.dict(), f, indent=4)

        return node
    
    def get_response(self, input:str):
        """
        Calls get_response_one until confidence exceeds threshold of 0.9.
        Then returns final result, as a node.
        """
        last_response = input
        while True:
            cur_node = self.get_response_one(last_response)
            # print(cur_node.tool)
            
            if cur_node.progress >= 1 or cur_node.tool == 'write_email':
                print("Done!")
                return cur_node
            else: last_response = cur_node.tool_result
            

if __name__ == '__main__':
    test_agent = Agent()
    # test_rsp = test_agent.get_response("""Given the following message, who is going to a science fair? 
            
    #         Alice and Bob are going to a science fair on Friday.""")
    # Note: tag is too slow ATM. We may need another tool.
    test_rsp = test_agent.get_response("""First, search all emails for ones sent by external sources.
Then, write a response email to the most important external sender, asking for more details on what they are talking about.""")
    print(test_rsp)