"""VMOS Cloud SDK HTTP Client.

Central HTTP client that handles authentication, request signing,
retries, and response parsing for all API modules.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from vmos_sdk.auth import v2_headers, v4_headers
from vmos_sdk.config import Config
from vmos_sdk.exceptions import VmosNetworkError, raise_for_error_code
from vmos_sdk.models import VmosResponse
from vmos_sdk.utils import compact_json

logger = logging.getLogger("vmos_sdk")


class _HttpClient:
    """Internal HTTP client with signing and retry logic."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._session = requests.Session()
        self._session.headers["User-Agent"] = config.user_agent

    def post(
        self,
        path: str,
        data: dict | None = None,
        *,
        raw_response: bool = False,
    ) -> VmosResponse:
        """Send signed POST request.

        Args:
            path: API endpoint path (e.g. "/vcpcloud/api/padApi/restart").
            data: Request body as dict.
            raw_response: If True, skip error code checking.

        Returns:
            VmosResponse with parsed data.
        """
        body = compact_json(data) if data else ""
        headers = self._build_headers(path, body)
        url = self._config.base_url + path

        response_json = self._execute_with_retry("POST", url, headers, body)

        result = VmosResponse.from_dict(response_json)
        if not raw_response:
            raise_for_error_code(result.code, result.msg, result.ts)
        return result

    def get(
        self,
        path: str,
        params: dict | None = None,
        *,
        raw_response: bool = False,
    ) -> VmosResponse:
        """Send signed GET request.

        Args:
            path: API endpoint path.
            params: Query parameters as dict.
            raw_response: If True, skip error code checking.

        Returns:
            VmosResponse with parsed data.
        """
        query = (
            "&".join(f"{k}={v}" for k, v in params.items())
            if params
            else ""
        )
        headers = self._build_headers(path, query, is_get=True)
        url = self._config.base_url + path
        if query:
            url += f"?{query}"

        response_json = self._execute_with_retry("GET", url, headers)

        result = VmosResponse.from_dict(response_json)
        if not raw_response:
            raise_for_error_code(result.code, result.msg, result.ts)
        return result

    def _build_headers(
        self, path: str, body_or_query: str, *, is_get: bool = False
    ) -> dict[str, str]:
        """Build authentication headers based on signing version."""
        if self._config.signing_version == "v2":
            content_type = "" if is_get else "application/json"
            return v2_headers(
                self._config.access_key,
                self._config.secret_key,
                path,
                body_or_query,
                content_type=content_type,
            )
        else:
            return v4_headers(
                self._config.access_key,
                self._config.secret_key,
                body_or_query,
            )

    def _execute_with_retry(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: str | None = None,
    ) -> dict:
        """Execute HTTP request with retry logic."""
        last_error: Exception | None = None
        for attempt in range(self._config.max_retries):
            try:
                if method == "POST":
                    resp = self._session.request(
                        method,
                        url,
                        headers=headers,
                        data=body.encode("utf-8") if body else None,
                        timeout=self._config.timeout,
                    )
                else:
                    resp = self._session.request(
                        method,
                        url,
                        headers=headers,
                        timeout=self._config.timeout,
                    )

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(
                    "Connection error (attempt %d/%d): %s",
                    attempt + 1,
                    self._config.max_retries,
                    e,
                )
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(
                    "Timeout (attempt %d/%d): %s",
                    attempt + 1,
                    self._config.max_retries,
                    e,
                )
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors
                if resp.status_code < 500:
                    try:
                        return resp.json()
                    except json.JSONDecodeError:
                        raise VmosNetworkError(
                            code=resp.status_code,
                            message=resp.text,
                        ) from e
                last_error = e
                logger.warning(
                    "HTTP %d (attempt %d/%d): %s",
                    resp.status_code,
                    attempt + 1,
                    self._config.max_retries,
                    e,
                )

            # Exponential backoff
            if attempt < self._config.max_retries - 1:
                wait = 2**attempt
                logger.info("Retrying in %ds...", wait)
                time.sleep(wait)

        raise VmosNetworkError(
            code=0, message=f"Request failed after {self._config.max_retries} retries: {last_error}"
        )

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()


class VmosClient:
    """VMOS Cloud API Client.

    Main entry point for all VMOS Cloud API operations.

    Usage:
        client = VmosClient(access_key="...", secret_key="...")
        result = client.instance.restart(pad_codes=["AC22030022693"])
        apps = client.app.list_installed(pad_codes=["AC22030022693"])
    """

    def __init__(
        self,
        access_key: str = "",
        secret_key: str = "",
        *,
        base_url: str = "https://api.vmoscloud.com",
        timeout: int = 30,
        max_retries: int = 3,
        signing_version: str = "v2",
        config: Config | None = None,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = Config(
                access_key=access_key,
                secret_key=secret_key,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                signing_version=signing_version,
            )
        self._config.validate()
        self._http = _HttpClient(self._config)

        # Lazy-init API modules
        self._instance: Any = None
        self._app: Any = None
        self._cloud_phone: Any = None
        self._cloud_space: Any = None
        self._task: Any = None
        self._proxy: Any = None
        self._email: Any = None
        self._automation: Any = None
        self._account_matrix: Any = None
        self._sdk_token: Any = None

    # === API Module Properties (lazy-loaded) ===

    @property
    def instance(self):
        """Instance Management API."""
        if self._instance is None:
            from vmos_sdk.api.instance import InstanceAPI
            self._instance = InstanceAPI(self._http)
        return self._instance

    @property
    def app(self):
        """Application Management API."""
        if self._app is None:
            from vmos_sdk.api.application import ApplicationAPI
            self._app = ApplicationAPI(self._http)
        return self._app

    @property
    def cloud_phone(self):
        """Cloud Phone Management API."""
        if self._cloud_phone is None:
            from vmos_sdk.api.cloud_phone import CloudPhoneAPI
            self._cloud_phone = CloudPhoneAPI(self._http)
        return self._cloud_phone

    @property
    def cloud_space(self):
        """Cloud Space Management API."""
        if self._cloud_space is None:
            from vmos_sdk.api.cloud_space import CloudSpaceAPI
            self._cloud_space = CloudSpaceAPI(self._http)
        return self._cloud_space

    @property
    def task(self):
        """Task Management API."""
        if self._task is None:
            from vmos_sdk.api.task import TaskAPI
            self._task = TaskAPI(self._http)
        return self._task

    @property
    def proxy(self):
        """Proxy Management API (static + dynamic)."""
        if self._proxy is None:
            from vmos_sdk.api.proxy import ProxyAPI
            self._proxy = ProxyAPI(self._http)
        return self._proxy

    @property
    def email(self):
        """Email Verification Service API."""
        if self._email is None:
            from vmos_sdk.api.email import EmailAPI
            self._email = EmailAPI(self._http)
        return self._email

    @property
    def automation(self):
        """Flow Automation (RPA) API."""
        if self._automation is None:
            from vmos_sdk.api.automation import AutomationAPI
            self._automation = AutomationAPI(self._http)
        return self._automation

    @property
    def account_matrix(self):
        """Account Matrix API."""
        if self._account_matrix is None:
            from vmos_sdk.api.account_matrix import AccountMatrixAPI
            self._account_matrix = AccountMatrixAPI(self._http)
        return self._account_matrix

    @property
    def sdk_token(self):
        """SDK Token API."""
        if self._sdk_token is None:
            from vmos_sdk.api.sdk_token import SdkTokenAPI
            self._sdk_token = SdkTokenAPI(self._http)
        return self._sdk_token

    def close(self) -> None:
        """Close the HTTP session and release resources."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
