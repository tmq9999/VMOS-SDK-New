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
        group_id: int | None = None,
        status: str | None = None,
        keyword: str | None = None,
        device_bound: bool | None = None,
        sort_by: str | None = None,
        sort_dir: str | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Account list — paginate accounts with filtering & sorting.
        status: inactive / active / login_failed; sort_dir: asc / desc.
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
        if device_bound is not None:
            body["deviceBound"] = device_bound
        if sort_by is not None:
            body["sortBy"] = sort_by
        if sort_dir is not None:
            body["sortDir"] = sort_dir
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/list", body)

    def get_account(self, account_id: int) -> VmosResponse:
        """Account details — fetch a single account by accountId.
        POST /vcpcloud/api/padApi/automation/accounts/get
        """
        return self._http.post(
            f"{_PREFIX}/get", {"accountId": account_id}
        )

    def get_snapshots(self, account_id: int) -> VmosResponse:
        """Account data snapshots — historical snapshots by accountId
        (followers / following / works / likes time series).
        POST /vcpcloud/api/padApi/automation/accounts/snapshots
        """
        return self._http.post(
            f"{_PREFIX}/snapshots", {"accountId": account_id}
        )

    def get_works(
        self,
        account_id: int,
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
        self, account_id: int, work_id: int
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
        script_id: int,
        account_ids: list[int],
        *,
        task_name: str | None = None,
        shared_options: list[dict] | None = None,
        per_account_options: dict[str, list[dict]] | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Batch trigger account operation — dispatch a template to run
        immediately on multiple accounts. Target instances derived from
        bound instances, credentials injected server-side.
        Option item: {"key": ..., "value": ...} or
        {"key": ..., "fromCredential": "username|password|twofa_secret|email|email_password"}.
        POST /vcpcloud/api/padApi/automation/accounts/operations/batch
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "accountIds": account_ids,
        }
        if task_name is not None:
            body["taskName"] = task_name
        if shared_options is not None:
            body["sharedOptions"] = shared_options
        if per_account_options is not None:
            body["perAccountOptions"] = per_account_options
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/operations/batch", body)

    def batch_scheduled_tasks(
        self,
        script_id: int,
        account_ids: list[int],
        cron_expr: str,
        *,
        one_shot: bool = False,
        enabled: bool = True,
        task_name: str | None = None,
        shared_options: list[dict] | None = None,
        per_account_options: dict[str, list[dict]] | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Account batch scheduled tasks — batch-create scheduled tasks
        for multiple accounts (one record each), fired on a Cron schedule
        (6 fields, includes seconds). Credentials injected per account at
        fire time.
        POST /vcpcloud/api/padApi/automation/accounts/scheduled-tasks/batch
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "accountIds": account_ids,
            "cronExpr": cron_expr,
            "oneShot": one_shot,
            "enabled": enabled,
        }
        if task_name is not None:
            body["taskName"] = task_name
        if shared_options is not None:
            body["sharedOptions"] = shared_options
        if per_account_options is not None:
            body["perAccountOptions"] = per_account_options
        body.update(kwargs)
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/batch", body
        )

    # ========== Account Lifecycle ==========

    def create_account(
        self,
        platform: str,
        username: str,
        password: str,
        *,
        handle: str | None = None,
        twofa_secret: str | None = None,
        email: str | None = None,
        email_password: str | None = None,
        group_id: int | None = None,
        country: str | None = None,
        note: str | None = None,
        tags: str | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Create account — credentials are AES-GCM encrypted at rest.
        Handle is unique per platform (may be empty).
        POST /vcpcloud/api/padApi/automation/accounts/create
        """
        body: dict[str, Any] = {
            "platform": platform,
            "username": username,
            "password": password,
        }
        if handle is not None:
            body["handle"] = handle
        if twofa_secret is not None:
            body["twofaSecret"] = twofa_secret
        if email is not None:
            body["email"] = email
        if email_password is not None:
            body["emailPassword"] = email_password
        if group_id is not None:
            body["groupId"] = group_id
        if country is not None:
            body["country"] = country
        if note is not None:
            body["note"] = note
        if tags is not None:
            body["tags"] = tags
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/create", body)

    def bind_instance(
        self, account_id: int, pad_code: str, *, force: bool = False
    ) -> VmosResponse:
        """Bind instance — bind an account to an instance (padCode).
        One active account per instance+platform; force=True rebinds on
        conflict (409 otherwise).
        POST /vcpcloud/api/padApi/automation/accounts/bind
        """
        return self._http.post(
            f"{_PREFIX}/bind",
            {"accountId": account_id, "padCode": pad_code, "force": force},
        )

    def unbind_instance(self, account_id: int) -> VmosResponse:
        """Unbind instance — unbind the account from its instance.
        POST /vcpcloud/api/padApi/automation/accounts/unbind
        """
        return self._http.post(
            f"{_PREFIX}/unbind", {"accountId": account_id}
        )

    def delete_account(self, account_id: int) -> VmosResponse:
        """Delete account — soft-delete (credentials cleared, recoverable by admin).
        POST /vcpcloud/api/padApi/automation/accounts/delete
        """
        return self._http.post(
            f"{_PREFIX}/delete", {"accountId": account_id}
        )

    def move_group(
        self, account_id: int, group_id: int | None = None
    ) -> VmosResponse:
        """Move account group — pass None for groupId to ungroup.
        POST /vcpcloud/api/padApi/automation/accounts/group
        """
        return self._http.post(
            f"{_PREFIX}/group",
            {"accountId": account_id, "groupId": group_id},
        )
