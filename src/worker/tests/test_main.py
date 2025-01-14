import json
from unittest.mock import Mock, patch

import pytest
from app.main import callback, process_message


@pytest.fixture
def mock_openai():
    with patch("app.main.openai_client") as mock:
        mock.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Test AI response"))
        ]
        yield mock


@pytest.fixture
def mock_stream():
    with patch("app.main.stream_client") as mock:
        mock.channel.return_value.create.return_value = None
        mock.channel.return_value.send_message.return_value = None
        yield mock


@pytest.fixture
def mock_channel():
    mock = Mock()
    mock.basic_ack = Mock()
    mock.basic_nack = Mock()
    return mock


def test_process_message_success(mock_openai, mock_stream):
    """Test successful message processing."""
    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}

    process_message(message)

    # Verify OpenAI call
    mock_openai.chat.completions.create.assert_called_once_with(
        model="gpt-4", messages=[{"role": "user", "content": "Hello, bot!"}]
    )

    # Verify Stream Chat calls
    mock_stream.channel.assert_called_once_with("messaging", "test_chat")
    mock_stream.channel.return_value.create.assert_called_once_with(
        data={"members": ["test_user"]}
    )
    mock_stream.channel.return_value.send_message.assert_called_once_with(
        {"text": "Test AI response"}, user_id="test_user"
    )


def test_process_message_openai_error(mock_openai, mock_stream):
    """Test handling of OpenAI API error."""
    mock_openai.chat.completions.create.side_effect = Exception("API Error")

    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}

    with pytest.raises(Exception) as exc_info:
        process_message(message)

    assert str(exc_info.value) == "API Error"
    mock_stream.channel.assert_not_called()


def test_process_message_stream_error(mock_openai, mock_stream):
    """Test handling of Stream Chat API error."""
    mock_stream.channel.return_value.send_message.side_effect = Exception(
        "Stream Error"
    )

    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}

    with pytest.raises(Exception) as exc_info:
        process_message(message)

    assert str(exc_info.value) == "Stream Error"


def test_callback_success(mock_openai, mock_stream, mock_channel):
    """Test successful message callback processing."""
    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}
    method = Mock(delivery_tag="test_tag")

    callback(mock_channel, method, None, json.dumps(message).encode())

    # Verify message was acknowledged
    mock_channel.basic_ack.assert_called_once_with(delivery_tag="test_tag")
    mock_channel.basic_nack.assert_not_called()


def test_callback_error(mock_openai, mock_stream, mock_channel):
    """Test error handling in callback."""
    mock_openai.chat.completions.create.side_effect = Exception("API Error")

    message = {"user_id": "test_user", "chat_id": "test_chat", "content": "Hello, bot!"}
    method = Mock(delivery_tag="test_tag")

    callback(mock_channel, method, None, json.dumps(message).encode())

    # Verify message was not acknowledged and requeued
    mock_channel.basic_ack.assert_not_called()
    mock_channel.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=True
    )


def test_callback_invalid_json(mock_channel):
    """Test handling of invalid JSON message."""
    method = Mock(delivery_tag="test_tag")

    callback(mock_channel, method, None, b"invalid json")

    # Verify message was not acknowledged and requeued
    mock_channel.basic_ack.assert_not_called()
    mock_channel.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=True
    )
