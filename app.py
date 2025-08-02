import streamlit as st
from agent import Agent

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

# Display the response if available
if "last_response" in st.session_state:
    st.text_area(
        "Response:",
        value=st.session_state.last_response,
        height=80,
        disabled=True,
        key="conner_response_final"
    )

# Instructions
st.markdown("---")
st.markdown("""
**Instructions:**
- Tell Conner to do a task, and he will do it!
- Monitor Conner's thought process to correct him if things go wrong
""")