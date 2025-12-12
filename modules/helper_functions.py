import csv
import asyncio
from typing import Any, Callable


def read_ids_from_csv(filepath: str, column_name: str = "id") -> list[int | str]:
    """Read a list of IDs from a CSV file.

    Coerces to int if column_name is "id", otherwise coerces to string.
    """

    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        return [
            int(row[column_name]) if column_name == "id" else str(row[column_name])
            for row in reader
        ]


async def async_batch_processor(
    func: Callable[..., Any], items: list[Any], batch_size: int = 50
) -> list[Any]:
    """
    Async function that processes items in batches with asyncio.gather.

    Args:
        batch_size: Number of items per batch
    """

    # Create batches
    batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
    # Process batches sequentially, items within batch concurrently
    results = []
    for batch_num, batch in enumerate(batches, 1):
        print(f"Processing batch {batch_num}/{len(batches)}: {len(batch)} items")
        # Process all items in current batch concurrently
        tasks = [func(item) for item in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

    return results
