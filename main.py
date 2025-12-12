import asyncio
from typing import Any
from modules.api_client import CraftApiClient
from modules.database import DuckDbClient
from modules.models import ApiConfig, ApiResults
from modules.helper_functions import read_ids_from_csv, async_batch_processor


# TODO: Create a dictionary or enum for different query types that can be passed to ApiConfig
query_string = """
fragment Firmographics on Company { id duns displayName countryOfRegistration homepage shortDescription companyType }
fragment CreditScore on Company { creditScore { currentCreditRating { commonValue commonDescription } } }
fragment ComplianceData on Company { complianceData { datasets requestStatus } }
fragment SecurityRatings on Company { securityRatings { score grade datetime } }
fragment DataBreaches on Company { dataBreaches { affectedRecordsCount date description provider } }
query company ($id: ID!) { company(id: $id) {
 ...Firmographics 
 ...CreditScore
 ...ComplianceData
 ...SecurityRatings
 ...DataBreaches
} }
"""


async def main():
    client_config = ApiConfig(query_string=query_string)
    client = CraftApiClient(client_config)
    ids: list[str | int] = read_ids_from_csv("tests/bc_partners_ids.csv")
    results = {"results": await async_batch_processor(client.fetch_company, ids)}

    company_data = ApiResults.model_validate(results)

    # TODO: Serialize to json and load to duckdb table
    company_data_json = company_data.model_dump_json(indent=2)

    db_client = DuckDbClient(database_path="bc_test.db")
    _ = db_client.db_write_json_to_table(company_data_json)
    _ = db_client.unpack_company_data()
    _ = db_client.close()


# TODO: Run data transformations in Duckdb

# TODO: Export results to csv file


if __name__ == "__main__":
    asyncio.run(main())
