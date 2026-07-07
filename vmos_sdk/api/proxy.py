"""VMOS Cloud Proxy Management API.

Endpoints cho quản lý proxy (static residential + dynamic).
Ref: vmoscloud-api.txt Section 7 & 8.
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class ProxyAPI:
    """Proxy Management API (Static Residential + Dynamic)."""

    def __init__(self, http) -> None:
        self._http = http

    # ========== Static Residential Proxy ==========

    def get_static_products(self) -> VmosResponse:
        """Get static residential product list.
        GET /vcpcloud/api/padApi/proxyGoodList
        """
        return self._http.get(f"{_PREFIX}/proxyGoodList")

    def get_static_regions(self) -> VmosResponse:
        """Get static residential supported countries/cities.
        GET /vcpcloud/api/padApi/getProxyRegion
        """
        return self._http.get(f"{_PREFIX}/getProxyRegion")

    def purchase_static(
        self,
        proxy_good_id: str,
        num: int,
        *,
        region: str | None = None,
        country: str | None = None,
        proxy_address: str | None = None,
        auto_renew: bool | None = None,
    ) -> VmosResponse:
        """Static residential product purchase.
        POST /vcpcloud/api/padApi/createProxyOrder
        """
        body: dict[str, Any] = {"proxyGoodId": proxy_good_id, "num": num}
        if region is not None:
            body["region"] = region
        if country is not None:
            body["country"] = country
        if proxy_address is not None:
            body["proxyAddress"] = proxy_address
        if auto_renew is not None:
            body["autoRenew"] = auto_renew
        return self._http.post(f"{_PREFIX}/createProxyOrder", body)

    def get_static_orders(
        self, *, page: int = 1, rows: int = 20
    ) -> VmosResponse:
        """Static residential proxy order details.
        POST /vcpcloud/api/padApi/selectProxyOrderList
        """
        return self._http.post(
            f"{_PREFIX}/selectProxyOrderList", {"page": page, "rows": rows}
        )

    def renew_static(
        self,
        proxy_good_id: str,
        proxy_ips: list[str],
        *,
        auto_renew: bool | None = None,
    ) -> VmosResponse:
        """Static residential proxy renewal.
        POST /vcpcloud/api/padApi/createRenewProxyOrder
        """
        body: dict[str, Any] = {
            "proxyGoodId": proxy_good_id,
            "proxyIps": proxy_ips,
        }
        if auto_renew is not None:
            body["autoRenew"] = auto_renew
        return self._http.post(f"{_PREFIX}/createRenewProxyOrder", body)

    def query_static_list(
        self, *, current: int = 1, size: int = 20
    ) -> VmosResponse:
        """Query static residential proxy list.
        POST /vcpcloud/api/padApi/queryProxyList
        """
        return self._http.post(
            f"{_PREFIX}/queryProxyList", {"current": current, "size": size}
        )

    # ========== Dynamic Proxy ==========

    def get_dynamic_products(self) -> VmosResponse:
        """Query dynamic proxy product list.
        GET /vcpcloud/api/padApi/getDynamicGoodService
        """
        return self._http.get(f"{_PREFIX}/getDynamicGoodService")

    def get_dynamic_regions(self) -> VmosResponse:
        """Query dynamic proxy region list.
        GET /vcpcloud/api/padApi/getDynamicProxyRegion
        """
        return self._http.get(f"{_PREFIX}/getDynamicProxyRegion")

    def get_dynamic_balance(self) -> VmosResponse:
        """Get dynamic proxy current traffic balance.
        GET /vcpcloud/api/padApi/queryCurrentTrafficBalance
        """
        return self._http.get(f"{_PREFIX}/queryCurrentTrafficBalance")

    def get_supported_servers(self) -> VmosResponse:
        """Query supported server regions.
        GET /vcpcloud/api/padApi/getDynamicProxyHost
        """
        return self._http.get(f"{_PREFIX}/getDynamicProxyHost")

    def purchase_dynamic(
        self,
        good_id: str,
        good_num: int,
        *,
        auto_renew_order: bool | None = None,
    ) -> VmosResponse:
        """Purchase dynamic proxy traffic package.
        POST /vcpcloud/api/padApi/buyDynamicProxy
        """
        body: dict[str, Any] = {"goodId": good_id, "goodNum": good_num}
        if auto_renew_order is not None:
            body["autoRenewOrder"] = auto_renew_order
        return self._http.post(f"{_PREFIX}/buyDynamicProxy", body)

    def create_dynamic(
        self,
        *,
        city: str | None = None,
        country_code: str | None = None,
        good_num: int | None = None,
        proxy_host: str | None = None,
        proxy_type: str | None = None,
        proxy_use_type: str | None = None,
        state: str | None = None,
        time: int | None = None,
    ) -> VmosResponse:
        """Create dynamic proxy.
        POST /vcpcloud/api/padApi/createProxy
        """
        body: dict[str, Any] = {}
        if city is not None:
            body["city"] = city
        if country_code is not None:
            body["countryCode"] = country_code
        if good_num is not None:
            body["goodNum"] = good_num
        if proxy_host is not None:
            body["proxyHost"] = proxy_host
        if proxy_type is not None:
            body["proxyType"] = proxy_type
        if proxy_use_type is not None:
            body["proxyUseType"] = proxy_use_type
        if state is not None:
            body["state"] = state
        if time is not None:
            body["time"] = time
        return self._http.post(f"{_PREFIX}/createProxy", body)

    def get_dynamic_list(
        self, *, page: int = 1, rows: int = 20
    ) -> VmosResponse:
        """Query dynamic proxy list.
        GET /vcpcloud/api/padApi/getProxys
        """
        return self._http.get(
            f"{_PREFIX}/getProxys", {"page": page, "rows": rows}
        )

    def get_dynamic_orders(
        self,
        *,
        page: int = 1,
        rows: int = 20,
        complete_start_time: str | None = None,
        complete_end_time: str | None = None,
    ) -> VmosResponse:
        """Query dynamic proxy order list.
        POST /vcpcloud/api/padApi/getDynamicProxyOrders
        """
        body: dict[str, Any] = {"page": page, "rows": rows}
        if complete_start_time is not None:
            body["completeStartTime"] = complete_start_time
        if complete_end_time is not None:
            body["completeEndTime"] = complete_end_time
        return self._http.post(f"{_PREFIX}/getDynamicProxyOrders", body)

    def configure_for_instance(
        self,
        pad_codes: list[str],
        *,
        set_proxy_flag: bool | None = None,
        proxy_ids: list[str] | None = None,
    ) -> VmosResponse:
        """Configure dynamic proxy for cloud phone instances.
        POST /vcpcloud/api/padApi/batchPadConfigProxy
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if set_proxy_flag is not None:
            body["setProxyFlag"] = set_proxy_flag
        if proxy_ids is not None:
            body["proxyIds"] = proxy_ids
        return self._http.post(f"{_PREFIX}/batchPadConfigProxy", body)

    def query_batch_proxy_task(self, task_id: str) -> VmosResponse:
        """Query batch instance set proxy task.
        POST /vcpcloud/api/padApi/selectBatchPadProxyTask
        """
        return self._http.post(
            f"{_PREFIX}/selectBatchPadProxyTask", {"taskId": task_id}
        )

    def get_auto_renew_info(self) -> VmosResponse:
        """Query dynamic proxy auto-renewal info.
        GET /vcpcloud/api/padApi/getDynamicProxyAutomaticRenewal
        """
        return self._http.get(f"{_PREFIX}/getDynamicProxyAutomaticRenewal")

    def set_auto_renew(
        self, *, auto_renew_order: bool | None = None
    ) -> VmosResponse:
        """Set dynamic proxy auto-renewal switch.
        POST /vcpcloud/api/padApi/setAutoRenewSwitch
        """
        body: dict[str, Any] = {}
        if auto_renew_order is not None:
            body["autoRenewOrder"] = auto_renew_order
        return self._http.post(f"{_PREFIX}/setAutoRenewSwitch", body)

    def delete_dynamic(self, ids: list[str]) -> VmosResponse:
        """Delete dynamic proxy.
        POST /vcpcloud/api/padApi/delProxyByIds
        """
        return self._http.post(f"{_PREFIX}/delProxyByIds", {"ids": ids})
