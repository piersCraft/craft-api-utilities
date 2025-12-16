import asyncio
from pyarrow import Table
from modules.api_client import CraftApiClient
from modules.database import DuckDbClient
from modules.models import ApiConfig, ApiResponse
from modules.helper_functions import (
    read_ids_from_csv,
    async_batch_processor,
    import_dictlist_to_pyarrow,
)


# TODO: Create a client config object that can be resurrected if the process needs to be repeated
query_string = """
fragment Firmographics on Company { id duns displayName countryOfRegistration homepage shortDescription companyType }
fragment CreditScore on Company { creditScore { currentCreditRating { commonValue commonDescription } } }
fragment ComplianceEvidence on AcurisEvidence { title summary credibility captureDateIso publicationDateIso language keywords assetUrl originalUrl datasets }
fragment ComplianceData on Company { complianceData { datasets requestStatus relEntries { category subcategory events { type dateIso currencyCode amount evidences { ...ComplianceEvidence } } } } }
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
    # Initialise API client
    client_config = ApiConfig(query_string=query_string)
    client = CraftApiClient(client_config)
    # Import ids
    ids: list[str | int] = read_ids_from_csv("tests/bc_partners_ids_all.csv")
    # Fetch data in batches of 100
    results = await async_batch_processor(client.fetch_company, ids, batch_size=100)
    # Validate responses into a list of objects for pyarrow
    responses: list[ApiResponse] = [
        ApiResponse.model_validate(response) for response in results
    ]
    # Import list of companies to a pyarrow table
    companies_table: Table = import_dictlist_to_pyarrow(
        [r.data.company.model_dump() for r in responses]
    )

    # Initialise Database client and import the pyarrow table
    db_client = DuckDbClient(database_path="bcp_reports.db")
    _ = db_client.create_table_from_arrow(
        target_table_name="companies", arrow_data=companies_table
    )
    _ = db_client.close()


if __name__ == "__main__":
    asyncio.run(main())
