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

if "messages" not in st.session_state:
    st.session_state.messages = []
    # change these to actual user and chat ids
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.chat_id = str(uuid.uuid4())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to ask?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        logger.info(f"Sending request to {API_URL}/api/v1/chat/message")
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

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response}
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with the API: {str(e)}", exc_info=True)
        st.error(f"Error communicating with the API: {str(e)}")
