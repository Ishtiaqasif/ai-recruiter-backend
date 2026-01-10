import asyncio
from src.services.prototype_seeding import seed_prototype_data_if_needed
import os

# For manual seeding, we temporarily force enable it
os.environ["ENABLE_SAMPLE_SEEDING"] = "true"

if __name__ == "__main__":
    asyncio.run(seed_prototype_data_if_needed())
