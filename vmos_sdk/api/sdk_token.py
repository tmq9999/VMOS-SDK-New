"""VMOS Cloud SDK Token API.

Ref: vmoscloud-api.txt Section 9.
"""

from __future__ import annotations

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class SdkTokenAPI:
    """SDK Token API."""

    def __init__(self, http) -> None:
        self._http = http

    def get_token_by_padcode(self, pad_code: str) -> VmosResponse:
        """Get SDK temporary token by padCode.
        POST /vcpcloud/api/padApi/stsTokenByPadCode
        """
        return self._http.post(
            f"{_PREFIX}/stsTokenByPadCode", {"padCode": pad_code}
        )

    def get_session_token(self) -> VmosResponse:
        """Get group control session token.
        GET /vcpcloud/api/padApi/getSessionToken
        """
        return self._http.get(f"{_PREFIX}/getSessionToken")

    def clear_token(self, token: str) -> VmosResponse:
        """Clear SDK authorization token.
        POST /vcpcloud/api/padApi/clearStsToken
        """
        return self._http.post(f"{_PREFIX}/clearStsToken", {"token": token})
