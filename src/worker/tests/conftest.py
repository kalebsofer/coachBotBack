import platform

import pytest

pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure the event loop policy for tests."""
    import asyncio

    if platform.system() == "Windows":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()
