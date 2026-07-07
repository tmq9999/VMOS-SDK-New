"""VMOS Cloud SDK Constants.

Enums và constants được lấy trực tiếp từ tài liệu VMOS Cloud API.
"""

from __future__ import annotations

from enum import IntEnum, Enum


# === Instance Status (từ padDetail response, field: padStatus) ===
class PadStatus(IntEnum):
    """Instance running status (padStatus field from padDetail API)."""
    RUNNING = 10
    RESTARTING = 11
    RESETTING = 12
    UPGRADING = 13
    ABNORMAL = 14
    NOT_READY = 15
    BACKING_UP = 16
    RESTORING = 17
    SHUTDOWN = 18
    SHUTTING_DOWN = 19
    BOOTING = 20
    SHUTDOWN_FAILED = 21
    BOOT_FAILED = 22
    DELETING = 23
    DELETE_FAILED = 24
    DELETED = 25
    CLONING = 26


# === Cloud Phone Status (từ userPadList response, field: cvmStatus) ===
class CvmStatus(IntEnum):
    """Cloud phone status (cvmStatus field from userPadList API)."""
    LOADING = 99
    NORMAL = 100
    SCREENSHOT = 101
    REBOOTING = 102
    RESETTING = 103
    REBOOT_FAILED = 104
    RESET_FAILED = 105
    MAINTENANCE = 106
    UPGRADING_IMAGE = 107
    MIGRATING = 108
    MIGRATION_FAILED = 109
    DEVICE_CONFIG = 111
    ANTI_FRAUD_LOCKDOWN = 112
    CONFIG_CHANGE = 113
    OVER_SELLING = 114
    CHANGING_ZONE = 115
    CLEANING_MEMORY = 116
    INITIALIZING = 119
    ONE_KEY_NEW_DEVICE_INIT = 120
    TASK_IN_PROGRESS = 121
    BACKING_UP = 201
    RESTORING = 202


# === Task Status (từ callback và padTaskDetail) ===
class TaskStatus(IntEnum):
    """Task execution status."""
    TOTAL_FAILURE = -1
    PARTIAL_FAILURE = -2
    CANCELLED = -3
    TIMEOUT = -4
    PENDING = 1
    EXECUTING = 2
    COMPLETED = 3


# === Callback Task Business Type Codes ===
class CallbackType(IntEnum):
    """Callback task business type codes (từ CallbackTaskBusinessTypCodes.txt)."""
    INSTANCE_STATUS = 999
    RESTART = 1000
    RESET = 1001
    ADB_CMD = 1002
    APP_INSTALL = 1003
    APP_UNINSTALL = 1004
    APP_STOP = 1005
    APP_RESTART = 1006
    APP_START = 1007
    FILE_UPLOAD = 1009
    IMAGE_UPGRADE = 1012
    ONE_KEY_NEW_DEVICE = 1124
    USER_IMAGE_UPLOAD = 4001


# === Online Status ===
class OnlineStatus(IntEnum):
    """Instance online status."""
    OFFLINE = 0
    ONLINE = 1


# === Proxy Type ===
class ProxyType(str, Enum):
    """Proxy protocol type."""
    SOCKS5 = "socks5"
    HTTP = "http"
    HTTPS = "https"


# === Proxy Mode ===
class ProxyMode(str, Enum):
    """Proxy mode."""
    VPN = "vpn"
    PROXY = "proxy"


# === Smart IP Task Type ===
class SmartIpTaskType(IntEnum):
    """Smart IP task types."""
    SET_SMART_IP = 10010
    CANCEL_SMART_IP = 10011


# === SIM Card State (từ Instance_Property_List.txt) ===
class SimState(IntEnum):
    """SIM card state."""
    ABSENT = 0
    NO_SIM = 1
    NETWORK_LOCKED = 2
    PIN_LOCKED = 3
    PUK_LOCKED = 4
    READY = 5


# === Network Type (từ Instance_Property_List.txt) ===
class NetworkType(IntEnum):
    """Data/Voice network type."""
    CDMA = 4
    LTE = 13
    GSM = 16
    NR = 20  # 5G
