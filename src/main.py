# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

import asyncio
import json
import httpx
import hashlib
from pathlib import Path
from catalog_item_to_rdf import catalog_item_to_jsonld
from catalog_item_types import CatalogItem
from catalog_types import CatalogSchema
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
logging.getLogger("httpx").disabled = True

CACHE_DIR = Path("/tmp/.sciencebase-cache")


def _cache_path(url: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.json"


async def fetch_json(client: httpx.AsyncClient, url: str, cache: bool):
    """
    Fetch JSON with optional disk cache.
    """

    path = _cache_path(url)

    if cache and path.exists():
        LOGGER.info(f"Cache hit: {url}")
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    LOGGER.debug(f"Fetching: {url}")
    response = await client.get(url)
    response.raise_for_status()

    try:
        data = response.json()
    except json.decoder.JSONDecodeError as e:
        msg = f"Failed to decode JSON from {url}: {response.text}"
        raise ValueError(msg) from e

    if cache:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    return data


async def main(cache: bool = False):
    if cache:
        CACHE_DIR.mkdir(exist_ok=True)
    MAX_ITEMS_PER_PAGE = 1000
    base_url = (
        "https://www.sciencebase.gov/catalog/items/get?"
        "q=&filter=systemType%3DData+Release&format=json&max="
        f"{MAX_ITEMS_PER_PAGE}"
    )

    offset: int = 0
    catalog_url = base_url
    MAX_FAILURES = 100

    failures: dict[str, Exception] = {}

    async with httpx.AsyncClient() as client:
        while True:
            LOGGER.info(f"Fetching dataset list with offset {offset}")

            as_json: CatalogSchema = await fetch_json(client, catalog_url, cache)

            has_next = as_json.get("nextlink")
            # if there is no next link then we have iterated throughout the entire catalog
            if not has_next:
                break

            for item in as_json["items"]:
                if len(failures) >= MAX_FAILURES:
                    LOGGER.error(f"Reached max failures of {MAX_FAILURES}, exiting")
                    return

                item_url = item["link"]["url"]
                item_url_full = f"{item_url}?format=json"

                try:
                    item_json: CatalogItem = await fetch_json(
                        client, item_url_full, cache
                    )
                except Exception as e:
                    failures[item_url] = e
                    continue

                as_jsonld = catalog_item_to_jsonld(item_json, item_url)
                print(json.dumps(as_jsonld))

            offset += MAX_ITEMS_PER_PAGE
            catalog_url = f"{base_url}&offset={offset}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", action="store_true")
    args = parser.parse_args()

    if args.cache:
        LOGGER.info("Using cache")

    asyncio.run(main(args.cache))
    LOGGER.info("Done")
