import json
from typing import List, Dict
from google import genai

class BasicAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def enforce_json_format(self, tool: str, reason: str, confidence: float) -> str:
        """Enforce strict JSON format for the agent's output."""
        if not (0 <= confidence <= 1):
            raise ValueError("Confidence must be a float between 0 and 1.")
        output = {
            "tool": tool,
            "reason": reason,
            "confidence": confidence,
        }
        return json.dumps(output)

    def process_conversation(self, conversation: List[Dict[str, str]]) -> Dict[str, str]:
        """Take in a conversation and append the agent's output."""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            conversation=conversation,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "response": str,
                    "confidence": float,
                },
            },
        )
        agent_output = {
            "type": "agent",
            "text": response.parsed["response"],
        }
        conversation.append(agent_output)
        return agent_output

    def call_browser_tool(self, query: str) -> str:
        """Simulate calling a browser tool to search for information."""
        tool_output = self.enforce_json_format(
            tool="browser",
            reason=f"Searching for information about '{query}'",
            confidence=0.95,
        )
        # Simulate browser tool output (replace with actual browser tool logic)
        print(f"Browser tool called with query: {query}")
        return tool_output

# Example usage:
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    if 'GEMINI_API_KEY' not in os.environ: raise KeyError('Gemini Key is missing...')
    agent = BasicAgent(api_key=os.environ['GEMINI_API_KEY'])

    # Example conversation
    conversation = [
        {"type": "system", "text": "You are a helpful assistant."},
        {"type": "user", "text": "What is the most popular cookie recipe?"},
    ]

    try:
        # Process conversation
        agent_response = agent.process_conversation(conversation)
        print("Agent Response:", agent_response)

        # Call browser tool
        browser_output = agent.call_browser_tool("popular cookie recipe")
        print("Browser Tool Output:", browser_output)
    except Exception as e:
        print(e)