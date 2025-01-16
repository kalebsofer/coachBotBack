from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

with (
    patch("openai.OpenAI") as _mock_openai_init,
    patch("stream_chat.StreamChat") as _mock_stream_init,
):
    from core.main import app

client = TestClient(app)


@pytest.fixture
def mock_openai():
    with patch("core.main.client") as mock:
        mock.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Test AI response"))
        ]
        yield mock


@pytest.fixture
def mock_stream():
    with patch("core.main.stream_client") as mock:
        mock.channel.return_value.create.return_value = None
        mock.channel.return_value.send_message.return_value = None
        yield mock


def test_generate_response_success(mock_openai, mock_stream):
    response = client.post(
        "/generate-response",
        json={
            "user_id": "test_user",
            "message": "Hello",
            "chat_id": "test_chat",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"response": "Test AI response"}
    mock_openai.chat.completions.create.assert_called_once()
    mock_stream.channel.assert_called_once_with("messaging", "test_chat")
