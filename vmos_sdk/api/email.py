"""VMOS Cloud Email Verification Service API.

Ref: vmoscloud-api.txt Section 6.
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class EmailAPI:
    """Email Verification Service API."""

    def __init__(self, http) -> None:
        self._http = http

    def get_service_list(self) -> VmosResponse:
        """Get email service list.
        GET /vcpcloud/api/padApi/getEmailServiceList
        """
        return self._http.get(f"{_PREFIX}/getEmailServiceList")

    def get_types_and_stock(self, service_id: str) -> VmosResponse:
        """Get email type and remaining stock.
        GET /vcpcloud/api/padApi/getEmailTypeList
        """
        return self._http.get(
            f"{_PREFIX}/getEmailTypeList", {"serviceId": service_id}
        )

    def create_order(
        self, service_id: str, email_type_id: str, good_num: int
    ) -> VmosResponse:
        """Create email purchase order.
        POST /vcpcloud/api/padApi/createEmailOrder
        """
        return self._http.post(
            f"{_PREFIX}/createEmailOrder",
            {
                "serviceId": service_id,
                "emailTypeId": email_type_id,
                "goodNum": good_num,
            },
        )

    def get_purchased_list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        service_id: str | None = None,
        email: str | None = None,
        status: int | None = None,
    ) -> VmosResponse:
        """Query purchased email list.
        GET /vcpcloud/api/padApi/getEmailOrder
        """
        params: dict[str, Any] = {"page": page, "size": size}
        if service_id is not None:
            params["serviceId"] = service_id
        if email is not None:
            params["email"] = email
        if status is not None:
            params["status"] = status
        return self._http.get(f"{_PREFIX}/getEmailOrder", params)

    def get_verification_code(self, order_id: str) -> VmosResponse:
        """Refresh and get email verification code.
        GET /vcpcloud/api/padApi/getEmailCode
        """
        return self._http.get(
            f"{_PREFIX}/getEmailCode", {"orderId": order_id}
        )
