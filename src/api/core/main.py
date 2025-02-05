import logging
import os
import uuid
import asyncio

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from stream_chat import StreamChat
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from common.db.crud import log as log_crud
from common.db.crud import message as message_crud
from common.db.schemas import LogCreate, MessageCreate, ChatCreate, ChatRead
from common.db.crud import chat as chat_crud
from common.db.connect import get_db as get_db, wait_for_db
from .services import ChatService
from .logging_config import configure_logging

logger = configure_logging()
logger.info("Starting API application initialization")

try:
    load_dotenv()
    logger.info("Environment variables loaded")

    # Initialize clients
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    stream_client = StreamChat(
        api_key=os.getenv("STREAM_API_KEY"),
        api_secret=os.getenv("STREAM_SECRET"),
        location="dublin",
    )
    logger.info("API clients initialized")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

app = FastAPI(
    title="Coach Bot API",
    description="AI-powered coaching bot API service",
    version="0.1.0",
)

logger.info("FastAPI application created")

# For prometheus metrics
Instrumentator().instrument(app).expose(app)

# Allow all origins in development, configure properly in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService(client, stream_client)

@app.on_event("startup")
async def startup_event():
    logger.info("=== API Service Startup ===")
    logger.info("Checking environment variables...")
    
    # Verify required environment variables
    required_vars = ["DATABASE_URL", "OPENAI_API_KEY", "STREAM_API_KEY"]
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✓ {var} is configured")
        else:
            logger.error(f"✗ {var} is not configured")
            raise ValueError(f"Missing required environment variable: {var}")
    
    logger.info("Testing database connection...")
    try:
        await wait_for_db()
        logger.info("✓ Database connection successful")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise

    logger.info("=== Startup Complete ===")


@app.get("/")
async def root():
    return {
        "message": "Coach Bot API is running",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Quick db check using dependency injection
    await db.execute(text("SELECT 1"))
    return {"status": "healthy"}


class UserInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    chat_id: str = Field(..., min_length=1)


# Create crud container
class CrudOperations:
    def __init__(self):
        self.log = log_crud
        self.message = message_crud
        self.chat = chat_crud


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
        # Step 1: Receive and Validate Input
        logger.info(
            f"Received user message from frontend - user_id: {message.user_id}, "
            f"chat_id: {message.chat_id}, content: {message.content[:50]}..."
        )
        
        try:
            chat_id = uuid.UUID(message.chat_id)
            user_id = uuid.UUID(message.user_id)
        except ValueError as ve:
            logger.error(f"Invalid UUID format for chat_id or user_id: {str(ve)}")
            raise HTTPException(status_code=400, detail="Invalid UUID format") from ve

        try:
            # Step 2: Persist in PostgreSQL (Saving full message details)
            db_message = await message_crud.create(
                db,
                obj_in=MessageCreate(
                    chat_id=chat_id, 
                    sender_id=user_id, 
                    content=message.content
                ),
            )
            logger.info(f"Message saved to database with ID: {db_message.id}")
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Database error") from db_error

        try:
            # (Optional) Create a log entry to record message sending for auditing purposes
            await log_crud.create(
                db,
                obj_in=LogCreate(
                    user_id=user_id,
                    chat_id=chat_id,
                    action="send_message",
                    details=f"Message sent: {message.content[:50]}...",
                ),
            )
        except Exception as log_error:
            logger.error(f"Log creation error: {str(log_error)}")
            # Don't fail if logging fails

        # Step 3: Dispatch to Downstream Systems (e.g., forward to message queue)
        logger.info(
            f"Forwarding message to message queue - user_id: {user_id}, "
            f"chat_id: {chat_id}, content: {message.content[:50]}..."
        )

        try:
            # Stream Chat integration
            channel = stream_client.channel("messaging", str(chat_id))
            channel.create(data={"members": [str(user_id)]})
            channel.send_message({"text": message.content}, user_id=str(user_id))
        except Exception as stream_error:
            logger.error(f"Stream API error: {str(stream_error)}")
            # Don't fail if Stream fails

        try:
            # Generate AI response
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": message.content}]
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
                {"text": ai_response}, 
                user_id="ai_assistant"
            )

            return {
                "status": "success",
                "message_id": str(db_message.id),
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "content": ai_response,  # Return AI response instead of user message
            }

        except Exception as ai_error:
            logger.error(f"AI response error: {str(ai_error)}")
            # Return original message if AI fails
            return {
                "status": "partial_success",
                "message_id": str(db_message.id),
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "content": message.content,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/chats")
async def create_chat(chat_data: ChatCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new chat session for the provided user.
    
    Expected JSON payload example:
    {
        "user_id": "8fe294f5-bddc-48a2-83b1-357338df9642"
    }
    """
    try:
        new_chat = await chat_crud.create(db, obj_in=chat_data)
        logger.info(f"Created new chat with chat_id: {new_chat.chat_id} for user {chat_data.user_id}")
        return {"chat_id": str(new_chat.chat_id)}
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create chat")
