"""VMOS Cloud Flow Automation (RPA) API.

Endpoints cho flow script queries, batch task dispatch, và scheduling.
Scripts được tạo bằng VMOS Cloud console flow editor.

Ref: User-provided documentation (Flow Automation section).
"""

from __future__ import annotations

from typing import Any

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi/automation"


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

    def get_script(self, script_id: str) -> VmosResponse:
        """Flow script details — fetch a single script by scriptId.
        POST /vcpcloud/api/padApi/automation/scripts/get
        """
        return self._http.post(
            f"{_PREFIX}/scripts/get", {"scriptId": script_id}
        )

    # ========== Flow Tasks ==========

    def batch_dispatch(
        self,
        script_id: str,
        pad_codes: list[str],
        *,
        params: dict | None = None,
        per_device_params: list[dict] | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Batch dispatch flow task — dispatch a flow task to up to 200 instances.
        Supports shared params or per-device params.
        POST /vcpcloud/api/padApi/automation/tasks/batch-dispatch
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "padCodes": pad_codes,
        }
        if params is not None:
            body["params"] = params
        if per_device_params is not None:
            body["perDeviceParams"] = per_device_params
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

    def get_task(self, task_id: str) -> VmosResponse:
        """Flow task details — fetch a single task by taskId.
        POST /vcpcloud/api/padApi/automation/tasks/get
        """
        return self._http.post(
            f"{_PREFIX}/tasks/get", {"taskId": task_id}
        )

    def get_task_logs(self, task_id: str) -> VmosResponse:
        """Flow task logs — step-level execution logs of a task.
        POST /vcpcloud/api/padApi/automation/tasks/logs
        """
        return self._http.post(
            f"{_PREFIX}/tasks/logs", {"taskId": task_id}
        )

    def cancel_task(self, task_id: str) -> VmosResponse:
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
        script_id: str,
        pad_codes: list[str],
        *,
        task_name: str | None = None,
        cron: str | None = None,
        params: dict | None = None,
        **kwargs,
    ) -> VmosResponse:
        """Create scheduled task — can target multiple instances
        (one record per instance); recurring or one-shot.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/create
        """
        body: dict[str, Any] = {
            "scriptId": script_id,
            "padCodes": pad_codes,
        }
        if task_name is not None:
            body["taskName"] = task_name
        if cron is not None:
            body["cron"] = cron
        if params is not None:
            body["params"] = params
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/scheduled-tasks/create", body)

    def update_scheduled_task(
        self, task_id: str, **kwargs
    ) -> VmosResponse:
        """Update scheduled task — update a single scheduled task (single device).
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/update
        """
        body: dict[str, Any] = {"taskId": task_id}
        body.update(kwargs)
        return self._http.post(f"{_PREFIX}/scheduled-tasks/update", body)

    def toggle_scheduled_task(
        self, task_id: str, enabled: bool
    ) -> VmosResponse:
        """Toggle scheduled task — enable / disable a scheduled task.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/toggle
        """
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/toggle",
            {"taskId": task_id, "enabled": enabled},
        )

    def delete_scheduled_task(self, task_id: str) -> VmosResponse:
        """Delete scheduled task.
        POST /vcpcloud/api/padApi/automation/scheduled-tasks/delete
        """
        return self._http.post(
            f"{_PREFIX}/scheduled-tasks/delete", {"taskId": task_id}
        )
