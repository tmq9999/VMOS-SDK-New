"""VMOS Cloud Callback Event Models.

Callback JSON formats từ CallbackTaskBusinessTypCodes.txt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CallbackEvent:
    """Base callback event from VMOS webhook."""

    task_business_type: int = 0
    pad_code: str = ""
    task_id: int | None = None
    task_status: int = 0
    task_result: str = ""
    task_content: Any = None
    end_time: int | None = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> CallbackEvent:
        return cls(
            task_business_type=d.get("taskBusinessType", 0),
            pad_code=d.get("padCode", ""),
            task_id=d.get("taskId"),
            task_status=d.get("taskStatus", 0),
            task_result=d.get("taskResult", ""),
            task_content=d.get("taskContent"),
            end_time=d.get("endTime"),
            raw=d,
        )


@dataclass
class InstanceStatusEvent(CallbackEvent):
    """Instance status callback (type 999)."""

    pad_status: int = 0
    pad_connect_status: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> InstanceStatusEvent:
        base = CallbackEvent.from_dict(d)
        return cls(
            **{k: v for k, v in base.__dict__.items()},
            pad_status=d.get("padStatus", 0),
            pad_connect_status=d.get("padConnectStatus", 0),
        )


@dataclass
class AdbResultEvent(CallbackEvent):
    """ADB command result callback (type 1002)."""

    cmd: str = ""
    cmd_result: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> AdbResultEvent:
        base = CallbackEvent.from_dict(d)
        return cls(
            **{k: v for k, v in base.__dict__.items()},
            cmd=d.get("cmd", ""),
            cmd_result=d.get("cmdResult", ""),
        )


@dataclass
class AppEvent(CallbackEvent):
    """App start/stop/install/uninstall callback (types 1003-1007)."""

    package_name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> AppEvent:
        base = CallbackEvent.from_dict(d)
        return cls(
            **{k: v for k, v in base.__dict__.items()},
            package_name=d.get("packageName", ""),
        )


@dataclass
class FileUploadEvent(CallbackEvent):
    """File upload callback (type 1009)."""

    file_id: str = ""
    result: bool = False
    error_code: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> FileUploadEvent:
        base = CallbackEvent.from_dict(d)
        return cls(
            **{k: v for k, v in base.__dict__.items()},
            file_id=d.get("fileId", ""),
            result=d.get("result", False),
            error_code=d.get("errorCode"),
        )


@dataclass
class ImageUploadEvent(CallbackEvent):
    """Image upload callback (type 4001)."""

    image_id: str = ""
    fail_msg: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> ImageUploadEvent:
        base = CallbackEvent.from_dict(d)
        return cls(
            **{k: v for k, v in base.__dict__.items()},
            image_id=d.get("imageId", ""),
            fail_msg=d.get("failMsg", ""),
        )
