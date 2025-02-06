import asyncio
import json
import logging
import os
from typing import Any, Dict
import uuid
from datetime import datetime

import pika
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from common.db.connect import get_session as get_db_session
from common.db.models import Message, Log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize OpenAI client using OPENAI_API_KEY
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("OPENAI_API_KEY is not set in the environment.")

client = OpenAI(api_key=openai_api_key)

async def process_message(message: Dict[str, Any]) -> None:
    """Process a message from the queue."""
    try:
        user_message = message.get("user_message", True)

        if user_message:
            logger.info(f"Picked up user message for processing for chat {message['chat_id']}")
            
            logger.info(f"Sending request to LLM for chat: {message['chat_id']} with content: {message['content'][:50]}...")

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Traction is a habit tracking app that empowers users to build and sustain positive habits through engaging conversations with a smart, supportive chatbot. **You** are that chatbot—a highly qualified, empathetic personal coach. With a PhD in psychology, exceptional verbal communication skills, over 1000 hours of supervised counselling, and UKCP accreditation, you guide users by asking insightful questions, offering tailored advice, and helping them develop consistent, actionable habits aligned with their personal goals."},
                    {"role": "user", "content": message["content"]},
                ],
                stream=False
            )
            generated_message = response.choices[0].message.content

            logger.info(f"Received LLM response for chat {message['chat_id']} with content: {generated_message[:50]}...")

            # Instead of sending the message via StreamChat,
            # we now log the assistant's response into the database.
            await log_message(message["chat_id"], generated_message, user_message=False)

            await log_audit(
                action="LLM response processed & forwarded",
                details=f"Chat ID: {message['chat_id']}, Response: {generated_message[:50]}..."
            )

            logger.info(f"Successfully processed message for chat {message['chat_id']}")
        else:
            logger.info(f"Received system message for chat {message['chat_id']}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise


async def log_message(chat_id: str, content: str, user_message: bool) -> None:
    """Log a message in the Messages table."""
    async for session in get_db_session():
        new_message = Message(
            message_id=uuid.uuid4(),
            chat_id=chat_id,
            content=content,
            user_message=user_message,
            timestamp=datetime.utcnow()
        )
        session.add(new_message)
        await session.commit()


async def log_audit(action: str, details: str) -> None:
    """Insert an audit log record into the Logs table."""
    async for session in get_db_session():
        new_log = Log(
            log_id=uuid.uuid4(),
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        session.add(new_log)
        await session.commit()


async def callback(ch, method, properties, body):
    """Process messages from RabbitMQ."""
    try:
        message = json.loads(body.decode())
        # Log that a message has been picked up from the queue
        logger.info(f"Picked up message from queue for processing: chat_id: {message.get('chat_id')}")
        await process_message(message)
        await ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}", exc_info=True)
        await ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


async def main():
    """Main function to run the worker."""
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "95.216.214.173")
    queue_name = os.getenv("QUEUE_NAME", "chat_queue")

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host)
        )
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=queue_name, durable=True)

        # Set up consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        logger.info(f"Worker started, listening on queue: {queue_name}")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
