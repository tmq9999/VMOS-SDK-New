"""VMOS Cloud SDK utility functions."""

from __future__ import annotations

import json
import time


def unix_timestamp() -> str:
    """Return current unix timestamp as 10-digit string (seconds)."""
    return str(int(time.time()))


def compact_json(data: dict | list | None) -> str:
    """Serialize to compact JSON matching VMOS signing requirements.

    V2 signing: "sign exactly what you send — no re-order, no whitespace strip"
    """
    if data is None:
        return ""
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def build_property_list(
    properties: dict[str, str] | list[dict] | None,
) -> list[dict] | None:
    """Convert a dict of {name: value} into VMOS property list format.

    Accepts either:
        - dict: {"IMEI": "123456", "ICCID": "789"}
        - list: [{"propertiesName": "IMEI", "propertiesValue": "123456"}]

    Returns VMOS format list of {"propertiesName": ..., "propertiesValue": ...}
    """
    if properties is None:
        return None
    if isinstance(properties, list):
        return properties
    return [
        {"propertiesName": name, "propertiesValue": value}
        for name, value in properties.items()
    ]
