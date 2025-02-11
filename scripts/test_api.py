#!/usr/bin/env python3
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env (assumed to be in the project root)
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    exit(1)

client = OpenAI(api_key=openai_api_key)


def test_openai_api():
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
        )
        # Extract and print the AI response
        ai_response = response.choices[0].message.content
        print("AI Response:", ai_response)
    except Exception as e:
        # If there is an error, print the error details
        print("Error during API call:", str(e))


# # Get the Deepseek API key from environment variables and create the Deepseek client
# api_ds_key = os.environ.get("DEEPSEEK_API_KEY")
# if not api_ds_key:
#     print("Error: DEEPSEEK_API_KEY environment variable is not set.")
#     exit(1)

# client = OpenAI(api_key=api_ds_key, base_url="https://api.deepseek.com")

# def test_deepseek_api():
#     try:
#         # Attempt to generate a chat completion using Deepseek
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[
#                 {"role": "system", "content": "Traction is a habit tracking app that empowers users to build and sustain positive habits through engaging conversations with a smart, supportive chatbot. **You** are that chatbot—a highly qualified, empathetic personal coach. With a PhD in psychology, exceptional verbal communication skills, over 1000 hours of supervised counselling, and UKCP accreditation, you guide users by asking insightful questions, offering tailored advice, and helping them develop consistent, actionable habits aligned with their personal goals."},
#                 {"role": "user", "content": "Hello, how are you?"}
#             ],
#             stream=False
#         )
#         # Extract and print the AI response
#         ai_response = response.choices[0].message.content
#         print("AI Response:", ai_response)
#     except Exception as e:
#         print("Error during API call:", str(e))

if __name__ == "__main__":
    test_openai_api()
