import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from stream_chat import StreamChat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize clients
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

# CORS configuration
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:19006",  # Expo web
    "exp://localhost:19000",  # Expo Go
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


# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "Coach Bot API is running",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    # Add basic service checks
    services_status = {"api": "healthy", "openai": "unknown", "stream": "unknown"}

    try:
        # Basic OpenAI API check
        client.models.list()
        services_status["openai"] = "healthy"
    except Exception as e:
        logger.error(f"OpenAI health check failed: {str(e)}")
        services_status["openai"] = "unhealthy"

    try:
        # Basic Stream API check
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
        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": data.message}]
        )
        generated_message = response.choices[0].message.content

        # Send to Stream Chat
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
