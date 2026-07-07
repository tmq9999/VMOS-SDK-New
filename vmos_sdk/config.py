"""VMOS Cloud SDK Configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """SDK configuration.

    Attributes:
        access_key: VMOS Cloud Access Key ID (AK).
        secret_key: VMOS Cloud Secret Access Key (SK).
        base_url: API base URL.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on failure.
        signing_version: Signing scheme to use ("v2" or "v4").
    """

    access_key: str = ""
    secret_key: str = ""
    base_url: str = "https://api.vmoscloud.com"
    timeout: int = 30
    max_retries: int = 3
    signing_version: str = "v2"
    user_agent: str = field(default="VMOS-Python-SDK/1.0.0")

    def __post_init__(self) -> None:
        if not self.access_key:
            self.access_key = os.environ.get("VMOS_ACCESS_KEY", "")
        if not self.secret_key:
            self.secret_key = os.environ.get("VMOS_SECRET_KEY", "")

    def validate(self) -> None:
        """Validate required configuration."""
        if not self.access_key:
            raise ValueError(
                "access_key is required. Set VMOS_ACCESS_KEY env var or pass directly."
            )
        if not self.secret_key:
            raise ValueError(
                "secret_key is required. Set VMOS_SECRET_KEY env var or pass directly."
            )
        if self.signing_version not in ("v2", "v4"):
            raise ValueError("signing_version must be 'v2' or 'v4'")
