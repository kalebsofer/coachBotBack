import logging
import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

# Get API URL from environment, fallback to api:8000 for docker
API_URL = os.getenv("API_URL", "http://api:8000")
logger = logging.getLogger(__name__)
logger.info(f"Using API URL: {API_URL}")

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="CoachBot Chat", page_icon="🤖", layout="centered")

st.title("🤖 CoachBot Chat")

# Initialize session state with the test user's ID
# The user must already exist in Postgres to start a chat
if "user_id" not in st.session_state:
    # Test user ID created in Postgres
    st.session_state.user_id = "d62a2f99-e89b-43ad-b4ba-ec3826266410"

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# New Chat Button
if st.button("New Chat"):
    logger.info(f"UI Event: 'New Chat' button clicked by user {st.session_state.user_id}")
    # Send request to create a new chat
    response = requests.post(
        f"{API_URL}/api/v1/chats",
        json={"user_id": st.session_state.user_id}
    )
    if response.status_code == 200:
        chat_data = response.json()
        st.session_state.chat_id = chat_data["chat_id"]
        logger.info(f"New Chat: User {st.session_state.user_id} started chat {st.session_state.chat_id}.")
        st.success("New chat started!")
    else:
        logger.error(f"UI Error: Failed to start a new chat for user {st.session_state.user_id}. Response: {response.text}")
        st.error("Failed to start a new chat.")

# Display chat messages if a chat is active
if st.session_state.chat_id:
    st.write(f"Chat ID: {st.session_state.chat_id}")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if st.session_state.messages:
        logger.info(f"UI Event: Rendering {len(st.session_state.messages)} messages for chat {st.session_state.chat_id} for user {st.session_state.user_id}.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to ask?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        logger.info(f"UI Event: User message submitted in chat {st.session_state.chat_id}. User: {st.session_state.user_id}, Content: {prompt}")

        try:
            logger.info(f"UI Event: Sending user message for chat {st.session_state.chat_id}. User: {st.session_state.user_id}, Content: {prompt}")
            response = requests.post(
                f"{API_URL}/api/v1/chat/message",
                json={
                    "chat_id": st.session_state.chat_id,
                    "user_id": st.session_state.user_id,
                    "content": prompt
                },
            )
            response.raise_for_status()
            response_data = response.json()
            assistant_response = response_data.get("content", "No response received")

            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            logger.info(f"UI Event: Displayed assistant response for chat {st.session_state.chat_id}")
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response}
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with the API: {str(e)}", exc_info=True)
            st.error(f"Error communicating with the API: {str(e)}")
