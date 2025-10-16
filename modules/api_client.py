import asyncio
from typing import Any
import httpx
from modules.models import Company, Companies, ApiResponse
from modules.helper_functions import chunk_list


async def fetch_company(
    client: httpx.AsyncClient, QUERY: str, company_id: int
) -> dict[str, Any] | Company:
    """Fetch a single company from the craft API"""
    try:
        payload = {"query": QUERY, "variables": {"id": company_id}}
        response = await client.post("https://api.craft.co/v1/query", json=payload)
        _ = response.raise_for_status()

        api_response = ApiResponse.model_validate(response.json())
        company = api_response.data.company

        return company

    except httpx.HTTPStatusError as e:
        return {
            "id": company_id,
            "data": None,
            "error": f"HTTP {e.response.status_code}: {str(e)}",
        }
    except httpx.RequestError as e:
        return {"id": company_id, "data": None, "error": f"Request error: {str(e)}"}
    except KeyError as e:
        return {
            "id": company_id,
            "data": None,
            "error": f"Missing key in response: {str(e)}",
        }
    except Exception as e:
        return {
            "id": company_id,
            "data": None,
            "error": f"Unexpected error: {type(e).__name__}: {str(e)}",
        }


async def fetch_companies(QUERY: str, company_ids: list[int], api_key: str):
    """
    Fetch company data for a list of company_ids using a defined graphQL query.

    Returns a list of companies with nested data flattened for downstream processing.
    """
    headers = {
        "x-craft-api-key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=60.0,  # 30 second timeout
        follow_redirects=True,
    ) as client:
        # Batch company_ids into groups of 100
        batches = chunk_list(company_ids, 100)

        all_responses = []

        # Process each batch sequentially to avoid overwhelming the API
        for batch in batches:
            tasks = [fetch_company(client, QUERY, company_id) for company_id in batch]
            batch_responses = await asyncio.gather(*tasks)
            all_responses.extend(batch_responses)

        company_results = Companies.model_validate({"companies": all_responses})

        return company_results


async def main():
    print("Async API client to fetch data from the Craft API")


if __name__ == "__main__":
    asyncio.run(main())
