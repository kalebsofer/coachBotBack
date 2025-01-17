import pytest

pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure the event loop policy for tests."""
    import asyncio

    return asyncio.WindowsSelectorEventLoopPolicy()
