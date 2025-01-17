import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Create mock database session
mock_session = AsyncMock()
mock_session.__aenter__ = AsyncMock(return_value=mock_session)
mock_session.__aexit__ = AsyncMock(return_value=None)

# Create mock database
mock_database = Mock()
mock_database.AsyncSessionLocal = AsyncMock(return_value=mock_session)

# Create mock module structure
mock_log = Mock()
mock_message = Mock()
mock_crud = Mock()
mock_crud.log = mock_log
mock_crud.message = mock_message

mock_schemas = Mock()
mock_schemas.LogCreate = Mock
mock_schemas.MessageCreate = Mock

mock_core = Mock()
mock_core.crud = mock_crud
mock_core.schemas = mock_schemas
mock_core.database = mock_database

mock_coach_bot_db = Mock()
mock_coach_bot_db.core = mock_core

# Mock the modules before any imports
sys.modules["coach_bot_db"] = mock_coach_bot_db
sys.modules["coach_bot_db.core"] = mock_core
sys.modules["coach_bot_db.core.crud"] = mock_crud
sys.modules["coach_bot_db.core.schemas"] = mock_schemas
sys.modules["coach_bot_db.core.database"] = mock_database

# Now we can safely import our app
with (
    patch("openai.OpenAI") as _mock_openai_init,
    patch("stream_chat.StreamChat") as _mock_stream_init,
):
    from core.main import app


@pytest.fixture
def test_app():
    return app


@pytest.fixture
def mock_db():
    return mock_coach_bot_db


@pytest.fixture
def mock_crud():
    return mock_crud


@pytest.fixture
def mock_schemas():
    return mock_schemas


@pytest.fixture
def mock_db_session():
    return mock_session
