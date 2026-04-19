import asyncio
from app.tasks.processing import process_dataset_sync
from app.agents.pipeline import run_pipeline

# Mock schema info
schema = {
    "columns": [],
    "sample_rows": []
}

async def main():
    print("Testing processing...")
    # we don't have dataset_id so we will just run the pipeline with the real path
    res = await run_pipeline(
        "Show me total transaction amount by location",
        "mock-id",
        "../bank_transactions_data_2 (1).csv",
        "csv",
        schema
    )
    print("Pipeline result:", res)

asyncio.run(main())
