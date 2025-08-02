import streamlit as st
from agent import Agent
import os
import json
import random
import string

# Initialize the agent
agent = Agent()
debug_write_response_2uuid='304d5122-c5ba-4d34-9dbf-1fa24754143a' 

debug_write_response_3_value="Subject Line: Prioritized Follow-ups: External Communications Review\n\nEmail Body:\nTeam,\n\nWe've identified two external emails requiring follow-up.\n\nOur immediate focus should be on the email concerning the Q4 marketing platform proposal. This item takes priority due to its potential for immediate business impact.\n\nThe second email, regarding a speaking opportunity at a digital marketing conference, is also significant. However, for initial follow-up, it should receive a lower priority compared to the marketing platform proposal.\n\nPlease prioritize action accordingly.\n\nBest regards,\n\n[Your Name/Role]\n\nConfidence Note: All demands were fully met using the available facts. The email clearly prioritizes the Q4 marketing platform proposal based on immediate business impact, while assigning a lower initial priority to the speaking opportunity, as requested. No information beyond the provided facts was included."
debug_write_response_3_reason="I have identified two important external emails: one about a proposal for a Q4 marketing platform and another regarding a speaking opportunity at a digital marketing conference. Both are significant, but initial follow-up on a potential new platform might have more immediate business impact.",

# Debug flag
DEBUG_MODE = False

# Helper: Apply debug flow overrides
def apply_debug_overrides(nodes):
    if not (DEBUG_MODE and nodes):
        return nodes
    idx2 = next((i for i, n in enumerate(nodes) if n.get('uuid') == debug_write_response_2uuid), None)
    edit_idx = st.session_state.get('edit_node_index')
    if idx2 is not None and len(nodes) > 1:
        if edit_idx == 1:
            search_node = nodes[idx2+1] if idx2+1 < len(nodes) else None
            write_node = nodes[idx2]
            if search_node and write_node:
                return [search_node, write_node]
        elif edit_idx == 2:
            if len(nodes) > 2:
                new_uuid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
                nodes[2]['uuid'] = new_uuid
                nodes[2]['tool_result'] = debug_write_response_3_value
                nodes[2]['reason'] = debug_write_response_3_reason
                return [nodes[1], nodes[2]]
    return nodes

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
    submit_button = st.form_submit_button("Send")

# Debug: Always use a fixed set of nodes for demonstration
if submit_button and user_input.strip():
    # Simulate a search node and a write node
    search_node = {
        'uuid': 'debug-search-uuid',
        'tool': 'search_emails',
        'reason': debug_write_response_3_reason,
        'confidence': 0.9,
        'parent_uuid': 'root',
        'progress': 0.9,
        'tool_result': 'Found 2 important external emails.'
    }
    write_node = {
        'uuid': 'debug-write-uuid',
        'tool': 'write_email',
        'reason': debug_write_response_3_reason,
        'confidence': 1.0,
        'parent_uuid': 'debug-search-uuid',
        'progress': 1.0,
        'tool_result': debug_write_response_3_value
    }
    st.session_state.last_node_uuid = write_node['uuid']
    st.session_state.debug_nodes = [search_node, write_node]
    st.session_state.last_response = write_node['reason']
    st.session_state.tool_result = write_node['tool_result']

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
if view_nodes and "debug_nodes" in st.session_state:
    nodes = st.session_state.debug_nodes
    nodes = apply_debug_overrides(nodes)
    st.markdown("### Flowgraph of Nodes")
    for i, node in enumerate(reversed(nodes)): # Reverse order
        st.markdown(f"**Node {i+1}:**")
        st.markdown(f"- **Tool Used:** {node.get('tool', 'N/A')}")
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
        button_key = f"button_node_{i+1}"
        form_key = f"fix_form_{i+1}"
        show_form = st.session_state.show_feedback_form.get(button_key, False)
        if st.button("Fix Thinking", key=button_key):
            st.session_state.show_feedback_form[button_key] = True
            st.session_state.edit_node_index = i  # Track which node is being edited
            st.rerun()
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
                        st.session_state.edit_node_index = i  # Track for debug override
                        # Simulate new write node on feedback
                        new_uuid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
                        new_write_node = {
                            'uuid': new_uuid,
                            'tool': 'write_email',
                            'reason': debug_write_response_3_reason,
                            'confidence': 1.0,
                            'parent_uuid': nodes[0]['uuid'],
                            'progress': 1.0,
                            'tool_result': debug_write_response_3_value
                        }
                        st.session_state.debug_nodes = [nodes[0], new_write_node]
                        st.session_state.last_response = new_write_node['reason']
                        st.session_state.tool_result = new_write_node['tool_result']
                        st.session_state.last_node_uuid = new_write_node['uuid']
                        st.session_state.show_feedback_form[button_key] = False
                        st.success("Feedback submitted successfully!")
                        st.rerun()
                elif cancel_button:
                    st.session_state.show_feedback_form[button_key] = False
                    st.rerun()
        st.markdown("---")

