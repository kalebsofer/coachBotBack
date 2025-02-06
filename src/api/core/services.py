from pydantic import BaseModel


class ChatResponse(BaseModel):
    content: str
    user_id: str
    chat_id: str


class ChatService:
    def __init__(self, ai_client, chat_client):
        self.ai_client = ai_client
        self.chat_client = chat_client

    async def generate_response(
        self, user_id: str, message: str, chat_id: str
    ) -> ChatResponse:
        """Generate AI response and handle chat interactions."""
        
        ai_response = await self._get_ai_response(message)

        await self._send_to_chat(chat_id, user_id, ai_response)

        return ChatResponse(
            content=ai_response,
            user_id=user_id,
            chat_id=chat_id,
        )

    async def _get_ai_response(self, message: str) -> str:
        """Get response from AI service."""
        response = await self.ai_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content

    async def _send_to_chat(self, chat_id: str, user_id: str, message: str) -> None:
        """Send message to chat service."""
        channel = self.chat_client.channel("messaging", chat_id)
        await channel.create(data={"members": [user_id]})
        await channel.send_message({"text": message}, user_id=user_id)
