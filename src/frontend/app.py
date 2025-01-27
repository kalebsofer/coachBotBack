import logging
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://api:8000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="CoachBot Chat", page_icon="🤖", layout="centered")

st.title("🤖 CoachBot Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to ask?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    user_id = "test"  # Replace with actual user ID
    chat_id = "test"  # Replace with actual chat ID

    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat/message",
            json={"chat_id": chat_id, "user_id": user_id, "content": prompt},
        )
        response.raise_for_status()
        assistant_response = response.json()["response"]

        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response}
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with the API: {str(e)}", exc_info=True)
        st.error(f"Error communicating with the API: {str(e)}")
