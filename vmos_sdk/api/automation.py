"""VMOS Cloud Flow Automation (RPA) API.

Endpoints cho flow script queries, batch task dispatch, và scheduling.
Scripts được tạo bằng VMOS Cloud console flow editor.

Ref: User-provided documentation (Flow Automation section).
"""

from __future__ import annotations

import json
from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi/automation"


def _params_str(params: str | dict) -> str:
    """Dispatch params must be a JSON string; serialize dicts automatically."""
    if isinstance(params, str):
        return params
    return json.dumps(params, ensure_ascii=False, separators=(",", ":"))


class AutomationAPI:
    """Flow Automation (RPA) API — scripts, tasks, và scheduled tasks."""

    def __init__(self, http) -> None:
        self._http = http

    # ========== Flow Scripts ==========

    def list_scripts(
        self,
        *,
        page: int = 1,
        size: int = 20,
        category: str | None = None,
        platform: str | None = None,
    ) -> VmosResponse:
        """Flow script list — paginate flow scripts visible to current user
        (official scripts + private scripts).
        POST /vcpcloud/api/padApi/automation/scripts/list
        """
        body: dict[str, Any] = {"page": page, "size": size}
        if category is not None:
            body["category"] = category
        if platform is not None:
            body["platform"] = platform
        return self._http.post(f"{_PREFIX}/scripts/list", body)

    def get_script(self, script_id: int) -> VmosResponse:
        """Flow script details — fetch a single script by scriptId.
        POST /vcpcloud/api/padApi/automation/scripts/get
        """
        return self._http.post(
            f"{_PREFIX}/scripts/get", {"scriptId": script_id}
        )

    # ========== Flow Tasks ==========

    def batch_dispatch(
        self,
        script_id: int,
        pad_codes: list[str] | None = None,
        *,
        params: str | dict | None = None,
        items: list[dict] | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Batch dispatch flow task — dispatch a flow task to up to 200 instances.
        POST /vcpcloud/api/padApi/automation/tasks/batch-dispatch

        Mode A (shared params): pass pad_codes (+ optional params).
        Mode B (per-device params): pass items=[{"padCode": ..., "params": ...}].
        Exactly one of pad_codes / items must be provided.
        params values are JSON strings; dicts are serialized automatically.
        """
        body: dict[str, Any] = {"scriptId": script_id}
        if pad_codes is not None:
            body["padCodes"] = pad_codes
        if params is not None:
            body["params"] = _params_str(params)
        if items is not None:
            body["items"] = [
                {
                    "padCode": item["padCode"],
                    **(
                        {"params": _params_str(item["params"])}
                        if item.get("params") is not None
                        else {}
                    ),
                }
                for item in items
            ]
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/tasks/batch-dispatch", body)

    def list_tasks(
        self,
        *,
        page: int = 1,
        size: int = 20,
        start_time: str | None = None,
        end_time: str | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Flow task list — paginate current account's flow tasks.
        Supports time-range filtering.
        POST /vcpcloud/api/padApi/automation/tasks/list
        """
        body: dict[str, Any] = {"page": page, "size": size}
        if start_time is not None:
            body["startTime"] = start_time
        if end_time is not None:
            body["endTime"] = end_time
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/tasks/list", body)

    def get_task(self, task_id: int) -> VmosResponse:
        """Flow task details — fetch a single task by taskId.
        POST /vcpcloud/api/padApi/automation/tasks/get
        """
        return self._http.post(
            f"{_PREFIX}/tasks/get", {"taskId": task_id}
        )

    def get_task_logs(self, task_id: int) -> VmosResponse:
        """Flow task logs — step-level execution logs of a task.
        POST /vcpcloud/api/padApi/automation/tasks/logs
        """
        return self._http.post(
            f"{_PREFIX}/tasks/logs", {"taskId": task_id}
        )

    def cancel_task(self, task_id: int) -> VmosResponse:
        """Cancel flow task — cancel a pending or running flow task.
        POST /vcpcloud/api/padApi/automation/tasks/cancel
        """
        return self._http.post(
            f"{_PREFIX}/tasks/cancel", {"taskId": task_id}
        )

    # ========== Scheduled Tasks ==========

    def list_scheduled_tasks(
        self, *, page: int = 1, size: int = 20, **kwargs
    ) -> VmosResponse:
        """Scheduled task list — paginate current user's scheduled tasks.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/list
        """
        body: dict[str, Any] = {"page": page, "size": size}
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/scheduled-tasks/list", body)

    def create_scheduled_task(
        self,
        task_name: str,
        script_id: int,
        pad_codes: list[str],
        *,
        cron_expr: str | None = None,
        one_shot: bool = False,
        params: str | dict | None = None,
        enabled: bool = True,
        **kwargs,
    ) -> VmosResponse:
        """Create scheduled task — can target multiple instances
        (one record per instance); recurring (cronExpr, 6 fields) or one-shot.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/create
        """
        body: dict[str, Any] = {
            "taskName": task_name,
            "scriptId": script_id,
            "padCodes": pad_codes,
            "oneShot": one_shot,
            "enabled": enabled,
        }
        if cron_expr is not None:
            body["cronExpr"] = cron_expr
        if params is not None:
            body["params"] = _params_str(params)
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/scheduled-tasks/create", body)

    def update_scheduled_task(
        self,
        task_id: int,
        task_name: str,
        script_id: int,
        pad_code: str,
        *,
        cron_expr: str | None = None,
        one_shot: bool | None = None,
        params: str | dict | None = None,
        enabled: bool | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Update scheduled task — update a single scheduled task (single device).
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/update
        """
        body: dict[str, Any] = {
            "taskId": task_id,
            "taskName": task_name,
            "scriptId": script_id,
            "padCode": pad_code,
        }
        if cron_expr is not None:
            body["cronExpr"] = cron_expr
        if one_shot is not None:
            body["oneShot"] = one_shot
        if params is not None:
            body["params"] = _params_str(params)
        if enabled is not None:
            body["enabled"] = enabled
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/scheduled-tasks/update", body)

    def toggle_scheduled_task(
        self, task_id: int, enabled: bool
    ) -> VmosResponse:
        """Toggle scheduled task — enable / disable a scheduled task.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/toggle
        """
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/toggle",
            {"taskId": task_id, "enabled": enabled},
        )

    def delete_scheduled_task(self, task_id: int) -> VmosResponse:
        """Delete scheduled task.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/delete
        """
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/delete", {"taskId": task_id}
        )
