"""VMOS Cloud Python SDK.

SDK hoàn chỉnh cho VMOS Cloud OpenAPI, hỗ trợ quản lý cloud phone instances,
ứng dụng, proxy, RPA automation và nhiều tính năng khác.

Sử dụng:
    from vmos_sdk import VmosClient

    client = VmosClient(
        access_key="your_access_key",
        secret_key="your_secret_key",
    )
    result = client.instance.restart(pad_codes=["AC22030022693"])
"""

from vmos_sdk.client import VmosClient
from vmos_sdk.config import Config
from vmos_sdk.exceptions import (
    VmosAuthError,
    VmosError,
    VmosInstanceError,
    VmosRateLimitError,
    VmosRequestError,
)

__version__ = "1.0.0"
__all__ = [
    "VmosClient",
    "Config",
    "VmosError",
    "VmosAuthError",
    "VmosInstanceError",
    "VmosRateLimitError",
    "VmosRequestError",
]
