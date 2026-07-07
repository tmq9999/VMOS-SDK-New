"""VMOS Cloud Phone Management API.

Endpoints cho quản lý cloud phone: tạo, mua, gia hạn, danh sách, thông tin.
Ref: vmoscloud-api.txt Section 5.
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class CloudPhoneAPI:
    """Cloud Phone Management API."""

    def __init__(self, http) -> None:
        self._http = http

    def create(
        self,
        good_id: str,
        good_num: int,
        *,
        android_version_name: str | None = None,
        auto_renew: bool | None = None,
        equipment_id: str | None = None,
        country_code: str | None = None,
    ) -> VmosResponse:
        """Create/renew cloud phone. POST /vcpcloud/api/padApi/createMoneyOrder"""
        body: dict[str, Any] = {"goodId": good_id, "goodNum": good_num}
        if android_version_name is not None:
            body["androidVersionName"] = android_version_name
        if auto_renew is not None:
            body["autoRenew"] = auto_renew
        if equipment_id is not None:
            body["equipmentId"] = equipment_id
        if country_code is not None:
            body["countryCode"] = country_code
        return self._http.post(f"{_PREFIX}/createMoneyOrder", body)

    def list_phones(
        self,
        *,
        pad_code: str | None = None,
        equipment_ids: list[str] | None = None,
    ) -> VmosResponse:
        """Cloud phone list. POST /vcpcloud/api/padApi/userPadList"""
        body: dict[str, Any] = {}
        if pad_code is not None:
            body["padCode"] = pad_code
        if equipment_ids is not None:
            body["equipmentIds"] = equipment_ids
        return self._http.post(f"{_PREFIX}/userPadList", body)

    def get_info(self, pad_code: str) -> VmosResponse:
        """Cloud phone info query. POST /vcpcloud/api/padApi/padInfo"""
        return self._http.post(f"{_PREFIX}/padInfo", {"padCode": pad_code})

    def get_sku_list(
        self,
        *,
        android_version: str | None = None,
        good_ids: str | None = None,
    ) -> VmosResponse:
        """SKU package list. GET /vcpcloud/api/padApi/getCloudGoodList"""
        params: dict[str, Any] = {}
        if android_version is not None:
            params["androidVersion"] = android_version
        if good_ids is not None:
            params["goodIds"] = good_ids
        return self._http.get(f"{_PREFIX}/getCloudGoodList", params or None)

    def get_image_versions(self, pad_code: str) -> VmosResponse:
        """Android image version list.
        POST /vcpcloud/api/padApi/imageVersionList
        """
        return self._http.post(f"{_PREFIX}/imageVersionList", {"padCode": pad_code})

    def presale_purchase(
        self,
        good_id: str,
        good_num: int,
        *,
        android_version_name: str | None = None,
        auto_renew: bool | None = None,
        country_code: str | None = None,
    ) -> VmosResponse:
        """Device presale purchase.
        POST /vcpcloud/api/padApi/createMoneyProOrder
        """
        body: dict[str, Any] = {"goodId": good_id, "goodNum": good_num}
        if android_version_name is not None:
            body["androidVersionName"] = android_version_name
        if auto_renew is not None:
            body["autoRenew"] = auto_renew
        if country_code is not None:
            body["countryCode"] = country_code
        return self._http.post(f"{_PREFIX}/createMoneyProOrder", body)

    def query_presale_orders(
        self,
        *,
        pro_buy_status: int | None = None,
        order_id: str | None = None,
    ) -> VmosResponse:
        """Query presale order result details.
        POST /vcpcloud/api/padApi/queryProOrderList
        """
        body: dict[str, Any] = {}
        if pro_buy_status is not None:
            body["proBuyStatus"] = pro_buy_status
        if order_id is not None:
            body["orderId"] = order_id
        return self._http.post(f"{_PREFIX}/queryProOrderList", body)

    # === Timing Device (On-demand instances) ===

    def create_timing_order(
        self, good_id: str, good_num: int
    ) -> VmosResponse:
        """Create timing device order.
        POST /vcpcloud/api/padApi/createByTimingOrder
        """
        return self._http.post(
            f"{_PREFIX}/createByTimingOrder",
            {"goodId": good_id, "goodNum": good_num},
        )

    def timing_power_on(
        self,
        pad_codes: list[str],
        *,
        def_code: str | None = None,
        net_storage_res_unit_code: str | None = None,
    ) -> VmosResponse:
        """Timing device power on. POST /vcpcloud/api/padApi/timingPadOn"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if def_code is not None:
            body["defCode"] = def_code
        if net_storage_res_unit_code is not None:
            body["netStorageResUnitCode"] = net_storage_res_unit_code
        return self._http.post(f"{_PREFIX}/timingPadOn", body)

    def timing_power_off(
        self,
        pad_codes: list[str],
        *,
        is_back_up: bool | None = None,
        remark: str | None = None,
    ) -> VmosResponse:
        """Timing device power off. POST /vcpcloud/api/padApi/timingPadOff"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if is_back_up is not None:
            body["isBackUp"] = is_back_up
        if remark is not None:
            body["remark"] = remark
        return self._http.post(f"{_PREFIX}/timingPadOff", body)

    def timing_destroy(self, pad_codes: list[str]) -> VmosResponse:
        """Timing device destroy. POST /vcpcloud/api/padApi/timingPadDel"""
        return self._http.post(f"{_PREFIX}/timingPadDel", {"padCodes": pad_codes})

    def get_storage_packages(self) -> VmosResponse:
        """Storage resource package list.
        GET /vcpcloud/api/padApi/vcTimingBackupList
        """
        return self._http.get(f"{_PREFIX}/vcTimingBackupList")
