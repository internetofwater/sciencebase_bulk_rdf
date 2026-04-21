# Copyright 2026 Lincoln Institute of Land Policy
# SPDX-License-Identifier: MIT

from typing import Any, Dict
import uuid

from catalog_item_types import (
    CatalogItem,
    CatalogItemBoundingBox,
    CatalogItemDistributionLink,
    CatalogItemIdentifier,
)


# ----------------------------
# BBOX → WKT (GeoSPARQL)
# ----------------------------


def bbox_to_wkt(bbox: CatalogItemBoundingBox) -> str:
    """
    Convert bounding box → WKT Polygon (GeoSPARQL-compatible)
    WKT format:
    POLYGON((x1 y1, x2 y2, ...))
    """

    minx = bbox["minX"]
    miny = bbox["minY"]
    maxx = bbox["maxX"]
    maxy = bbox["maxY"]

    return (
        f"POLYGON(({minx} {miny}, "
        f"{maxx} {miny}, "
        f"{maxx} {maxy}, "
        f"{minx} {maxy}, "
        f"{minx} {miny}))"
    )


# ----------------------------
# Identifiers
# ----------------------------


def map_identifiers(ids: list[CatalogItemIdentifier]) -> list[str]:
    """
    Map identifiers → list of string literals (required by SHACL)
    """
    result: list[str] = []

    for ident in ids or []:
        value = ident.get("key")
        if value:
            result.append(str(value))

    return result


# ----------------------------
# Distributions (FIXED)
# ----------------------------


def map_distributions(
    dists: list[CatalogItemDistributionLink],
) -> list[Dict[str, Any]]:
    """
    Map distributions → schema:DataDownload
    """

    result: list[Dict[str, Any]] = []

    for d in dists or []:
        obj: Dict[str, Any] = {
            "@type": "schema:DataDownload",
            "schema:contentUrl": d.get("uri"),
        }

        if d.get("title"):
            obj["schema:name"] = d["title"]

        if d.get("typeLabel"):
            obj["schema:description"] = d["typeLabel"]

        # this just adds extra metadata bout the files like checksum; not really relevant imo so omitted
        # if d.get("files"):
        #     obj["schema:description"] = d["files"]

        result.append(obj)

    return result


# ----------------------------
# Main JSON-LD Transformer
# ----------------------------


def catalog_item_to_jsonld(item: CatalogItem) -> dict[str, Any]:
    """
    Convert CatalogItem → JSON-LD dataset
    using schema.org + GeoSPARQL WKT geometry
    """

    jsonld: Dict[str, Any] = {
        "@context": {
            "schema": "https://schema.org/",
            "gsp": "http://www.opengis.net/ont/geosparql#",
            "dc": "http://purl.org/dc/terms/",
        },
        "@id": f"http://geoconnex.us/catalog/{uuid.uuid4()}",
        "@type": "schema:Dataset",
    }

    # ----------------------------
    # Core dataset metadata
    # ----------------------------

    jsonld["schema:name"] = item.get("title") or "Unnamed Dataset"

    if item.get("summary"):
        jsonld["schema:description"] = item["summary"]

    if item.get("body"):
        jsonld["schema:text"] = item["body"]

    if item.get("citation"):
        jsonld["schema:citation"] = item["citation"]

    if item.get("purpose"):
        jsonld["schema:abstract"] = item["purpose"]

    if item.get("maintenanceUpdateFrequency"):
        jsonld["dc:accrualPeriodicity"] = item["maintenanceUpdateFrequency"]

    # ----------------------------
    # Identifiers
    # ----------------------------

    if item.get("identifiers"):
        jsonld["schema:identifier"] = map_identifiers(item["identifiers"])

    # ----------------------------
    # Distributions (NOW ALWAYS INCLUDED IF PRESENT)
    # ----------------------------

    if item.get("distributionLinks"):
        jsonld["schema:distribution"] = map_distributions(item["distributionLinks"])

    # ----------------------------
    # Spatial → GeoSPARQL WKT
    # ----------------------------

    spatial = item.get("spatial")

    if spatial and spatial.get("boundingBox"):
        wkt = bbox_to_wkt(spatial["boundingBox"])

        jsonld["gsp:hasGeometry"] = {
            "@type": "gsp:Geometry",
            "gsp:asWKT": {
                "@value": wkt,
                "@type": "http://www.opengis.net/ont/geosparql#wktLiteral",
            },
        }
    contacts = item.get("contacts") or []

    if contacts:
        primary = contacts[0]

        provider = {
            "@type": "schema:Organization",
            "schema:name": primary.get("organization", {}).get("displayText")
            or primary.get("name"),
        }

        if primary.get("email"):
            provider["schema:email"] = primary["email"]

        jsonld["schema:provider"] = provider
    return jsonld
