import httpx

from mir_commander.core.consts import BASE_URL
from mir_commander.core.errors import NetworkError


async def get_latest_version() -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/latest_version")
            response.raise_for_status()
            return response.json()["data"]["version"]
        except (TypeError, ValueError, KeyError):
            raise NetworkError("Invalid response from the server")
        except httpx.HTTPError as e:
            raise NetworkError(str(e))
