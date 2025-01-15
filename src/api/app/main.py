import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from stream_chat import StreamChat

from db.app.crud import log as log_crud
from db.app.crud import message as message_crud
from db.app.schemas import LogCreate, MessageCreate

from .db import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stream_client = StreamChat(
    api_key=os.getenv("STREAM_API_KEY"),
    api_secret=os.getenv("STREAM_SECRET"),
    location="dublin",
)

app = FastAPI(
    title="Coach Bot API",
    description="AI-powered coaching bot API service",
    version="0.1.0",
)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:19006",
    "exp://localhost:19000",
]

if production_origins := os.getenv("ALLOWED_ORIGINS"):
    allowed_origins.extend(production_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Coach Bot API is running",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    services_status = {"api": "healthy", "openai": "unknown", "stream": "unknown"}

    try:
        client.models.list()
        services_status["openai"] = "healthy"
    except Exception as e:
        logger.error(f"OpenAI health check failed: {str(e)}")
        services_status["openai"] = "unhealthy"

    try:
        stream_client.get_app_settings()
        services_status["stream"] = "healthy"
    except Exception as e:
        logger.error(f"Stream health check failed: {str(e)}")
        services_status["stream"] = "unhealthy"

    return {"status": services_status}


class UserInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    chat_id: str = Field(..., min_length=1)


@app.post("/generate-response")
async def generate_response(data: UserInput):
    logger.info(f"Generating response for user {data.user_id} in chat {data.chat_id}")

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
            logger.error(f"Stream API error: {str(stream_error)}")
            raise HTTPException(
                status_code=400, detail=f"Stream API error: {str(stream_error)}"
            ) from stream_error

        return {"response": generated_message}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


class MessageRequest(BaseModel):
    chat_id: str
    user_id: str
    content: str


@app.post("/api/v1/chat/message")
async def send_message(message: MessageRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Validate UUIDs
        chat_id = uuid.UUID(message.chat_id)
        user_id = uuid.UUID(message.user_id)

        # 1. Save user message to database
        db_message = await message_crud.create(
            db,
            obj_in=MessageCreate(
                chat_id=chat_id, sender_id=user_id, content=message.content
            ),
        )

        # 2. Create log entry
        await log_crud.create(
            db,
            obj_in=LogCreate(
                user_id=user_id,
                chat_id=chat_id,
                action="send_message",
                details=f"Message sent: {message.content[:50]}...",
            ),
        )

        # 3. Send to Stream Chat
        try:
            channel = stream_client.channel("messaging", str(chat_id))
            channel.create(data={"members": [str(user_id)]})
            channel.send_message({"text": message.content}, user_id=str(user_id))
        except Exception as stream_error:
            logger.error(f"Stream API error: {str(stream_error)}")
            # Don't fail the whole request if Stream fails
            pass

        # 4. Generate AI response if needed
        try:
            response = client.chat.completions.create(
                model="gpt-4", messages=[{"role": "user", "content": message.content}]
            )
            ai_response = response.choices[0].message.content

            # Save AI response to database
            await message_crud.create(
                db,
                obj_in=MessageCreate(
                    chat_id=chat_id,
                    sender_id=user_id,  # or a special AI user ID
                    content=ai_response,
                ),
            )

            # Send AI response to Stream Chat
            channel.send_message(
                {"text": ai_response}, user_id="ai_assistant"  # or your AI user ID
            )

        except Exception as ai_error:
            logger.error(f"AI response error: {str(ai_error)}")
            # Don't fail if AI generation fails
            pass

        return {
            "status": "success",
            "message_id": str(db_message.id),
            "chat_id": str(chat_id),
            "user_id": str(user_id),
            "content": message.content,
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid UUID format") from ve
    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
