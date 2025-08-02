import streamlit as st
from agent import Agent
import os
import json

# Initialize the agent
agent = Agent()

# Streamlit app title
st.title("Chat with Conner")

# Session state to store conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Create a container for the chat messages
chat_container = st.container()
        
# Create a form for the text input (this handles the Enter key behavior)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "What would you like Conner to do?",
        placeholder="Analyze the stock market...",
        key="user_input"
    )
    
    # Submit button (optional - form submits on Enter as well)
    submit_button = st.form_submit_button("Send")

# Process the input when form is submitted
if submit_button and user_input.strip():
    print(user_input.strip())
    response_node = agent.get_response(user_input.strip())

    # Store the response in session state
    st.session_state.last_response = response_node.reason
    st.session_state.last_node_uuid = response_node.uuid

# Display the response if available
if "last_response" in st.session_state:
    st.text_area(
        "Response:",
        value=st.session_state.last_response,
        height=80,
        disabled=True,
        key="conner_response_final"
    )

# Toggle to view nodes

# TODO: Come back here once tools are done. Then test on complex MCP tasks.
debug=True
view_nodes = st.checkbox("View Nodes")
if view_nodes and (debug or "last_node_uuid" in st.session_state):
    # current_uuid = st.session_state.last_node_uuid
    current_uuid = "test1"
    nodes = []

    # Read nodes recursively
    while current_uuid != "root":
        node_path = f"./nodes/{current_uuid}.json"
        # print(node_path)
        if os.path.exists(node_path):
            with open(node_path, "r") as f:
                node_data = json.load(f)
                nodes.append(node_data)
                current_uuid = node_data.get("parent_uuid", "root")
        else:
            break

    # Display nodes as a tree-style flowgraph
    st.markdown("### Flowgraph of Nodes")
    for i, node in enumerate(reversed(nodes)): # Reverse order
        st.markdown(f"**Node {i+1}:**")
        st.markdown(f"- **Tool Used:** {node['tool']}")
        st.markdown(f"- **Reason:** {node['reason']}")
        st.markdown(f"- **Confidence:** {node['confidence']}")
        
        reset_button_i = st.button("Fix Thinking", key=f"button_node_{i+1}")
        st.markdown("---")
        
        

# Instructions
st.markdown("---")
st.markdown("""
**Instructions:**
- Tell Conner to do a task, and he will do it!
- Monitor Conner's thought process to correct him if things go wrong
""")