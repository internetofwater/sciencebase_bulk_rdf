# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

from typing import Literal, TypedDict

# Types which represent the JSON response from
# https://www.sciencebase.gov/catalog/items/get?q=&filter=systemType%3DData+Release&format=json&max=1000


class CatalogSchema(TypedDict):
    nextlink: dict[Literal["url"], str]
    total: int
    took: str
    items: list["ItemInCatalogSchema"]


class ItemInCatalogSchema(TypedDict):
    link: dict[Literal["url"], str]
    title: str
    summary: str
    hasChildren: bool
