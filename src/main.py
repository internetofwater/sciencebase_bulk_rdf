# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

import asyncio
import json
import sys
import httpx
from catalog_item_to_rdf import catalog_item_to_jsonld
from catalog_item_types import CatalogItem
from catalog_types import CatalogSchema
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
logging.getLogger("httpx").disabled = True


async def main():
    MAX_ITEMS_PER_PAGE = 1000
    base_url = f"https://www.sciencebase.gov/catalog/items/get?q=&filter=systemType%3DData+Release&format=json&max={MAX_ITEMS_PER_PAGE}"
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
                item_url = item["link"]["url"]
                item_url_response = await client.get(f"{item_url}?format=json")
                item_url_response.raise_for_status()
                try:
                    item_json: CatalogItem = item_url_response.json()
                except json.decoder.JSONDecodeError as e:
                    msg = f"Failed to decode JSON {item_url_response.text}"
                    raise ValueError(msg) from e

                as_jsonld = catalog_item_to_jsonld(item_json)
                print(json.dumps(as_jsonld))
                sys.exit(0)

            offset += MAX_ITEMS_PER_PAGE
            catalog_url = f"{base_url}&offset={offset}"


if __name__ == "__main__":
    asyncio.run(main())
    LOGGER.info("Done")
