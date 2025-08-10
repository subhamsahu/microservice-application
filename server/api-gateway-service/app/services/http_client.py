from typing import Union
import httpx
import jwt

from app.core.config import config
from app.core.logger import logger


class HTTPClientService:
    """
    Provides a reusable HTTPX AsyncClient with optional gateway JWT token.
    """

    def __init__(self, base_url: str, service_name: str = ""):
        self.base_url = base_url
        self.service_name = service_name
        self.client = self._create_client()

    def _create_client(self) -> httpx.AsyncClient:
        gateway_token = ""
        if self.service_name:
            try:
                gateway_token = jwt.encode(
                    {"id": self.service_name},
                    config.GATEWAY_JWT_TOKEN,
                    algorithm="HS256"
                )
            except Exception as e:
                logger.error(f"Error generating gateway token: {e}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "gatewaytoken": gateway_token
        }

        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=10.0
        )

    async def get(self, url: str, params: Union[dict, None] = None):
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response

    async def post(self, url: str, data: Union[dict, None] = None, json: Union[dict, None] = None):
        response = await self.client.post(url, data=data, json=json)
        response.raise_for_status()
        return response

    async def close(self):
        await self.client.aclose()
