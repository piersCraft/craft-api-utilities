import csv
from modules.models import Companies, Fragments


#  Input and output file management
def load_graphQL_query_fragments() -> Fragments:
    """Load pre-build query fragments from json storage file"""
    with open("graphql_fragments.json", "r") as f:
        fragments_json = f.read()
        fragments = Fragments.model_validate_json(fragments_json)

    return fragments


def read_ids_from_csv(filepath: str, column_name: str = "id") -> list[int]:
    """Read a list of IDs from a CSV file."""

    ids: list[int] = []
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ids.append(int(row[column_name]))

    return ids


def chunk_list(lst: list[int], chunk_size: int):
    """Split a list of company IDs into chunks of specified size."""

    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def write_company_data_to_json(
    company_data: Companies, companies_file_path: str = "companies.json"
) -> str:
    """Write company results data to json file in project root directory. Returns the file path"""

    with open(f"{companies_file_path}", "w") as f:
        _ = f.write(company_data.model_dump_json(indent=2))

    return companies_file_path


# GraphQL string construction
def graphql_stringify(fragments: Fragments, field_name: str):
    """Convert a list of values from a fragment object into a graphQL string for use inside a query"""

    list_values = [getattr(fragment, field_name) for fragment in fragments.fragments]
    graphql_string = " ".join(list_values)

    return graphql_string


def construct_graphql_query(fragments: Fragments) -> str:
    """Construct a graphQL query string from fragments"""

    fragment_string = graphql_stringify(fragments, "definition")
    field_spreads = graphql_stringify(fragments, "query_string")
    full_query: str = f"""{fragment_string} query company ($id: ID) {{company (id: $id) {{ {field_spreads} }} }}"""

    return full_query
