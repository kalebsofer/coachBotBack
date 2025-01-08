import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def env():
    load_dotenv(".env.example")
