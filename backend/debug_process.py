import asyncio
from app.database import async_session_factory
from app.models.dataset import Dataset
from app.tasks.processing import process_dataset_sync
from sqlalchemy import select

async def debug_process():
    async with async_session_factory() as session:
        result = await session.execute(
            select(Dataset).where(Dataset.name.like("%bank_transactions_data_2%"))
        )
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            print("Dataset not found!")
            return
            
        print(f"Dataset found: {dataset.name} ({dataset.id})")
        print(f"File Path: {dataset.file_path}")
        print(f"File Type: {dataset.file_type}")
        
        try:
            await process_dataset_sync(str(dataset.id))
            print("Processing task finished (check DB status for outcome)")
        except Exception as e:
            print(f"CRITICAL Task Failure: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_process())
