"""VMOS Cloud Task Management API.

Endpoints cho query task results (async operations).
Ref: vmoscloud-api.txt Section 4.
"""

from __future__ import annotations

from vmos_sdk.models import VmosResponse

_PREFIX = "/vcpcloud/api/padApi"


class TaskAPI:
    """Task Management API."""

    def __init__(self, http) -> None:
        self._http = http

    def get_task_detail(
        self, task_ids: list[int] | None = None, *, task_id: int | None = None
    ) -> VmosResponse:
        """Instance operation task details.
        POST /vcpcloud/api/padApi/padTaskDetail

        Can query by task_ids list or single task_id.
        """
        body = {}
        if task_ids is not None:
            body["taskIds"] = task_ids
        if task_id is not None:
            body["taskId"] = task_id
        return self._http.post(f"{_PREFIX}/padTaskDetail", body)

    def get_file_task_detail(
        self, task_ids: list[int] | None = None, *, task_id: int | None = None
    ) -> VmosResponse:
        """File task details.
        POST /vcpcloud/api/padApi/fileTaskDetail
        """
        body = {}
        if task_ids is not None:
            body["taskIds"] = task_ids
        if task_id is not None:
            body["taskId"] = task_id
        return self._http.post(f"{_PREFIX}/fileTaskDetail", body)
