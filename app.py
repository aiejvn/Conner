import streamlit as st
from agent import Agent
import os
import json

# Initialize the agent
agent = Agent()

# Streamlit app title
st.title("Admin with Conner")
        
# Instructions
st.markdown("---")
st.markdown("""
**Instructions:**
- Tell Conner to do a task, and he will do it!
- Monitor Conner's thought process to correct him if things go wrong
""")

# Session state to store conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Initialize feedback states
if "show_feedback_form" not in st.session_state:
    st.session_state.show_feedback_form = {}

# Create a container for the chat messages
chat_container = st.container()
        
# Create a form for the text input (this handles the Enter key behavior)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "What would you like Conner to do?",
        placeholder="Find all important meetings in my emails...",
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
    st.session_state.tool_result = response_node.tool_result
    st.session_state.last_node_uuid = response_node.uuid

# Display the response if available
if "last_response" in st.session_state:
    st.text_area(
        "Tool Output:",
        value=st.session_state.tool_result,
        height=None,  # Auto-scale height
        disabled=True,
        key="conner_output_final"
    )
    st.text_area(
        "Reasoning:",
        value=st.session_state.last_response,
        height=None,  # Auto-scale height
        disabled=True,
        key="conner_response_final"
    )

# Toggle to view nodes
view_nodes = st.checkbox("View Nodes")
if view_nodes and "last_node_uuid" in st.session_state:
    current_uuid = st.session_state.last_node_uuid
    nodes = []

    # Read nodes recursively
    while current_uuid != "root":
        node_path = f"./nodes/{current_uuid}.json"
        if os.path.exists(node_path):
            with open(node_path, "r") as f:
                try:
                    node_data = json.load(f)
                    nodes.append(node_data)
                    current_uuid = node_data.get("parent_uuid", "root")
                except json.JSONDecodeError:
                    st.error(f"Error reading node file: {node_path}")
                    break
        else:
            st.warning(f"Node file not found: {node_path}")
            break

    # Display nodes as a tree-style flowgraph
    if nodes:  # Only display if we have nodes
        st.markdown("### Flowgraph of Nodes")
        for i, node in enumerate(reversed(nodes)): # Reverse order
            st.markdown(f"**Node {i+1}:**")
            st.markdown(f"- **Tool Used:** {node.get('tool', 'N/A')}")
            
            # Display the output or result of the tool used
            tool_result = node.get('tool_result', '')
            if node.get('tool') == 'search_emails':
                st.text_area(
                    "Tool Output:",
                    value=tool_result,
                    height=None,
                    disabled=True,
                    key=f"tool_output_{i+1}"
                )
            elif node.get('tool') == 'write_email':
                st.text_area(
                    "Tool Output:",
                    value=tool_result,
                    height=None,
                    disabled=True,
                    key=f"tool_output_{i+1}"
                )
            elif node.get('tool') == 'tag_emails':
                try:
                    tagged_ids = json.loads(tool_result)
                    st.text_area(
                        "Tagged Email IDs:",
                        value="\n".join(tagged_ids),
                        height=None,
                        disabled=True,
                        key=f"tagged_ids_{i+1}"
                    )
                except json.JSONDecodeError:
                    st.error("Invalid JSON in tagged emails")

            st.text_area(
                "Reason:",
                value=node.get('reason', ''),
                height=None,
                disabled=True,
                key=f"reason_{i+1}"
            )
            st.text_area(
                "Confidence:",
                value=str(node.get('confidence', 0)),
                height=None,
                disabled=True,
                key=f"confidence_{i+1}"
            )
            
            # Fixed button logic - moved outside of form
            button_key = f"button_node_{i+1}"
            form_key = f"fix_form_{i+1}"
            
            # Check if this node's feedback form should be shown
            show_form = st.session_state.show_feedback_form.get(button_key, False)
            
            # Fix Thinking button
            if st.button("Fix Thinking", key=button_key):
                # Toggle the form visibility for this specific node
                st.session_state.show_feedback_form[button_key] = True
                st.rerun()
            
            # Show feedback form if button was clicked
            if show_form:
                with st.form(key=form_key, clear_on_submit=True):
                    user_feedback = st.text_area(
                        "Explain where Conner went wrong and what he should try instead:",
                        placeholder="Provide detailed feedback...",
                        key=f"feedback_{i+1}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fix_submit_button = st.form_submit_button("Submit Feedback")
                    with col2:
                        cancel_button = st.form_submit_button("Cancel")
                    
                    if fix_submit_button and user_feedback:
                        print("button triggered successfully")
                        with st.spinner("Conner is rethinking..."):
                            # Trim agent's conversation and nodes
                            agent.conversation = agent.conversation[:i+2]
                            agent.conv_nodes = agent.conv_nodes[:i]
                            
                            response_node = agent.get_response(user_feedback.strip())

                            # Store the response in session state
                            st.session_state.last_response = response_node.reason
                            st.session_state.tool_result = response_node.tool_result
                            st.session_state.last_node_uuid = response_node.uuid

                            # Reset the form visibility
                            st.session_state.show_feedback_form[button_key] = False
                            
                            # You might want to update the session state with new results here
                            st.success("Feedback submitted successfully!")
                            st.rerun()
                    
                    elif cancel_button:
                        # Hide the form
                        st.session_state.show_feedback_form[button_key] = False
                        st.rerun()
            
            st.markdown("---")