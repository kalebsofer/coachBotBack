import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from stream_chat import StreamChat

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stream_client = StreamChat(
    api_key=os.getenv("STREAM_API_KEY"),
    api_secret=os.getenv("STREAM_SECRET"),
    location="dublin",
)


app = FastAPI()


class UserInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    chat_id: str = Field(..., min_length=1)


@app.post("/generate-response")
async def generate_response(data: UserInput):
    try:
        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": data.message}]
        )
        generated_message = response.choices[0].message.content

        try:
            channel = stream_client.channel("messaging", data.chat_id)
            channel.create(data={"members": [data.user_id]})
            channel.send_message({"text": generated_message}, user_id=data.user_id)
        except Exception as stream_error:
            raise HTTPException(
                status_code=400, detail=f"Stream API error: {str(stream_error)}"
            ) from stream_error

        return {"response": generated_message}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e
