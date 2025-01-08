import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import openai
from stream_chat import StreamChat

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
stream_client = StreamChat(
    api_key=os.getenv("STREAM_API_KEY"), api_secret=os.getenv("STREAM_SECRET")
)

app = FastAPI()


class UserInput(BaseModel):
    user_id: str
    message: str


@app.post("/generate-response")
async def generate_response(data: UserInput):
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": data.message}]
    )
    generated_message = response["choices"][0]["message"]["content"]

    stream_client.send_message({"text": generated_message}, data.user_id, "<CHAT_ID>")
    return {"response": generated_message}
