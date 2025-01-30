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
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from db.core.crud import log as log_crud
from db.core.crud import message as message_crud
from db.core.schemas import LogCreate, MessageCreate

from .db import get_db
from .services import ChatService
from .logging_config import configure_logging

# Configure logging first thing
logger = configure_logging()
logger.info("Starting API application initialization")

# Rest of the imports...

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

# Create FastAPI app with logging
app = FastAPI(
    title="Coach Bot API",
    description="AI-powered coaching bot API service",
    version="0.1.0",
)

logger.info("FastAPI application created")

# For prometheus metrics
Instrumentator().instrument(app).expose(app)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService(client, stream_client)

@app.on_event("startup")
async def startup_event():
    logger.info("=== API Service Startup ===")
    
    # Log environment check
    logger.info("Checking environment variables...")
    for env_var in ["DATABASE_URL", "OPENAI_API_KEY", "STREAM_API_KEY"]:
        if env_var in os.environ:
            logger.info(f"✓ {env_var} is configured")
        else:
            logger.error(f"✗ {env_var} is missing")

    # Database check
    logger.info("Testing database connection...")
    try:
        db = await anext(get_db())
        try:
            await db.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
        finally:
            await db.close()
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        logger.error("API might not function correctly without database")
        raise  # Fail startup if database isn't available

    logger.info("=== Startup Complete ===")


@app.get("/")
async def root():
    return {
        "message": "Coach Bot API is running",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    # Quick database check
    try:
        db = await anext(get_db())
        try:
            await db.execute(text("SELECT 1"))
            return {"status": "healthy"}
        finally:
            await db.close()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


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
        # Add debug logging
        logger.info(f"Received message request: {message}")
        
        try:
            chat_id = uuid.UUID(message.chat_id)
            user_id = uuid.UUID(message.user_id)
        except ValueError as ve:
            logger.error(f"Invalid UUID format: {str(ve)}")
            raise HTTPException(status_code=400, detail="Invalid UUID format") from ve

        try:
            # Save message to database
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
            # Create log entry
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
