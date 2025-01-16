import logging
from typing import Dict, List

import httpx

logger = logging.getLogger(__name__)


async def check_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Check if API is running and list available routes."""
    try:
        async with httpx.AsyncClient() as client:
            # Check health
            response = await client.get(f"{base_url}/health")
            if response.status_code != 200:
                logger.error(f"Health check failed with status {response.status_code}")
                return False

            # List available routes
            routes_response = await client.get(f"{base_url}/openapi.json")
            if routes_response.status_code == 200:
                paths: Dict = routes_response.json()["paths"]
                routes: List[str] = list(paths.keys())
                logger.info(f"Available API routes: {routes}")
            else:
                logger.warning("Could not fetch API routes")

            return True
    except httpx.RequestError as e:
        logger.error(f"API health check failed: {str(e)}")
        return False
