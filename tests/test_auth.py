"""Tests for VMOS Cloud SDK Authentication.

Verifies V2 Simplified Signature implementation against the official
signing example from V2_Simplified_Signature.txt.
"""

import hashlib
from vmos_sdk.auth import v2_sign, v2_headers


class TestV2Signing:
    """Test V2 Simplified Signature."""

    def test_sign_matches_docs_example(self):
        """Verify against the example from V2_Simplified_Signature.txt:

        SK   = 9cucpjoyn4xxmkhj3q9el3ce
        ts   = 1747555200
        path = /vcpcloud/api/padApi/padInfo
        body = {"padCode":"AC32010601132"}

        signString = SK + ts + path + body
        """
        sk = "9cucpjoyn4xxmkhj3q9el3ce"
        ts = "1747555200"
        path = "/vcpcloud/api/padApi/padInfo"
        body = '{"padCode":"AC32010601132"}'

        # Manually compute expected result
        sign_string = sk + ts + path + body
        expected = hashlib.sha256(sign_string.encode("utf-8")).hexdigest()

        result = v2_sign(sk, ts, path, body)

        assert result == expected
        assert len(result) == 64  # 64-char hex
        assert result == result.lower()  # lowercase

    def test_sign_empty_body(self):
        """Empty body when GET request has no params."""
        sk = "test_secret_key"
        ts = "1747555200"
        path = "/vcpcloud/api/padApi/country"
        body = ""

        result = v2_sign(sk, ts, path, body)

        expected = hashlib.sha256(
            (sk + ts + path).encode("utf-8")
        ).hexdigest()
        assert result == expected

    def test_sign_get_with_query(self):
        """GET request with query string as bodyOrQuery."""
        sk = "test_secret_key"
        ts = "1747555200"
        path = "/vcpcloud/api/padApi/getOrderEquipmentList"
        query = "startDate=2026-05-01&endDate=2026-05-31"

        result = v2_sign(sk, ts, path, query)

        expected = hashlib.sha256(
            (sk + ts + path + query).encode("utf-8")
        ).hexdigest()
        assert result == expected

    def test_headers_contain_required_fields(self):
        """V2 headers must contain X-Access-Key, X-Timestamp, X-Sign."""
        headers = v2_headers(
            access_key="ak_test",
            secret_key="sk_test",
            path="/vcpcloud/api/padApi/padInfo",
            body_or_query='{"padCode":"AC32010601132"}',
        )

        assert "X-Access-Key" in headers
        assert "X-Timestamp" in headers
        assert "X-Sign" in headers
        assert "Content-Type" in headers
        assert headers["X-Access-Key"] == "ak_test"
        assert headers["Content-Type"] == "application/json"
        assert len(headers["X-Timestamp"]) == 10
        assert len(headers["X-Sign"]) == 64

    def test_headers_get_no_content_type(self):
        """GET requests should NOT have Content-Type."""
        headers = v2_headers(
            access_key="ak_test",
            secret_key="sk_test",
            path="/vcpcloud/api/padApi/country",
            body_or_query="",
            content_type="",
        )

        assert "Content-Type" not in headers

    def test_sign_file_upload_empty_body(self):
        """File upload endpoints use empty string for bodyOrQuery (per V2 FAQ Q4)."""
        sk = "test_secret_key"
        ts = "1747555200"
        path = "/vcpcloud/api/padApi/uploadFile"
        body = ""  # File body is NOT signed

        result = v2_sign(sk, ts, path, body)

        expected = hashlib.sha256(
            (sk + ts + path).encode("utf-8")
        ).hexdigest()
        assert result == expected

    def test_sign_with_real_credentials(self):
        """Test with the actual AK/SK from Auth_Key.txt."""
        ak = "R3ZAcmkLn0zu2RWyJCQYn5RHHW9j03G4"
        sk = "vYeoL2mCuwLJIQoLXkXAUREO"

        headers = v2_headers(
            access_key=ak,
            secret_key=sk,
            path="/vcpcloud/api/padApi/padInfo",
            body_or_query='{"padCode":"test"}',
        )

        assert headers["X-Access-Key"] == ak
        assert len(headers["X-Sign"]) == 64
