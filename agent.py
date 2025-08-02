from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import uuid
import json

from time import sleep


class Node(BaseModel):
    tool: str
    reason: str
    confidence: float
    uuid: str
    parent_uuid: str

class Agent:
    def __init__(self):
        load_dotenv()
        if 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("Key not found")
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.conversation = [
        # TODO: When v1 is done, fix this prompt. Lol.
        {
            "role": "system", 
            "content": 
"""You are a smart assistant with many tools at your disposal. 
Follow the user's commands as best as you can, and include a brief, one-sentence explaining your thinking, as well as a confidence value between 0 and 1 expressing how confident you are in your reasoning.
If no tool is needed, simply return N/A as tool used.
If your confidence is >=0.9, include an answer alongside your reasoning.
Otherwise, describe what information you have and what information you are looking for, as if handing off the problem to someone else.
Make sure to consider all reasonable routes when deciding output. Only use specific tools when they seem reasonable."""}
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
        response = self.client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=self.conversation,
            text_format=Node
        )

        # Generate UUID for the new node
        node_uuid = str(uuid.uuid4())

        # Create Node instance
        node = Node(
            tool=response.output_parsed.tool,
            reason=response.output_parsed.reason,
            confidence=response.output_parsed.confidence,
            uuid=node_uuid,
            parent_uuid=parent_uuid
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
        while True:
            cur_node = self.get_response_one(input)
            if cur_node.confidence >= 0.9:
                return cur_node
            else:
                print("Conner needs another node...")
                sleep(1) # To avoid overloading our API key

if __name__ == '__main__':
    test_agent = Agent()
    test_rsp = test_agent.get_response("""Given the following message, who is going to a science fair? 
            
            Alice and Bob are going to a science fair on Friday.""")
    print(test_rsp)