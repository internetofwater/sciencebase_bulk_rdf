# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

from typing import TypedDict

# Types which represent the JSON response from item urls like
# https://www.sciencebase.gov/catalog/item/5411deb1e4b0fe7e184a8eff?format=json
# NOTE: not all keys are represented in this schema. Some which arent relevant are
# ignored


class CatalogItemIdentifier(TypedDict):
    type: str
    scheme: str
    key: str


class CatalogItemProvenance(TypedDict):
    dataSource: str
    # iso timestamp as string
    dateCreated: str
    lastUpdated: str


class CatalogItemBoundingBox(TypedDict):
    minX: float
    minY: float
    maxX: float
    maxY: float


class CatalogItemSpatial(TypedDict):
    boundingBox: CatalogItemBoundingBox


class CatalogItemTag(TypedDict):
    type: str
    scheme: str
    name: str


class CatalogItemDistributionLink(TypedDict):
    uri: str
    title: str
    type: str
    typeLabel: str
    rel: str
    name: str
    files: str


class CatalogItem(TypedDict):
    summary: str
    identifiers: list[CatalogItemIdentifier]
    title: str
    summary: str
    body: str
    citation: str
    purpose: str
    maintenanceUpdateFrequency: str
    spatial: CatalogItemSpatial
    distributions: list[CatalogItemDistributionLink]
