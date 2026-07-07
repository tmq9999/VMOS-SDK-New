"""VMOS Cloud Space Management API.

Endpoints cho quản lý cloud storage: upload, purchase, renew, delete.
Ref: vmoscloud-api.txt Section 5 (Cloud storage phần dưới).
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class CloudSpaceAPI:
    """Cloud Space / Storage Management API."""

    def __init__(self, http) -> None:
        self._http = http

    def get_remaining_storage(self) -> VmosResponse:
        """Cloud storage remaining capacity.
        GET /vcpcloud/api/padApi/getRenewStorageInfo
        """
        return self._http.get(f"{_PREFIX}/getRenewStorageInfo")

    def get_product_list(self) -> VmosResponse:
        """Cloud storage product list.
        GET /vcpcloud/api/padApi/getVcStorageGoods
        """
        return self._http.get(f"{_PREFIX}/getVcStorageGoods")

    def purchase_expansion(
        self,
        storage_id: str,
        *,
        auto_renew_order: bool | None = None,
    ) -> VmosResponse:
        """Purchase cloud storage expansion.
        POST /vcpcloud/api/padApi/buyStorageGoods
        """
        body: dict[str, Any] = {"storageId": storage_id}
        if auto_renew_order is not None:
            body["autoRenewOrder"] = auto_renew_order
        return self._http.post(f"{_PREFIX}/buyStorageGoods", body)

    def query_renewal_details(self) -> VmosResponse:
        """Cloud storage renewal details query.
        GET /vcpcloud/api/padApi/selectAutoRenew
        """
        return self._http.get(f"{_PREFIX}/selectAutoRenew")

    def aggregate_renew(
        self, *, auto_renew_order: bool | None = None
    ) -> VmosResponse:
        """Aggregate renew cloud storage products.
        POST /vcpcloud/api/padApi/renewsStorageGoods
        """
        body: dict[str, Any] = {}
        if auto_renew_order is not None:
            body["autoRenewOrder"] = auto_renew_order
        return self._http.post(f"{_PREFIX}/renewsStorageGoods", body)

    def toggle_auto_renew(self, renew_storage_status: bool) -> VmosResponse:
        """Cloud storage auto-renewal switch.
        GET /vcpcloud/api/padApi/updateRenewStorageStatus
        """
        return self._http.get(
            f"{_PREFIX}/updateRenewStorageStatus",
            {"renewStorageStatus": renew_storage_status},
        )

    def delete_backup_data(self, backup_ids: list[str]) -> VmosResponse:
        """Delete backup resource package data.
        POST /vcpcloud/api/padApi/deleteUploadFiles
        """
        return self._http.post(
            f"{_PREFIX}/deleteUploadFiles", {"backupIds": backup_ids}
        )
