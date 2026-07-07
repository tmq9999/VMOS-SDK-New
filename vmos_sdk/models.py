"""VMOS Cloud SDK response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VmosResponse:
    """Generic VMOS API response wrapper.

    All API responses follow the format: {code, msg, ts, data, traceId?}
    """

    code: int = 200
    msg: str = "success"
    ts: int = 0
    data: Any = None
    trace_id: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> VmosResponse:
        return cls(
            code=d.get("code", 0),
            msg=d.get("msg", ""),
            ts=d.get("ts", 0),
            data=d.get("data"),
            trace_id=d.get("traceId", ""),
        )

    @property
    def success(self) -> bool:
        return self.code == 200


@dataclass
class TaskResult:
    """Task result from async operations (restart, reset, install, etc.)."""

    task_id: int = 0
    pad_code: str = ""
    vm_status: int = 0
    task_status: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> TaskResult:
        return cls(
            task_id=d.get("taskId", 0),
            pad_code=d.get("padCode", ""),
            vm_status=d.get("vmStatus", 0),
            task_status=d.get("taskStatus", 0),
        )


@dataclass
class PropertyItem:
    """A single property name-value pair."""

    name: str = ""
    value: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> PropertyItem:
        return cls(
            name=d.get("propertiesName", ""),
            value=d.get("propertiesValue", ""),
        )

    def to_dict(self) -> dict:
        return {"propertiesName": self.name, "propertiesValue": self.value}


@dataclass
class InstanceProperties:
    """Instance properties response from padProperties API."""

    pad_code: str = ""
    modem_properties: list[PropertyItem] = field(default_factory=list)
    system_properties: list[PropertyItem] = field(default_factory=list)
    setting_properties: list[PropertyItem] = field(default_factory=list)
    oaid_properties: list[PropertyItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> InstanceProperties:
        return cls(
            pad_code=d.get("padCode", ""),
            modem_properties=[
                PropertyItem.from_dict(p)
                for p in d.get("modemPropertiesList", [])
            ],
            system_properties=[
                PropertyItem.from_dict(p)
                for p in d.get("systemPropertiesList", [])
            ],
            setting_properties=[
                PropertyItem.from_dict(p)
                for p in d.get("settingPropertiesList", [])
            ],
            oaid_properties=[
                PropertyItem.from_dict(p)
                for p in d.get("oaidPropertiesList", [])
            ],
        )


@dataclass
class SmartIpTaskResult:
    """Smart IP task result from getTaskStatus API."""

    pad_code: str = ""
    task_status: str = ""
    task_type: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> SmartIpTaskResult:
        return cls(
            pad_code=d.get("padCode", ""),
            task_status=d.get("taskStatus", ""),
            task_type=d.get("taskType", 0),
        )


@dataclass
class InstalledApp:
    """Installed app info."""

    app_name: str = ""
    package_name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> InstalledApp:
        return cls(
            app_name=d.get("appName", ""),
            package_name=d.get("packageName", ""),
        )


@dataclass
class ProxyCheckResult:
    """Smart IP proxy detection result."""

    proxy_location: str = ""
    public_ip: str = ""
    proxy_working: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> ProxyCheckResult:
        return cls(
            proxy_location=d.get("proxyLocation", ""),
            public_ip=d.get("publicIp", ""),
            proxy_working=d.get("proxyWorking", False),
        )


@dataclass
class PadDetailItem:
    """Cloud phone base info from padDetail API."""

    pad_code: str = ""
    pad_ip: str | None = None
    pad_status: int = 0
    online: int = 0
    compute_occupied: bool = False
    net_storage_res_flag: int = 0
    device_status: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> PadDetailItem:
        return cls(
            pad_code=d.get("padCode", ""),
            pad_ip=d.get("padIp"),
            pad_status=d.get("padStatus", 0),
            online=d.get("online", 0),
            compute_occupied=d.get("computeOccupied", False),
            net_storage_res_flag=d.get("netStorageResFlag", 0),
            device_status=d.get("deviceStatus", 0),
        )


@dataclass
class PaginatedDetail:
    """Paginated result from padDetail API."""

    rows: int = 0
    size: int = 0
    last_id: int | None = None
    has_next: bool = False
    page_data: list[PadDetailItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> PaginatedDetail:
        return cls(
            rows=d.get("rows", 0),
            size=d.get("size", 0),
            last_id=d.get("lastId"),
            has_next=d.get("hasNext", False),
            page_data=[
                PadDetailItem.from_dict(item)
                for item in d.get("pageData", [])
            ],
        )
