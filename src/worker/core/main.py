import json
import logging
import os
from typing import Any, Dict

import pika
from dotenv import load_dotenv
from openai import OpenAI
from stream_chat import StreamChat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
stream_client = StreamChat(
    api_key=os.getenv("STREAM_API_KEY"),
    api_secret=os.getenv("STREAM_SECRET"),
    location="dublin",
)


def process_message(message: Dict[str, Any]) -> None:
    """Process a message from the queue."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": message["content"]}]
        )
        generated_message = response.choices[0].message.content

        channel = stream_client.channel("messaging", message["chat_id"])
        channel.create(data={"members": [message["user_id"]]})
        channel.send_message({"text": generated_message}, user_id=message["user_id"])

        logger.info(f"Successfully processed message for chat {message['chat_id']}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Could implement retry logic here
        raise


def callback(ch, method, properties, body):
    """Callback function for processing queue messages."""
    try:
        message = json.loads(body)
        process_message(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    """Main function to run the worker."""
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
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
        logger.error(f"Worker error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
