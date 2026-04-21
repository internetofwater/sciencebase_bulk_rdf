# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

import asyncio
import httpx
from catalog_types import CatalogSchema
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
logging.getLogger("httpx").disabled = True


async def main():
    # we fetch with max = 1000 since that is the maximum amount of items that can be returned in a single request
    base_url = "https://www.sciencebase.gov/catalog/items/get?q=&filter=systemType%3DData+Release&format=json&max=1000"
    catalog_url = base_url

    offset = 0
    while True:
        async with httpx.AsyncClient() as client:
            LOGGER.info(f"Fetching dataset list with offset {offset} at {catalog_url}")
            response = await client.get(catalog_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch dataset list: {response.status_code}")
            response.raise_for_status()
            as_json: CatalogSchema = response.json()

            has_next = as_json.get("nextlink")
            if not has_next:
                # if there is no nextlink then we are at the end of the dataset and thus we can stop
                break

            for item in as_json["items"]:
                _item_url = item["link"]["url"]

            offset += 1000
            catalog_url = f"{base_url}&offset={offset}"


if __name__ == "__main__":
    asyncio.run(main())
    LOGGER.info("Done")
