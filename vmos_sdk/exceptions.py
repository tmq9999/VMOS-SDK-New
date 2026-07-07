"""VMOS Cloud SDK Exceptions."""

from __future__ import annotations


class VmosError(Exception):
    """Base exception for all VMOS SDK errors."""

    def __init__(self, code: int = 0, message: str = "", ts: int = 0) -> None:
        self.code = code
        self.message = message
        self.ts = ts
        super().__init__(f"[{code}] {message}")


class VmosAuthError(VmosError):
    """Authentication / signature errors.

    Error codes: 2019, 2031, 2032, 2033, 100003, 100004, 100005
    """


class VmosInstanceError(VmosError):
    """Instance-related errors.

    Error codes: 110028, 110013, 110031, 120005
    """


class VmosRateLimitError(VmosError):
    """Rate limiting / too frequent requests.

    Error codes: 110014, 100011
    """


class VmosRequestError(VmosError):
    """Invalid request parameters.

    Error codes: 100000, 110065, 1104, 100013
    """


class VmosNetworkError(VmosError):
    """Network connectivity errors (timeout, connection refused, etc.)."""


# Error code → exception class mapping
ERROR_CODE_MAP: dict[int, type[VmosError]] = {
    # Auth errors
    2019: VmosAuthError,
    2031: VmosAuthError,
    2032: VmosAuthError,
    2033: VmosAuthError,
    100003: VmosAuthError,
    100004: VmosAuthError,
    100005: VmosAuthError,
    100006: VmosAuthError,
    100007: VmosAuthError,
    100008: VmosAuthError,
    # Instance errors
    110028: VmosInstanceError,
    110013: VmosInstanceError,
    110031: VmosInstanceError,
    120005: VmosInstanceError,
    2020: VmosInstanceError,
    # Rate limit errors
    110014: VmosRateLimitError,
    100011: VmosRateLimitError,
    # Request errors
    100000: VmosRequestError,
    110065: VmosRequestError,
    1104: VmosRequestError,
    100013: VmosRequestError,
    100012: VmosRequestError,
}


def raise_for_error_code(code: int, message: str, ts: int = 0) -> None:
    """Raise the appropriate exception for a VMOS error code."""
    if code == 200:
        return
    exc_class = ERROR_CODE_MAP.get(code, VmosError)
    raise exc_class(code=code, message=message, ts=ts)
