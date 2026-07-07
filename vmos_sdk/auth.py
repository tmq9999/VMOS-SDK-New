"""VMOS Cloud SDK Authentication.

Supports two signing schemes:
- V2 Simplified Signature (recommended, default)
- V4 HMAC-SHA256 (legacy)

Both schemes share the same AK/SK credentials.
Ref: V2_Simplified_Signature.txt, UserGUIDE.txt
"""

from __future__ import annotations

import binascii
import datetime
import hashlib
import hmac

from vmos_sdk.utils import unix_timestamp


# ============================================================
# V2 Simplified Signature
# ============================================================
# signString = SK + X-Timestamp + path + bodyOrQuery
# X-Sign = lowerHex( SHA-256( signString_UTF8 ) )
#
# Headers: X-Access-Key, X-Timestamp, X-Sign, Content-Type


def v2_sign(secret_key: str, timestamp: str, path: str, body_or_query: str) -> str:
    """Compute V2 Simplified Signature.

    Args:
        secret_key: Secret Access Key (SK) in plain text.
        timestamp: 10-digit unix seconds string.
        path: Full path including servlet prefix, e.g. /vcpcloud/api/padApi/padInfo
        body_or_query: Raw POST body or GET query string. Empty string when no params.

    Returns:
        64-char lowercase hex SHA-256 digest.
    """
    sign_string = secret_key + timestamp + path + body_or_query
    return hashlib.sha256(sign_string.encode("utf-8")).hexdigest()


def v2_headers(
    access_key: str,
    secret_key: str,
    path: str,
    body_or_query: str,
    content_type: str = "application/json",
) -> dict[str, str]:
    """Build complete V2 authentication headers.

    Args:
        access_key: Access Key ID (AK).
        secret_key: Secret Access Key (SK).
        path: API endpoint path.
        body_or_query: Raw body (POST) or query string (GET).
        content_type: Content-Type header value.

    Returns:
        Dict of authentication headers ready to use.
    """
    ts = unix_timestamp()
    sign = v2_sign(secret_key, ts, path, body_or_query)
    headers = {
        "X-Access-Key": access_key,
        "X-Timestamp": ts,
        "X-Sign": sign,
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


# ============================================================
# V4 HMAC-SHA256 Signature (Legacy)
# ============================================================
# Derived signing key:
#   kDate = HMAC-SHA256(SK, shortDate)
#   kService = HMAC-SHA256(kDate, "armcloud-paas")
#   signingKey = HMAC-SHA256(kService, "request")
#
# Canonical string → StringToSign → Signature
# Ref: UserGUIDE.txt Python example

_V4_SERVICE = "armcloud-paas"
_V4_ALGORITHM = "HMAC-SHA256"
_V4_CONTENT_TYPE = "application/json;charset=UTF-8"
_V4_HOST = "api.vmoscloud.com"
_V4_SIGNED_HEADERS = "content-type;host;x-content-sha256;x-date"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hmac_sha256(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def v4_sign(
    secret_key: str,
    body: str,
    host: str = _V4_HOST,
    content_type: str = _V4_CONTENT_TYPE,
) -> tuple[str, str, str]:
    """Compute V4 HMAC-SHA256 signature.

    Args:
        secret_key: Secret Access Key (SK).
        body: JSON body string (spaces removed for hashing).
        host: API host.
        content_type: Content-Type header.

    Returns:
        Tuple of (x_date, authorization_header, signature).
    """
    x_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_date = x_date[:8]

    # Hash body
    x_content_sha256 = _sha256_hex(body.encode("utf-8") if body else b"")

    # Canonical string
    canonical = (
        f"host:{host}\n"
        f"x-date:{x_date}\n"
        f"content-type:{content_type}\n"
        f"signedHeaders:{_V4_SIGNED_HEADERS}\n"
        f"x-content-sha256:{x_content_sha256}"
    )

    # Credential scope
    credential_scope = f"{short_date}/{_V4_SERVICE}/request"

    # String to sign
    string_to_sign = (
        f"{_V4_ALGORITHM}\n"
        f"{x_date}\n"
        f"{credential_scope}\n"
        f"{_sha256_hex(canonical.encode('utf-8'))}"
    )

    # Derived signing key
    k_date = _hmac_sha256(secret_key.encode("utf-8"), short_date)
    k_service = _hmac_sha256(k_date, _V4_SERVICE)
    signing_key = _hmac_sha256(k_service, "request")

    # Final signature
    signature = binascii.hexlify(
        _hmac_sha256(signing_key, string_to_sign)
    ).decode("utf-8")

    # Authorization header
    authorization = (
        f"{_V4_ALGORITHM} Credential={{}}, "
        f"SignedHeaders={_V4_SIGNED_HEADERS}, "
        f"Signature={signature}"
    )

    return x_date, authorization, signature


def v4_headers(
    access_key: str,
    secret_key: str,
    body: str,
    host: str = _V4_HOST,
    content_type: str = _V4_CONTENT_TYPE,
) -> dict[str, str]:
    """Build complete V4 authentication headers.

    Returns:
        Dict of authentication headers ready to use.
    """
    x_date, auth_template, _sig = v4_sign(secret_key, body, host, content_type)
    authorization = auth_template.format(access_key)
    return {
        "content-type": content_type,
        "x-date": x_date,
        "x-host": host,
        "authorization": authorization,
    }
