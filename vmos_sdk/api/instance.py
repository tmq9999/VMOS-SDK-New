"""VMOS Cloud Instance Management API.

Endpoints cho quản lý cloud phone instances: restart, reset, properties,
proxy, ADB commands, touch simulation, file upload, và nhiều hơn nữa.

Tất cả endpoint paths và parameter names lấy trực tiếp từ API.txt và vmoscloud-api.txt.
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse
from vmos_sdk.utils import build_property_list

_PREFIX = "/vcpcloud/api/padApi"


class InstanceAPI:
    """Instance Management API (~55 endpoints)."""

    def __init__(self, http) -> None:
        self._http = http

    # ========== Core Operations ==========

    def restart(self, pad_codes: list[str]) -> VmosResponse:
        """Restart instance(s). POST /vcpcloud/api/padApi/restart"""
        return self._http.post(f"{_PREFIX}/restart", {"padCodes": pad_codes})

    def reset(self, pad_codes: list[str]) -> VmosResponse:
        """Reset instance(s) — clears ALL data. POST /vcpcloud/api/padApi/reset"""
        return self._http.post(f"{_PREFIX}/reset", {"padCodes": pad_codes})

    def one_key_new_device(
        self,
        pad_codes: list[str],
        *,
        country_code: str | None = None,
        real_phone_template_id: int | None = None,
        android_prop: dict | None = None,
        replacement_real_adi_flag: bool | None = None,
        exclude_real_phone_template_ids: list[int] | None = None,
        certificate: str | None = None,
        wipe_data: bool | None = None,
        wipe_specific_data: list[str] | None = None,
    ) -> VmosResponse:
        """One-key new device ⭐ — clears all data and resets Android properties.
        POST /vcpcloud/api/padApi/replacePad
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if country_code is not None:
            body["countryCode"] = country_code
        if real_phone_template_id is not None:
            body["realPhoneTemplateId"] = real_phone_template_id
        if android_prop is not None:
            body["androidProp"] = android_prop
        if replacement_real_adi_flag is not None:
            body["replacementRealAdiFlag"] = replacement_real_adi_flag
        if exclude_real_phone_template_ids is not None:
            body["excludeRealPhoneTemplateIds"] = exclude_real_phone_template_ids
        if certificate is not None:
            body["certificate"] = certificate
        if wipe_data is not None:
            body["wipeData"] = wipe_data
        if wipe_specific_data is not None:
            body["wipeSpecificData"] = wipe_specific_data
        return self._http.post(f"{_PREFIX}/replacePad", body)

    def one_key_new_device_auto(
        self,
        pad_codes: list[str],
        *,
        country_code: str | None = None,
        real_phone_template_id: int | None = None,
        android_prop: dict | None = None,
        replacement_real_adi_flag: bool | None = None,
        exclude_real_phone_template_ids: list[int] | None = None,
        certificate: str | None = None,
        wipe_data: bool | None = None,
        wipe_specific_data: list[str] | None = None,
    ) -> VmosResponse:
        """One-key new device (Auto SIM/GPS/Timezone) ⭐.
        POST /vcpcloud/api/padApi/padReplaceNew
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if country_code is not None:
            body["countryCode"] = country_code
        if real_phone_template_id is not None:
            body["realPhoneTemplateId"] = real_phone_template_id
        if android_prop is not None:
            body["androidProp"] = android_prop
        if replacement_real_adi_flag is not None:
            body["replacementRealAdiFlag"] = replacement_real_adi_flag
        if exclude_real_phone_template_ids is not None:
            body["excludeRealPhoneTemplateIds"] = exclude_real_phone_template_ids
        if certificate is not None:
            body["certificate"] = certificate
        if wipe_data is not None:
            body["wipeData"] = wipe_data
        if wipe_specific_data is not None:
            body["wipeSpecificData"] = wipe_specific_data
        return self._http.post(f"{_PREFIX}/padReplaceNew", body)

    def async_cmd(
        self, pad_codes: list[str], script_content: str
    ) -> VmosResponse:
        """Async execute ADB commands ⭐. POST /vcpcloud/api/padApi/asyncCmd"""
        return self._http.post(
            f"{_PREFIX}/asyncCmd",
            {"padCodes": pad_codes, "scriptContent": script_content},
        )

    def switch_root(
        self,
        pad_codes: list[str],
        *,
        global_root: bool | None = None,
        package_name: str | None = None,
        root_status: bool | None = None,
    ) -> VmosResponse:
        """Switch root permissions. POST /vcpcloud/api/padApi/switchRoot"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if global_root is not None:
            body["globalRoot"] = global_root
        if package_name is not None:
            body["packageName"] = package_name
        if root_status is not None:
            body["rootStatus"] = root_status
        return self._http.post(f"{_PREFIX}/switchRoot", body)

    # ========== Properties ==========

    def get_properties(self, pad_code: str) -> VmosResponse:
        """Query instance properties. POST /vcpcloud/api/padApi/padProperties"""
        return self._http.post(f"{_PREFIX}/padProperties", {"padCode": pad_code})

    def batch_get_properties(self, pad_codes: list[str]) -> VmosResponse:
        """Batch query instance properties (max 200).
        POST /vcpcloud/api/padApi/batchPadProperties
        """
        return self._http.post(f"{_PREFIX}/batchPadProperties", {"padCodes": pad_codes})

    def update_properties(
        self,
        pad_codes: list[str],
        *,
        modem_persist: dict[str, str] | list[dict] | None = None,
        modem: dict[str, str] | list[dict] | None = None,
        system_persist: dict[str, str] | list[dict] | None = None,
        system: dict[str, str] | list[dict] | None = None,
        setting: dict[str, str] | list[dict] | None = None,
        oaid: dict[str, str] | list[dict] | None = None,
    ) -> VmosResponse:
        """Dynamically modify instance properties (takes effect immediately).
        POST /vcpcloud/api/padApi/updatePadProperties
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if modem_persist is not None:
            body["modemPersistPropertiesList"] = build_property_list(modem_persist)
        if modem is not None:
            body["modemPropertiesList"] = build_property_list(modem)
        if system_persist is not None:
            body["systemPersistPropertiesList"] = build_property_list(system_persist)
        if system is not None:
            body["systemPropertiesList"] = build_property_list(system)
        if setting is not None:
            body["settingPropertiesList"] = build_property_list(setting)
        if oaid is not None:
            body["oaidPropertiesList"] = build_property_list(oaid)
        return self._http.post(f"{_PREFIX}/updatePadProperties", body)

    def update_android_props(
        self,
        pad_code: str,
        props: dict[str, str],
        *,
        restart: bool = False,
    ) -> VmosResponse:
        """Modify Android modification properties (requires restart to take effect).
        POST /vcpcloud/api/padApi/updatePadAndroidProp
        """
        return self._http.post(
            f"{_PREFIX}/updatePadAndroidProp",
            {"padCode": pad_code, "props": props, "restart": restart},
        )

    def update_sim(
        self,
        pad_code: str,
        *,
        country_code: str | None = None,
        props: dict[str, str] | None = None,
    ) -> VmosResponse:
        """Modify SIM card info by country code (auto restart).
        POST /vcpcloud/api/padApi/updateSIM
        """
        body: dict[str, Any] = {"padCode": pad_code}
        if country_code is not None:
            body["countryCode"] = country_code
        if props is not None:
            body["props"] = props
        return self._http.post(f"{_PREFIX}/updateSIM", body)

    # ========== Network & Proxy ==========

    def set_wifi(
        self, pad_codes: list[str], wifi_json_list: list[dict]
    ) -> VmosResponse:
        """Modify instance WIFI properties. POST /vcpcloud/api/padApi/setWifiList"""
        return self._http.post(
            f"{_PREFIX}/setWifiList",
            {"padCodes": pad_codes, "wifiJsonList": wifi_json_list},
        )

    def check_ip(
        self,
        host: str,
        port: int,
        account: str,
        password: str,
        proxy_type: str,
        *,
        country: str | None = None,
        ip: str | None = None,
        loc: str | None = None,
        city: str | None = None,
        region: str | None = None,
        timezone: str | None = None,
    ) -> VmosResponse:
        """Smart IP proxy detection. POST /vcpcloud/api/padApi/checkIP"""
        body: dict[str, Any] = {
            "host": host,
            "port": port,
            "account": account,
            "password": password,
            "type": proxy_type,
        }
        if country is not None:
            body["country"] = country
        if ip is not None:
            body["ip"] = ip
        if loc is not None:
            body["loc"] = loc
        if city is not None:
            body["city"] = city
        if region is not None:
            body["region"] = region
        if timezone is not None:
            body["timezone"] = timezone
        return self._http.post(f"{_PREFIX}/checkIP", body)

    def set_smart_ip(
        self,
        pad_codes: list[str],
        host: str,
        port: int,
        account: str,
        password: str,
        proxy_type: str,
        mode: str,
        *,
        bypass_package_list: list[str] | None = None,
        bypass_ip_list: list[str] | None = None,
        bypass_domain_list: list[str] | None = None,
        follow_language: bool | None = None,
    ) -> VmosResponse:
        """Set smart IP — auto changes exit IP, SIM, GPS, timezone.
        POST /vcpcloud/api/padApi/smartIp
        """
        body: dict[str, Any] = {
            "padCodes": pad_codes,
            "host": host,
            "port": port,
            "account": account,
            "password": password,
            "type": proxy_type,
            "mode": mode,
        }
        if bypass_package_list is not None:
            body["bypassPackageList"] = bypass_package_list
        if bypass_ip_list is not None:
            body["bypassIpList"] = bypass_ip_list
        if bypass_domain_list is not None:
            body["bypassDomainList"] = bypass_domain_list
        if follow_language is not None:
            body["followLanguage"] = follow_language
        return self._http.post(f"{_PREFIX}/smartIp", body)

    def cancel_smart_ip(self, pad_codes: list[str]) -> VmosResponse:
        """Cancel smart IP. POST /vcpcloud/api/padApi/notSmartIp"""
        return self._http.post(f"{_PREFIX}/notSmartIp", {"padCodes": pad_codes})

    def get_task_status(self, task_id: str) -> VmosResponse:
        """Query smart IP task execution result.
        POST /vcpcloud/api/padApi/getTaskStatus
        """
        return self._http.post(f"{_PREFIX}/getTaskStatus", {"taskId": task_id})

    def set_proxy(
        self,
        pad_codes: list[str],
        *,
        ip: str | None = None,
        port: int | None = None,
        account: str | None = None,
        password: str | None = None,
        enable: bool | None = None,
        proxy_type: str | None = None,
        proxy_name: str | None = None,
        model: str | None = None,
        bypass_package_list: list[str] | None = None,
        bypass_ip_list: list[str] | None = None,
        bypass_domain_list: list[str] | None = None,
        limit_package_list: list[str] | None = None,
        limit_ip_list: list[str] | None = None,
        limit_domain_list: list[str] | None = None,
        s_uo_t: bool | None = None,
    ) -> VmosResponse:
        """Set instance proxy. POST /vcpcloud/api/padApi/setProxy"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if ip is not None:
            body["ip"] = ip
        if port is not None:
            body["port"] = port
        if account is not None:
            body["account"] = account
        if password is not None:
            body["password"] = password
        if enable is not None:
            body["enable"] = enable
        if proxy_type is not None:
            body["proxyType"] = proxy_type
        if proxy_name is not None:
            body["proxyName"] = proxy_name
        if model is not None:
            body["model"] = model
        if bypass_package_list is not None:
            body["bypassPackageList"] = bypass_package_list
        if bypass_ip_list is not None:
            body["bypassIpList"] = bypass_ip_list
        if bypass_domain_list is not None:
            body["bypassDomainList"] = bypass_domain_list
        if limit_package_list is not None:
            body["limitPackageList"] = limit_package_list
        if limit_ip_list is not None:
            body["limitIpList"] = limit_ip_list
        if limit_domain_list is not None:
            body["limitDomainList"] = limit_domain_list
        if s_uo_t is not None:
            body["sUoT"] = s_uo_t
        return self._http.post(f"{_PREFIX}/setProxy", body)

    def stop_streaming(self, pad_codes: list[str]) -> VmosResponse:
        """Stop streaming. POST /vcpcloud/api/padApi/dissolveRoom"""
        return self._http.post(f"{_PREFIX}/dissolveRoom", {"padCodes": pad_codes})

    # ========== Info & Monitoring ==========

    def get_detail(
        self,
        *,
        last_id: int | None = None,
        rows: int = 10,
        pad_codes: list[str] | None = None,
        pad_ips: list[str] | None = None,
        online: int | None = None,
        pad_status: int | None = None,
        compute_occupied: bool | None = None,
        net_storage_res_flag: int | None = None,
        brand: str | None = None,
        brand_model: str | None = None,
    ) -> VmosResponse:
        """Query cloud phone base info list (paginated).
        POST /vcpcloud/api/padApi/padDetail
        """
        body: dict[str, Any] = {"rows": rows}
        if last_id is not None:
            body["lastId"] = last_id
        if pad_codes is not None:
            body["padCodes"] = pad_codes
        if pad_ips is not None:
            body["padIps"] = pad_ips
        if online is not None:
            body["online"] = online
        if pad_status is not None:
            body["padStatus"] = pad_status
        if compute_occupied is not None:
            body["computeOccupied"] = compute_occupied
        if net_storage_res_flag is not None:
            body["netStorageResFlag"] = net_storage_res_flag
        if brand is not None:
            body["brand"] = brand
        if brand_model is not None:
            body["brandModel"] = brand_model
        return self._http.post(f"{_PREFIX}/padDetail", body)

    def get_installed_apps(self, pad_code_list: list[str]) -> VmosResponse:
        """Get all installed apps. POST /vcpcloud/api/padApi/getListInstalledApp"""
        return self._http.post(
            f"{_PREFIX}/getListInstalledApp", {"padCodeList": pad_code_list}
        )

    def list_installed_apps(
        self, pad_codes: list[str], *, app_name: str | None = None
    ) -> VmosResponse:
        """Real-time query installed apps. POST /vcpcloud/api/padApi/listInstalledApp"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if app_name is not None:
            body["appName"] = app_name
        return self._http.post(f"{_PREFIX}/listInstalledApp", body)

    def get_list_info(
        self,
        *,
        page: int | None = None,
        rows: int | None = None,
        pad_type: int | None = None,
        pad_codes: list[str] | None = None,
    ) -> VmosResponse:
        """Instance group list / instance list info.
        POST /vcpcloud/api/padApi/infos
        """
        body: dict[str, Any] = {}
        if page is not None:
            body["page"] = page
        if rows is not None:
            body["rows"] = rows
        if pad_type is not None:
            body["padType"] = pad_type
        if pad_codes is not None:
            body["padCodes"] = pad_codes
        return self._http.post(f"{_PREFIX}/infos", body)

    def get_model_info(self, pad_codes: list[str]) -> VmosResponse:
        """Batch get instance device model information (Pending Launch).
        POST /vcpcloud/api/padApi/modelInfo
        """
        return self._http.post(f"{_PREFIX}/modelInfo", {"padCodes": pad_codes})

    # ========== Screenshot & Preview ==========

    def screenshot(
        self,
        pad_codes: list[str],
        *,
        rotation: int | None = None,
        broadcast: bool | None = None,
        definition: int | None = None,
        resolution_height: int | None = None,
        resolution_width: int | None = None,
    ) -> VmosResponse:
        """Local screenshot. POST /vcpcloud/api/padApi/screenshot"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if rotation is not None:
            body["rotation"] = rotation
        if broadcast is not None:
            body["broadcast"] = broadcast
        if definition is not None:
            body["definition"] = definition
        if resolution_height is not None:
            body["resolutionHeight"] = resolution_height
        if resolution_width is not None:
            body["resolutionWidth"] = resolution_width
        return self._http.post(f"{_PREFIX}/screenshot", body)

    def get_preview_image(
        self,
        pad_codes: list[str],
        *,
        format: str | None = None,
        height: int | None = None,
        width: int | None = None,
        quality: int | None = None,
    ) -> VmosResponse:
        """Get instance real-time preview image.
        POST /vcpcloud/api/padApi/getLongGenerateUrl
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if format is not None:
            body["format"] = format
        if height is not None:
            body["height"] = height
        if width is not None:
            body["width"] = width
        if quality is not None:
            body["quality"] = quality
        return self._http.post(f"{_PREFIX}/getLongGenerateUrl", body)

    def get_screenshot_result(self, task_ids: list[int]) -> VmosResponse:
        """Get instance screenshot result (Pending Launch).
        POST /vcpcloud/api/padApi/screenshotInfo
        """
        return self._http.post(f"{_PREFIX}/screenshotInfo", {"taskIds": task_ids})

    # ========== Touch Simulation ==========

    def simulate_touch(
        self,
        pad_codes: list[str],
        width: int,
        height: int,
        point_count: int,
        positions: list[dict],
    ) -> VmosResponse:
        """Simulate touch events. POST /vcpcloud/api/padApi/simulateTouch"""
        return self._http.post(
            f"{_PREFIX}/simulateTouch",
            {
                "padCodes": pad_codes,
                "width": width,
                "height": height,
                "pointCount": point_count,
                "positions": positions,
            },
        )

    def simulate_click(self, pad_codes: list[str], **kwargs) -> VmosResponse:
        """Simulate humanized click. POST /vcpcloud/api/padApi/simulateClick"""
        body: dict[str, Any] = {"padCodes": pad_codes, **kwargs}
        return self._http.post(f"{_PREFIX}/simulateClick", body)

    def simulate_swipe(self, pad_codes: list[str], **kwargs) -> VmosResponse:
        """Simulate humanized swipe. POST /vcpcloud/api/padApi/simulateSwipe"""
        body: dict[str, Any] = {"padCodes": pad_codes, **kwargs}
        return self._http.post(f"{_PREFIX}/simulateSwipe", body)

    def simulate_long_press(self, pad_codes: list[str], **kwargs) -> VmosResponse:
        """Simulate humanized long press. POST /vcpcloud/api/padApi/simulateLongPress"""
        body: dict[str, Any] = {"padCodes": pad_codes, **kwargs}
        return self._http.post(f"{_PREFIX}/simulateLongPress", body)

    # ========== Text, SMS, Call Logs ==========

    def input_text(self, pad_codes: list[str], text: str) -> VmosResponse:
        """Cloud phone text input. POST /vcpcloud/api/padApi/inputText"""
        return self._http.post(
            f"{_PREFIX}/inputText", {"padCodes": pad_codes, "text": text}
        )

    def simulate_send_sms(
        self, pad_codes: list[str], sender_number: str, sms_content: str
    ) -> VmosResponse:
        """Simulate send SMS. POST /vcpcloud/api/padApi/simulateSendSms"""
        return self._http.post(
            f"{_PREFIX}/simulateSendSms",
            {
                "padCodes": pad_codes,
                "senderNumber": sender_number,
                "smsContent": sms_content,
            },
        )

    def import_call_logs(
        self, pad_codes: list[str], call_records: list[dict]
    ) -> VmosResponse:
        """Import call logs. POST /vcpcloud/api/padApi/addPhoneRecord"""
        return self._http.post(
            f"{_PREFIX}/addPhoneRecord",
            {"padCodes": pad_codes, "callRecords": call_records},
        )

    # ========== File Upload & Media Injection ==========

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
        """File upload via link. POST /vcpcloud/api/padApi/uploadFileV3"""
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

    def batch_upload_files(self, file_list: list[dict]) -> VmosResponse:
        """Batch upload different files to different instances (max 100 items).
        POST /vcpcloud/api/padApi/batchUploadFile
        """
        return self._http.post(f"{_PREFIX}/batchUploadFile", {"list": file_list})

    def inject_audio(
        self,
        pad_codes: list[str],
        *,
        url: str | None = None,
        file_unique_id: str | None = None,
        enable: bool | None = None,
    ) -> VmosResponse:
        """Inject audio to instance microphone.
        POST /vcpcloud/api/padApi/injectAudioToMic
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if url is not None:
            body["url"] = url
        if file_unique_id is not None:
            body["fileUniqueId"] = file_unique_id
        if enable is not None:
            body["enable"] = enable
        return self._http.post(f"{_PREFIX}/injectAudioToMic", body)

    def unmanned_live(
        self,
        pad_codes: list[str],
        *,
        inject_switch: bool | None = None,
        inject_loop: bool | None = None,
        inject_url: str | None = None,
        inject_urls: list[str] | None = None,
    ) -> VmosResponse:
        """Unmanned live streaming (video injection).
        POST /vcpcloud/api/padApi/unmannedLive
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if inject_switch is not None:
            body["injectSwitch"] = inject_switch
        if inject_loop is not None:
            body["injectLoop"] = inject_loop
        if inject_url is not None:
            body["injectUrl"] = inject_url
        if inject_urls is not None:
            body["injectUrls"] = inject_urls
        return self._http.post(f"{_PREFIX}/unmannedLive", body)

    def inject_picture(
        self,
        pad_codes: list[str],
        *,
        inject_switch: bool | None = None,
        inject_loop: bool | None = None,
        inject_url: str | None = None,
    ) -> VmosResponse:
        """Image injection (Pending Launch).
        POST /vcpcloud/api/padApi/injectPicture
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if inject_switch is not None:
            body["injectSwitch"] = inject_switch
        if inject_loop is not None:
            body["injectLoop"] = inject_loop
        if inject_url is not None:
            body["injectUrl"] = inject_url
        return self._http.post(f"{_PREFIX}/injectPicture", body)

    def upload_user_image(
        self,
        name: str,
        download_url: str,
        *,
        update_log: str | None = None,
        android_version: str | None = None,
        version: str | None = None,
        package_size: int | None = None,
    ) -> VmosResponse:
        """Upload user image. POST /vcpcloud/api/padApi/addUserRom"""
        body: dict[str, Any] = {"name": name, "downloadUrl": download_url}
        if update_log is not None:
            body["updateLog"] = update_log
        if android_version is not None:
            body["androidVersion"] = android_version
        if version is not None:
            body["version"] = version
        if package_size is not None:
            body["packageSize"] = package_size
        return self._http.post(f"{_PREFIX}/addUserRom", body)

    # ========== Timezone, Language, GPS, Contacts ==========

    def update_timezone(
        self, pad_codes: list[str], timezone: str
    ) -> VmosResponse:
        """Modify instance timezone. POST /vcpcloud/api/padApi/updateTimeZone"""
        return self._http.post(
            f"{_PREFIX}/updateTimeZone",
            {"padCodes": pad_codes, "timeZone": timezone},
        )

    def update_language(
        self, pad_codes: list[str], language: str, *, country: str | None = None
    ) -> VmosResponse:
        """Modify instance language. POST /vcpcloud/api/padApi/updateLanguage"""
        body: dict[str, Any] = {"padCodes": pad_codes, "language": language}
        if country is not None:
            body["country"] = country
        return self._http.post(f"{_PREFIX}/updateLanguage", body)

    def set_gps(
        self,
        pad_codes: list[str],
        longitude: float,
        latitude: float,
        *,
        altitude: float | None = None,
        speed: float | None = None,
        bearing: float | None = None,
        horizontal_accuracy_meters: float | None = None,
    ) -> VmosResponse:
        """Set instance GPS coordinates.
        POST /vcpcloud/api/padApi/gpsInjectInfo
        """
        body: dict[str, Any] = {
            "padCodes": pad_codes,
            "longitude": longitude,
            "latitude": latitude,
        }
        if altitude is not None:
            body["altitude"] = altitude
        if speed is not None:
            body["speed"] = speed
        if bearing is not None:
            body["bearing"] = bearing
        if horizontal_accuracy_meters is not None:
            body["horizontalAccuracyMeters"] = horizontal_accuracy_meters
        return self._http.post(f"{_PREFIX}/gpsInjectInfo", body)

    def update_contacts(
        self,
        pad_codes: list[str],
        *,
        file_unique_id: str | None = None,
        operate_type: int | None = None,
        info: list[dict] | None = None,
    ) -> VmosResponse:
        """Update contacts. POST /vcpcloud/api/padApi/updateContacts"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if file_unique_id is not None:
            body["fileUniqueId"] = file_unique_id
        if operate_type is not None:
            body["operateType"] = operate_type
        if info is not None:
            body["info"] = info
        return self._http.post(f"{_PREFIX}/updateContacts", body)

    # ========== Device Management ==========

    def query_countries(self) -> VmosResponse:
        """Query one-key new device supported countries.
        GET /vcpcloud/api/padApi/country
        """
        return self._http.get(f"{_PREFIX}/country")

    def query_webview_versions(self) -> VmosResponse:
        """Query available WebView versions.
        POST /vcpcloud/api/padApi/webview/version/list
        """
        return self._http.post(f"{_PREFIX}/webview/version/list", {})

    def set_keep_alive_app(
        self,
        pad_codes: list[str],
        *,
        apply_all_instances: bool | None = None,
        app_infos: list[dict] | None = None,
    ) -> VmosResponse:
        """Set app keep-alive (Android 13/14/15 only).
        POST /vcpcloud/api/padApi/setKeepAliveApp
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if apply_all_instances is not None:
            body["applyAllInstances"] = apply_all_instances
        if app_infos is not None:
            body["appInfos"] = app_infos
        return self._http.post(f"{_PREFIX}/setKeepAliveApp", body)

    def set_hide_app_list(
        self, pad_codes: list[str], app_infos: list[dict]
    ) -> VmosResponse:
        """Set app hide (Pending Launch).
        POST /vcpcloud/api/padApi/setHideAppList
        """
        return self._http.post(
            f"{_PREFIX}/setHideAppList",
            {"padCodes": pad_codes, "appInfos": app_infos},
        )

    def modify_real_adi_template(
        self,
        pad_codes: list[str],
        *,
        wipe_data: bool | None = None,
        real_phone_template_id: int | None = None,
    ) -> VmosResponse:
        """Modify real device ADI template.
        POST /vcpcloud/api/padApi/replaceRealAdiTemplate
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if wipe_data is not None:
            body["wipeData"] = wipe_data
        if real_phone_template_id is not None:
            body["realPhoneTemplateId"] = real_phone_template_id
        return self._http.post(f"{_PREFIX}/replaceRealAdiTemplate", body)

    def upgrade_image(
        self,
        pad_codes: list[str],
        image_id: str,
        *,
        wipe_data: bool | None = None,
        enable_cpu_core_config: bool | None = None,
    ) -> VmosResponse:
        """Batch instance image upgrade.
        POST /vcpcloud/api/padApi/upgradeImage
        """
        body: dict[str, Any] = {"padCodes": pad_codes, "imageId": image_id}
        if wipe_data is not None:
            body["wipeData"] = wipe_data
        if enable_cpu_core_config is not None:
            body["enableCpuCoreConfig"] = enable_cpu_core_config
        return self._http.post(f"{_PREFIX}/upgradeImage", body)

    def upgrade_real_device_image(
        self,
        pad_codes: list[str],
        *,
        image_id: str | None = None,
        wipe_data: bool | None = None,
        real_phone_template_id: int | None = None,
        upgrade_image_convert_type: int | None = None,
        screen_layout_id: int | None = None,
        certificate: str | None = None,
        device_android_props: dict | None = None,
        enable_cpu_core_config: bool | None = None,
    ) -> VmosResponse:
        """Batch real device image upgrade.
        POST /vcpcloud/api/padApi/virtualRealSwitch
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if image_id is not None:
            body["imageId"] = image_id
        if wipe_data is not None:
            body["wipeData"] = wipe_data
        if real_phone_template_id is not None:
            body["realPhoneTemplateId"] = real_phone_template_id
        if upgrade_image_convert_type is not None:
            body["upgradeImageConvertType"] = upgrade_image_convert_type
        if screen_layout_id is not None:
            body["screenLayoutId"] = screen_layout_id
        if certificate is not None:
            body["certificate"] = certificate
        if device_android_props is not None:
            body["deviceAndroidProps"] = device_android_props
        if enable_cpu_core_config is not None:
            body["enableCpuCoreConfig"] = enable_cpu_core_config
        return self._http.post(f"{_PREFIX}/virtualRealSwitch", body)

    def get_real_device_templates(
        self, *, page: int = 1, rows: int = 20
    ) -> VmosResponse:
        """Paginated get real device templates.
        POST /vcpcloud/api/padApi/templateList
        """
        return self._http.post(
            f"{_PREFIX}/templateList", {"page": page, "rows": rows}
        )

    # ========== ADB ==========

    def enable_adb(
        self, pad_codes: list[str], open_status: bool
    ) -> VmosResponse:
        """Enable/disable ADB. POST /vcpcloud/api/padApi/openOnlineAdb"""
        return self._http.post(
            f"{_PREFIX}/openOnlineAdb",
            {"padCodes": pad_codes, "openStatus": open_status},
        )

    def get_adb_info(
        self,
        pad_code: str,
        *,
        enable: bool | None = None,
        expire_minutes: int | None = None,
    ) -> VmosResponse:
        """Get ADB connection information. POST /vcpcloud/api/padApi/adb"""
        body: dict[str, Any] = {"padCode": pad_code}
        if enable is not None:
            body["enable"] = enable
        if expire_minutes is not None:
            body["expireMinutes"] = expire_minutes
        return self._http.post(f"{_PREFIX}/adb", body)

    def batch_get_adb_info(
        self, pad_codes: list[str], *, enable: bool | None = None
    ) -> VmosResponse:
        """Batch get ADB connection info (Pending Launch).
        POST /vcpcloud/api/padApi/batch/adb
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if enable is not None:
            body["enable"] = enable
        return self._http.post(f"{_PREFIX}/batch/adb", body)

    # ========== Other ==========

    def reset_gaid(
        self,
        pad_codes: list[str],
        *,
        reset_gms_type: int | None = None,
        opr_by: str | None = None,
        task_source: str | None = None,
    ) -> VmosResponse:
        """Reset GAID. POST /vcpcloud/api/padApi/resetGAID"""
        body: dict[str, Any] = {"padCodes": pad_codes}
        if reset_gms_type is not None:
            body["resetGmsType"] = reset_gms_type
        if opr_by is not None:
            body["oprBy"] = opr_by
        if task_source is not None:
            body["taskSource"] = task_source
        return self._http.post(f"{_PREFIX}/resetGAID", body)

    def clear_to_desktop(self, pad_codes: list[str]) -> VmosResponse:
        """Clear processes and return to desktop (Pending Launch).
        POST /vcpcloud/api/padApi/cleanAppHome
        """
        return self._http.post(f"{_PREFIX}/cleanAppHome", {"padCodes": pad_codes})

    def set_bandwidth(
        self,
        pad_codes: list[str],
        *,
        up_bandwidth: int | None = None,
        down_bandwidth: int | None = None,
    ) -> VmosResponse:
        """Set instance bandwidth (Pending Launch).
        POST /vcpcloud/api/padApi/setSpeed
        """
        body: dict[str, Any] = {"padCodes": pad_codes}
        if up_bandwidth is not None:
            body["upBandwidth"] = up_bandwidth
        if down_bandwidth is not None:
            body["downBandwidth"] = down_bandwidth
        return self._http.post(f"{_PREFIX}/setSpeed", body)

    def device_replacement(self, pad_code: str) -> VmosResponse:
        """Device replacement. POST /vcpcloud/api/padApi/replacement"""
        return self._http.post(f"{_PREFIX}/replacement", {"padCode": pad_code})

    def transfer(
        self, pad_codes: list[str], make_over_mobile_phone: str
    ) -> VmosResponse:
        """Transfer cloud phone. POST /vcpcloud/api/padApi/confirmTransfer"""
        return self._http.post(
            f"{_PREFIX}/confirmTransfer",
            {"padCodes": pad_codes, "makeOverMobilePhone": make_over_mobile_phone},
        )

    def hide_accessibility(
        self, pad_codes: list[str], app_infos: list[dict]
    ) -> VmosResponse:
        """Hide accessibility service.
        POST /vcpcloud/api/padApi/setHideAccessibilityAppList
        """
        return self._http.post(
            f"{_PREFIX}/setHideAccessibilityAppList",
            {"padCodes": pad_codes, "appInfos": app_infos},
        )

    def get_script_execution_result(self, task_ids: list[int]) -> VmosResponse:
        """Get instance script execution result (Pending Launch).
        POST /vcpcloud/api/padApi/executeScriptInfo
        """
        return self._http.post(f"{_PREFIX}/executeScriptInfo", {"taskIds": task_ids})

    def get_restart_reset_result(self, task_ids: list[int]) -> VmosResponse:
        """Instance restart/reset execution result (Pending Launch).
        POST /vcpcloud/api/padApi/padExecuteTaskInfo
        """
        return self._http.post(f"{_PREFIX}/padExecuteTaskInfo", {"taskIds": task_ids})

    def toggle_process_hide(
        self, pad_codes: list[str], show: bool, package_name: str
    ) -> VmosResponse:
        """Show or hide app process.
        POST /vcpcloud/api/padApi/toggleProcessHide
        """
        return self._http.post(
            f"{_PREFIX}/toggleProcessHide",
            {"padCodes": pad_codes, "show": show, "packageName": package_name},
        )

    def get_proxy_info(self, pad_codes: list[str]) -> VmosResponse:
        """Query instance proxy information (Pending Launch).
        POST /vcpcloud/open/network/proxy/info
        """
        return self._http.post(
            "/vcpcloud/open/network/proxy/info", {"padCodes": pad_codes}
        )

    # ========== Activation ==========

    def activate_by_code(
        self, active_code_list: list[str], *, country_code: str | None = None
    ) -> VmosResponse:
        """Activate cloud phones with activation codes (async, returns batchId).
        POST /vcpcloud/api/padApi/activateByCode
        """
        body: dict[str, Any] = {"activeCodeList": active_code_list}
        if country_code is not None:
            body["countryCode"] = country_code
        return self._http.post(f"{_PREFIX}/activateByCode", body)

    def query_activation_batch(self, batch_id: str) -> VmosResponse:
        """Query batch activation progress by batchId from activate_by_code.
        POST /vcpcloud/api/padApi/queryActivationBatch
        """
        return self._http.post(
            f"{_PREFIX}/queryActivationBatch", {"batchId": batch_id}
        )

    # ========== Auto-Renewal & Naming & Authorization ==========

    def open_auto_renew(self, pad_code: str) -> VmosResponse:
        """Enable auto-renewal for a single cloud phone.
        POST /vcpcloud/api/padApi/openAutoRenew
        """
        return self._http.post(f"{_PREFIX}/openAutoRenew", {"padCode": pad_code})

    def close_auto_renew(self, pad_code: str) -> VmosResponse:
        """Disable auto-renewal for a single cloud phone.
        POST /vcpcloud/api/padApi/closeAutoRenew
        """
        return self._http.post(f"{_PREFIX}/closeAutoRenew", {"padCode": pad_code})

    def update_pad_name(self, pad_code: str, pad_name: str) -> VmosResponse:
        """Rename a single cloud phone.
        POST /vcpcloud/api/padApi/updatePadName
        """
        return self._http.post(
            f"{_PREFIX}/updatePadName",
            {"padCode": pad_code, "padName": pad_name},
        )

    def authorize_pad(
        self,
        pad_code: str,
        authorized_account: str,
        *,
        minutes: int | None = None,
        equi_authorize: bool | None = None,
        permission: str | None = None,
    ) -> VmosResponse:
        """Temporarily grant a cloud phone to another account.
        minutes is required when equi_authorize is False; permission is a
        comma-separated allowed-operation list (empty means all).
        POST /vcpcloud/api/padApi/authorizePad
        """
        body: dict[str, Any] = {
            "padCode": pad_code,
            "authorizedAccount": authorized_account,
        }
        if minutes is not None:
            body["minutes"] = minutes
        if equi_authorize is not None:
            body["equiAuthorize"] = equi_authorize
        if permission is not None:
            body["permission"] = permission
        return self._http.post(f"{_PREFIX}/authorizePad", body)

    def query_pad_id_change_records(
        self, *, query_date: str | None = None
    ) -> VmosResponse:
        """Query padCode change records (yyyy-MM-dd, Asia/Shanghai);
        omitted query_date returns the last 3 calendar days.
        POST /vcpcloud/api/padApi/queryPadIdChangeRecords
        """
        body: dict[str, Any] = {}
        if query_date is not None:
            body["queryDate"] = query_date
        return self._http.post(f"{_PREFIX}/queryPadIdChangeRecords", body)

    def generate_preview(
        self,
        pad_codes: list[str],
        rotation: int = 0,
        *,
        broadcast: bool | None = None,
    ) -> VmosResponse:
        """Generate preview image for specified instances.
        rotation: 0-default, 1-rotate to portrait.
        POST /vcpcloud/api/padApi/generatePreview
        """
        body: dict[str, Any] = {"padCodes": pad_codes, "rotation": rotation}
        if broadcast is not None:
            body["broadcast"] = broadcast
        return self._http.post(f"{_PREFIX}/generatePreview", body)

    # ========== Cloud-Disk Backups ==========

    def list_pad_backup_ids(self) -> VmosResponse:
        """List all available cloud-disk backup IDs owned by the caller.
        POST /vcpcloud/api/padApi/listPadBackupIds
        """
        return self._http.post(f"{_PREFIX}/listPadBackupIds", {})

    def add_backup(self, pad_codes: list[str]) -> VmosResponse:
        """Batch create cloud-disk backups (async; max 50 pads per call).
        POST /vcpcloud/api/padApi/addBackup
        """
        return self._http.post(
            f"{_PREFIX}/addBackup",
            {"vcPadBackupList": [{"padCode": pc} for pc in pad_codes]},
        )

    def clone_pad_backup(
        self, backup_ids: list[str], pad_codes: list[str]
    ) -> VmosResponse:
        """Batch clone cloud-disk backups onto multiple cloud phones (async).
        POST /vcpcloud/api/padApi/clonePadBackup
        """
        return self._http.post(
            f"{_PREFIX}/clonePadBackup",
            {
                "vcPadBackupList": [{"backupId": b} for b in backup_ids],
                "pads": [{"padCode": pc} for pc in pad_codes],
            },
        )

    def query_backup_batch(self, batch_id: str) -> VmosResponse:
        """Query backup progress by batchId from add_backup.
        POST /vcpcloud/api/padApi/queryBackupBatch
        """
        return self._http.post(
            f"{_PREFIX}/queryBackupBatch", {"batchId": batch_id}
        )
