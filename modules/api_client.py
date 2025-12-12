from typing import Any
import httpx
from modules.models import (
    ApiConfig,
    CompanyIdentifier,
    CraftPayload,
)


class CraftApiClient:
    """Initialise API client with settings for headers and query"""

    def __init__(self, api_config: ApiConfig) -> None:
        self.company_id_field: CompanyIdentifier = api_config.company_id_field
        self.query_string: str = api_config.query_string
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=api_config.base_url,
            headers=api_config.headers,
            timeout=60.0,
        )

    async def fetch_company(self, company_id_value: str | int) -> dict[str, Any]:
        """Fetch craft data for a single company"""

        payload = CraftPayload(
            query=self.query_string,
            variables={self.company_id_field.value: company_id_value},
        )
        try:
            response = await self.client.post(
                "/query", json=payload.model_dump()
            )  # Use relative path
            _ = response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError, Exception) as e:
            return {
                "error": str(e),
            }

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args: Any):
        await self.client.aclose()
