from unittest.mock import AsyncMock, Mock

import pytest
from core.services import ChatResponse, ChatService


@pytest.fixture
def mock_ai_client():
    client = Mock()
    response = Mock()
    response.choices = [Mock(message=Mock(content="AI response"))]

    # Create async mock that returns the response
    async_create = AsyncMock(return_value=response)
    client.chat.completions.create = async_create
    return client


@pytest.fixture
def mock_chat_client():
    client = Mock()
    channel = Mock()
    channel.create = AsyncMock()
    channel.send_message = AsyncMock()
    client.channel = Mock(return_value=channel)
    return client


@pytest.fixture
def chat_service(mock_ai_client, mock_chat_client):
    return ChatService(mock_ai_client, mock_chat_client)


@pytest.mark.asyncio
async def test_generate_response(chat_service, mock_ai_client, mock_chat_client):
    """Test the main response generation flow."""
    response = await chat_service.generate_response(
        user_id="test_user", message="Hello", chat_id="test_chat"
    )

    # Check response
    assert isinstance(response, ChatResponse)
    assert response.content == "AI response"
    assert response.user_id == "test_user"
    assert response.chat_id == "test_chat"

    # Verify AI call
    mock_ai_client.chat.completions.create.assert_awaited_once_with(
        model="gpt-4", messages=[{"role": "user", "content": "Hello"}]
    )

    # Verify chat operations
    mock_chat_client.channel.assert_called_once_with("messaging", "test_chat")
    channel = mock_chat_client.channel.return_value
    channel.create.assert_awaited_once_with(data={"members": ["test_user"]})
    channel.send_message.assert_awaited_once_with(
        {"text": "AI response"}, user_id="test_user"
    )


@pytest.mark.asyncio
async def test_ai_failure(chat_service, mock_ai_client):
    """Test handling of AI service failure."""
    mock_ai_client.chat.completions.create = AsyncMock(
        side_effect=Exception("AI error")
    )

    with pytest.raises(Exception, match="AI error"):
        await chat_service.generate_response("user1", "hello", "chat1")
