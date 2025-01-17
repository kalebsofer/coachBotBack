import json
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Mock the database modules
mock_crud = Mock()
mock_crud.log = Mock()
mock_crud.message = Mock()

mock_core = Mock()
mock_core.crud = mock_crud

mock_coach_bot_db = Mock()
mock_coach_bot_db.core = mock_core

# Mock modules before imports
sys.modules["coach_bot_db"] = mock_coach_bot_db
sys.modules["coach_bot_db.core"] = mock_core
sys.modules["coach_bot_db.core.crud"] = mock_crud

# Now we can safely import our app
with patch("openai.OpenAI"), patch("stream_chat.StreamChat"):
    from core.main import callback, process_message


@pytest.fixture
def mock_openai():
    with patch("core.main.openai_client") as mock:
        # Create a proper async response
        async def async_create(**kwargs):
            return Mock(choices=[Mock(message=Mock(content="Test AI response"))])

        mock.chat.completions.create = async_create
        yield mock


@pytest.fixture
def mock_stream():
    with patch("core.main.stream_client") as mock:
        channel = Mock()
        channel.create = AsyncMock()
        channel.send_message = AsyncMock()
        mock.channel = Mock(return_value=channel)
        yield mock


@pytest.fixture
def mock_channel():
    mock = Mock()
    mock.basic_ack = AsyncMock()
    mock.basic_nack = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_process_message_success(mock_openai, mock_stream):
    """Test successful message processing."""
    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}

    await process_message(message)

    # Verify Stream Chat calls
    mock_stream.channel.assert_called_once_with("messaging", "test_chat")
    channel = mock_stream.channel.return_value

    # Verify channel.create call
    assert channel.create.await_count == 1
    assert channel.create.await_args.kwargs == {"data": {"members": ["test_user"]}}

    # Verify channel.send_message call
    assert channel.send_message.await_count == 1
    assert channel.send_message.await_args.args == ({"text": "Test AI response"},)
    assert channel.send_message.await_args.kwargs == {"user_id": "test_user"}


@pytest.mark.asyncio(scope="function")
async def test_process_message_openai_error(mock_openai, mock_stream):
    """Test handling of OpenAI API error."""

    async def raise_error(**kwargs):
        raise Exception("API Error")

    mock_openai.chat.completions.create = raise_error

    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello"}

    with pytest.raises(Exception, match="API Error"):
        await process_message(message)

    mock_stream.channel.assert_not_called()


@pytest.mark.asyncio
async def test_callback_success(mock_openai, mock_stream, mock_channel):
    """Test successful message callback processing."""
    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello"}
    method = Mock(delivery_tag="test_tag")

    await callback(mock_channel, method, None, json.dumps(message).encode())

    # Verify message was acknowledged
    assert mock_channel.basic_ack.await_count == 1
    assert mock_channel.basic_ack.await_args.kwargs == {"delivery_tag": "test_tag"}
    assert mock_channel.basic_nack.await_count == 0


@pytest.mark.asyncio
async def test_callback_error(mock_openai, mock_stream, mock_channel):
    """Test error handling in callback."""

    async def raise_error(**kwargs):
        raise Exception("API Error")

    mock_openai.chat.completions.create = raise_error

    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello"}
    method = Mock(delivery_tag="test_tag")

    await callback(mock_channel, method, None, json.dumps(message).encode())

    # Verify message was not acknowledged and requeued
    assert mock_channel.basic_ack.await_count == 0
    assert mock_channel.basic_nack.await_count == 1
    assert mock_channel.basic_nack.await_args.kwargs == {
        "delivery_tag": "test_tag",
        "requeue": True,
    }
