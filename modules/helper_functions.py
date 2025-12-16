import csv
import asyncio
import pyarrow as pa
from pyarrow import Table
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
    func: Callable[..., Any],
    items: list[Any],
    batch_size: int = 50,
    final_processor: Callable[..., Any] | None = None,
) -> list[Any]:
    """
    Async function that processes items in batches with asyncio.gather.

    Args:
        func: Async function to apply to each item
        items: List of items to process
        batch_size: Number of items per batch
        final_processor: Optional function to process each batch's results.
                        If it returns None, that batch is skipped.
                        If it returns a list, results are extended.
                        Otherwise, the return value is appended.

    Returns:
        List of processed results from all batches.
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

        # Apply final processor to this batch if provided
        if final_processor is not None:
            processed = final_processor(batch_results)

            # Handle None - skip this batch
            if processed is None:
                continue

            # If it's a list, extend; otherwise append
            if isinstance(processed, list):
                results.extend(processed)
            else:
                results.append(processed)
        else:
            results.extend(batch_results)

    return results


def import_dictlist_to_pyarrow(data: list[dict[str, Any]]) -> Table:
    """Read a list of dictionaries into a PyArrow table"""

    return pa.Table.from_pylist(data)
