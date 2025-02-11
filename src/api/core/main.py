import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# from stream_chat import StreamChat
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.connect import get_db as get_db
from common.db.connect import wait_for_db
from common.db.crud import chat as chat_crud
from common.db.crud import log as log_crud
from common.db.crud import message as message_crud
from common.db.schemas import ChatCreate, LogCreate, MessageCreate

from .logging_config import configure_logging
from .services import ChatService

logger = configure_logging()
logger.info("Starting API application initialization")

try:
    load_dotenv()
    logger.info("Environment variables loaded")

    # Initialize the OpenAI client (StreamChat is not used with the Streamlit UI)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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


# Dummy chat client to satisfy ChatService dependency while StreamChat is removed.
class DummyChatClient:
    def channel(self, channel_type, channel_id):
        class DummyChannel:
            def create(self, data):
                # Do nothing
                pass

            def send_message(self, message, user_id):
                # Do nothing
                pass

        return DummyChannel()


# -----------------------------------------------------------

# Then, update the instantiation of ChatService.
# Previous code:
# chat_service = ChatService(client)
chat_service = ChatService(client, DummyChatClient())


@app.on_event("startup")
async def startup_event():
    logger.info("=== API Service Startup ===")
    logger.info("Checking environment variables...")

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
        # Receive and Validate Input
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
            # Persist in PostgreSQL (Saving full message details)
            db_message = await message_crud.create(
                db,
                obj_in=MessageCreate(
                    chat_id=chat_id, user_id=user_id, content=message.content
                ),
            )
            logger.info(f"Message saved to database with ID: {db_message.message_id}")
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Database error") from db_error

        try:
            # Create a log entry to record message sending for auditing purposes
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

        # Dispatch to Downstream Systems (e.g., forward to message queue)
        logger.info(
            f"Forwarding message to message queue - user_id: {user_id}, "
            f"chat_id: {chat_id}, content: {message.content[:50]}..."
        )

        try:
            # Generate AI response
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": message.content}],
            )
            ai_response = response.choices[0].message.content

            # Save AI response to database
            await message_crud.create(
                db,
                obj_in=MessageCreate(
                    chat_id=chat_id,
                    user_id=user_id,
                    content=ai_response,
                ),
            )

            return {
                "status": "success",
                "message_id": str(db_message.message_id),
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "content": ai_response,
            }

        except Exception as ai_error:
            logger.error(f"AI response error: {str(ai_error)}")
            # Return an error message if AI fails
            return {
                "status": "error",
                "message_id": str(db_message.message_id),
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "content": "Error connecting to the server, please try again later.",
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
        logger.info(
            "Created new chat with chat_id: %s for user %s",
            new_chat.chat_id,
            chat_data.user_id,
        )
        return {"chat_id": str(new_chat.chat_id)}
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create chat")


@app.get("/api/v1/chats/{chat_id}")
async def get_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    # Retrieve the chat instance. Ensure your chat_crud.get includes an eager load of messages.
    chat = await chat_crud.get(db, id=uuid.UUID(chat_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Transform the messages to match the frontend expected format.
    messages = []
    for msg in chat.messages:
        # Determine role based on the user_message boolean
        role = "user" if msg.user_message else "assistant"
        messages.append(
            {
                "role": role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            }
        )
    return messages


logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
