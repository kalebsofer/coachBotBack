from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_openai():
    with patch("src.main.client") as mock:
        mock.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Test AI response"))
        ]
        yield mock


@pytest.fixture
def mock_stream():
    with patch("src.main.stream_client") as mock:
        mock.channel.return_value.create.return_value = None
        mock.channel.return_value.send_message.return_value = None
        yield mock


def test_generate_response_success(mock_openai, mock_stream):
    response = client.post(
        "/generate-response",
        json={"user_id": "test_user", "message": "Hello", "chat_id": "test_chat"},
    )

    assert response.status_code == 200
    assert response.json() == {"response": "Test AI response"}
    mock_openai.chat.completions.create.assert_called_once()
    mock_stream.channel.assert_called_once_with("messaging", "test_chat")


def test_generate_response_stream_error(mock_openai, mock_stream):
    class StreamError(Exception):
        pass

    mock_stream.channel.return_value.create.side_effect = StreamError("Stream error")

    response = client.post(
        "/generate-response",
        json={"user_id": "test_user", "message": "Hello", "chat_id": "test_chat"},
    )

    assert response.status_code == 400
    assert "Stream API error" in response.json()["detail"]


def test_generate_response_invalid_input():
    response = client.post(
        "/generate-response",
        json={"invalid": "data"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "input_data",
    [
        {"user_id": "", "message": "Hello", "chat_id": "test"},
        {"user_id": "test", "message": "", "chat_id": "test"},
        {"user_id": "test", "message": "Hello", "chat_id": ""},
    ],
)
def test_generate_response_empty_fields(input_data):
    response = client.post("/generate-response", json=input_data)
    assert response.status_code == 422
