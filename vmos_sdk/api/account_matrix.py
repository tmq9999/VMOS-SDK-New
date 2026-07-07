"""VMOS Cloud Account Matrix API.

Account-centric operational endpoints: account queries, lifecycle management
(create / bind / unbind / delete / group), và batch-triggering templates on accounts.

Target instance is derived from each account's currently bound instance.
Credentials are write-only: written on create (AES-GCM encrypted at rest) and
injected per account at execution via fromCredential. Plaintext is never readable
via OpenAPI (credential read is console-only).

Ref: User-provided documentation (Account Matrix section).
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi/automation/accounts"


class AccountMatrixAPI:
    """Account Matrix API — account CRUD, binding, batch operations."""

    def __init__(self, http) -> None:
        self._http = http

    # ========== Account Queries ==========

    def list_accounts(
        self,
        *,
        page: int = 1,
        size: int = 20,
        platform: str | None = None,
        group_id: str | None = None,
        status: int | None = None,
        keyword: str | None = None,
        bind_status: int | None = None,
        sort_field: str | None = None,
        sort_order: str | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Account list — paginate accounts with filtering & sorting.
        Supports platform / group / status / keyword / bind-status filtering.
        POST /vcpcloud/api/padApi/automation/accounts/list
        """
        body: dict[str, Any] = {"page": page, "size": size}
        if platform is not None:
            body["platform"] = platform
        if group_id is not None:
            body["groupId"] = group_id
        if status is not None:
            body["status"] = status
        if keyword is not None:
            body["keyword"] = keyword
        if bind_status is not None:
            body["bindStatus"] = bind_status
        if sort_field is not None:
            body["sortField"] = sort_field
        if sort_order is not None:
            body["sortOrder"] = sort_order
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/list", body)

    def get_account(self, account_id: str) -> VmosResponse:
        """Account details — fetch a single account by accountId.
        POST /vcpcloud/api/padApi/automation/accounts/get
        """
        return self._http.post(
            f"{_PREFIX}/get", {"accountId": account_id}
        )

    def get_snapshots(self, account_id: str) -> VmosResponse:
        """Account data snapshots — historical snapshots by accountId
        (followers / following / works / likes time series).
        POST /vcpcloud/api/padApi/automation/accounts/snapshots
        """
        return self._http.post(
            f"{_PREFIX}/snapshots", {"accountId": account_id}
        )

    def get_works(
        self,
        account_id: str,
        *,
        page: int = 1,
        size: int = 20,
        **kwargs,
    ) -> VmosResponse:
        """Account works list — paginate the account's collected works (deduplicated).
        POST /vcpcloud/api/padApi/automation/accounts/works
        """
        body: dict[str, Any] = {
            "accountId": account_id,
            "page": page,
            "size": size,
        }
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/works", body)

    def get_work_snapshots(
        self, account_id: str, work_id: str
    ) -> VmosResponse:
        """Account work data snapshots — single work's metric time series.
        POST /vcpcloud/api/padApi/automation/accounts/work-snapshots
        """
        return self._http.post(
            f"{_PREFIX}/work-snapshots",
            {"accountId": account_id, "workId": work_id},
        )

    # ========== Groups ==========

    def list_groups(self) -> VmosResponse:
        """Account group list — list the current user's account groups.
        POST /vcpcloud/api/padApi/automation/accounts/groups/list
        """
        return self._http.post(f"{_PREFIX}/groups/list", {})

    # ========== Batch Operations ==========

    def batch_trigger(
        self,
        script_id: str,
        account_ids: list[str],
        *,
        params: dict | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Batch trigger account operation — dispatch a template to run
        immediately on multiple accounts. Target instances derived from
        bound instances, credentials injected server-side.
        POST /vcpcloud/api/padApi/automation/accounts/operations/batch
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "accountIds": account_ids,
        }
        if params is not None:
            body["params"] = params
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/operations/batch", body)

    def batch_scheduled_tasks(
        self,
        script_id: str,
        account_ids: list[str],
        *,
        cron: str | None = None,
        task_name: str | None = None,
        params: dict | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Account batch scheduled tasks — batch-create scheduled tasks
        for multiple accounts (one record each). Credentials injected
        per account at fire time.
        POST /vcpcloud/api/padApi/automation/accounts/scheduled-tasks/batch
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "accountIds": account_ids,
        }
        if cron is not None:
            body["cron"] = cron
        if task_name is not None:
            body["taskName"] = task_name
        if params is not None:
            body["params"] = params
        body.update(kwargs)
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/batch", body
        )

    # ========== Account Lifecycle ==========

    def create_account(
        self,
        handle: str,
        platform: str,
        *,
        credentials: dict | None = None,
        group_id: str | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Create account — with credentials (AES-GCM encrypted at rest).
        Handle is unique per platform.
        POST /vcpcloud/api/padApi/automation/accounts/create
        """
        body: dict[str, Any] = {
            "handle": handle,
            "platform": platform,
        }
        if credentials is not None:
            body["credentials"] = credentials
        if group_id is not None:
            body["groupId"] = group_id
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/create", body)

    def bind_instance(
        self, account_id: str, pad_code: str
    ) -> VmosResponse:
        """Bind instance — bind an account to an instance (padCode).
        One active account per instance+platform, force to rebind.
        POST /vcpcloud/api/padApi/automation/accounts/bind
        """
        return self._http.post(
            f"{_PREFIX}/bind",
            {"accountId": account_id, "padCode": pad_code},
        )

    def unbind_instance(self, account_id: str) -> VmosResponse:
        """Unbind instance — unbind the account from its instance.
        POST /vcpcloud/api/padApi/automation/accounts/unbind
        """
        return self._http.post(
            f"{_PREFIX}/unbind", {"accountId": account_id}
        )

    def delete_account(self, account_id: str) -> VmosResponse:
        """Delete account — soft-delete (credentials cleared, recoverable by admin).
        POST /vcpcloud/api/padApi/automation/accounts/delete
        """
        return self._http.post(
            f"{_PREFIX}/delete", {"accountId": account_id}
        )

    def move_group(
        self, account_id: str, group_id: str | None = None
    ) -> VmosResponse:
        """Move account group — pass None for groupId to ungroup.
        POST /vcpcloud/api/padApi/automation/accounts/group
        """
        return self._http.post(
            f"{_PREFIX}/group",
            {"accountId": account_id, "groupId": group_id},
        )
