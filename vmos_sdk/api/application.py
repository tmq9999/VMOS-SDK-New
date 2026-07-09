"""VMOS Cloud Application Management API.

Endpoints cho quản lý ứng dụng trên cloud phone instances.
Ref: vmoscloud-api.txt Section 3.
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class ApplicationAPI:
    """Application Management API."""

    def __init__(self, http) -> None:
        self._http = http

    def install(self, apps: list[dict]) -> VmosResponse:
        """Install one or more apps on one or more instances (async).
        Each app item: {"appId": int, "padCodes": [str], "appName"?: str,
        "pkgName"?: str, "isGrantAllPerm"?: bool}.
        POST /vcpcloud/api/padApi/installApp
        """
        return self._http.post(f"{_PREFIX}/installApp", {"apps": apps})

    def uninstall(
        self, pad_code_list: list[str], apk_package_list: list[str]
    ) -> VmosResponse:
        """Uninstall app. POST /vcpcloud/api/padApi/uninstallApp"""
        return self._http.post(
            f"{_PREFIX}/uninstallApp",
            {"padCodeList": pad_code_list, "apkPackageList": apk_package_list},
        )

    def start(self, pad_codes: list[str], package_name: str) -> VmosResponse:
        """Start app. POST /vcpcloud/api/padApi/startApp"""
        return self._http.post(
            f"{_PREFIX}/startApp",
            {"padCodes": pad_codes, "pkgName": package_name},
        )

    def stop(self, pad_codes: list[str], package_name: str) -> VmosResponse:
        """Stop app. POST /vcpcloud/api/padApi/stopApp"""
        return self._http.post(
            f"{_PREFIX}/stopApp",
            {"padCodes": pad_codes, "pkgName": package_name},
        )

    def restart_app(
        self, pad_codes: list[str], package_name: str
    ) -> VmosResponse:
        """Restart app. POST /vcpcloud/api/padApi/restartApp"""
        return self._http.post(
            f"{_PREFIX}/restartApp",
            {"padCodes": pad_codes, "pkgName": package_name},
        )

    def list_installed(
        self, pad_codes: list[str], *, app_name: str | None = None
    ) -> VmosResponse:
        """Instance installed app list query.
        POST /vcpcloud/api/padApi/listInstalledApp
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if app_name is not None:
            body["appName"] = app_name
        return self._http.post(f"{_PREFIX}/listInstalledApp", body)

    def upload_file(
        self,
        pad_codes: list[str],
        *,
        url: str | None = None,
        auto_install: int | None = None,
        file_unique_id: str | None = None,
        customize_file_path: str | None = None,
        file_name: str | None = None,
        package_name: str | None = None,
        md5: str | None = None,
        is_authorization: bool | None = None,
        icon_path: str | None = None,
    ) -> VmosResponse:
        """Upload file via URL. POST /vcpcloud/api/padApi/uploadFileV3"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if url is not None:
            body["url"] = url
        if auto_install is not None:
            body["autoInstall"] = auto_install
        if file_unique_id is not None:
            body["fileUniqueId"] = file_unique_id
        if customize_file_path is not None:
            body["customizeFilePath"] = customize_file_path
        if file_name is not None:
            body["fileName"] = file_name
        if package_name is not None:
            body["packageName"] = package_name
        if md5 is not None:
            body["md5"] = md5
        if is_authorization is not None:
            body["isAuthorization"] = is_authorization
        if icon_path is not None:
            body["iconPath"] = icon_path
        return self._http.post(f"{_PREFIX}/uploadFileV3", body)

    def upload_to_cloud_storage(self, file_path: str) -> VmosResponse:
        """Upload file to cloud storage. POST /vcpcloud/api/padApi/uploadFile

        Note: File body is NOT signed (V2 bodyOrQuery is empty string).
        """
        # File upload requires multipart/form-data, handled separately
        import os

        with open(file_path, "rb") as f:
            file_name = os.path.basename(file_path)
            # V2 signing: file uploads use empty body for signing
            from vmos_sdk.auth import v2_headers
            from vmos_sdk.utils import unix_timestamp

            path = f"{_PREFIX}/uploadFile"
            ts = unix_timestamp()
            headers = v2_headers(
                self._http._config.access_key,
                self._http._config.secret_key,
                path,
                "",  # Empty for file uploads
                content_type="",
            )
            import requests as req

            resp = req.post(
                self._http._config.base_url + path,
                headers=headers,
                files={"file": (file_name, f)},
                timeout=self._http._config.timeout,
            )
            return VmosResponse.from_dict(resp.json())

    def delete_cloud_files(
        self, files: list[str] | None = None, urls: list[str] | None = None
    ) -> VmosResponse:
        """Delete cloud storage files. POST /vcpcloud/api/padApi/deleteOssFiles"""
        body: dict[str, Any] = {}
        if files is not None:
            body["files"] = files
        if urls is not None:
            body["urls"] = urls
        return self._http.post(f"{_PREFIX}/deleteOssFiles", body)

    def query_user_files(self) -> VmosResponse:
        """Query user file list. POST /vcpcloud/api/padApi/selectFiles"""
        return self._http.post(f"{_PREFIX}/selectFiles", {})
