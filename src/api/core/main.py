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

from db.core.crud import log as log_crud
from db.core.crud import message as message_crud
from db.core.schemas import LogCreate, MessageCreate

from .db import get_db
from .services import ChatService

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

chat_service = ChatService(client, stream_client)


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


# Create crud container
class CrudOperations:
    def __init__(self):
        self.log = log_crud
        self.message = message_crud


# Dependency function
def get_crud():
    return CrudOperations()


@app.post("/generate-response")
async def generate_response(data: UserInput):
    try:
        response = await chat_service.generate_response(
            data.user_id, data.message, data.chat_id
        )
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MessageRequest(BaseModel):
    chat_id: str
    user_id: str
    content: str


@app.post("/api/v1/chat/message")
async def send_message(message: MessageRequest, db: AsyncSession = Depends(get_db)):
    try:
        chat_id = uuid.UUID(message.chat_id)
        user_id = uuid.UUID(message.user_id)

        # Use db session for database operations
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
