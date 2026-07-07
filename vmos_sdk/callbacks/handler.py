"""VMOS Cloud Callback/Webhook Handler.

Xử lý callback events từ VMOS Cloud. Hỗ trợ Flask integration.

Callback types từ CallbackTaskBusinessTypCodes.txt:
- 999:  Instance status
- 1000: Restart completed
- 1001: Reset completed
- 1002: ADB command result
- 1003: App installed
- 1004: App uninstalled
- 1005: App stopped
- 1006: App restarted
- 1007: App started
- 1009: File uploaded
- 1012: Image upgraded
- 1124: One-key new device done
- 4001: User image uploaded
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any, Callable

from vmos_sdk.callbacks.models import (
    AdbResultEvent,
    AppEvent,
    CallbackEvent,
    FileUploadEvent,
    ImageUploadEvent,
    InstanceStatusEvent,
)
from vmos_sdk.constants import CallbackType

logger = logging.getLogger("vmos_sdk.callbacks")

# Type → event model mapping
_EVENT_MAP: dict[int, type[CallbackEvent]] = {
    CallbackType.INSTANCE_STATUS: InstanceStatusEvent,
    CallbackType.ADB_CMD: AdbResultEvent,
    CallbackType.APP_INSTALL: AppEvent,
    CallbackType.APP_UNINSTALL: AppEvent,
    CallbackType.APP_STOP: AppEvent,
    CallbackType.APP_RESTART: AppEvent,
    CallbackType.APP_START: AppEvent,
    CallbackType.FILE_UPLOAD: FileUploadEvent,
    CallbackType.USER_IMAGE_UPLOAD: ImageUploadEvent,
}


class CallbackHandler:
    """Webhook callback handler for VMOS Cloud events.

    Usage:
        handler = CallbackHandler()

        @handler.on(CallbackType.ADB_CMD)
        def handle_adb(event: AdbResultEvent):
            print(f"ADB result: {event.cmd_result}")

        @handler.on_adb_result
        def handle_adb2(event):
            print(f"ADB result: {event.cmd_result}")

        # Flask integration
        app.route("/webhook", methods=["POST"])(handler.flask_view)
    """

    def __init__(self) -> None:
        self._handlers: dict[int, list[Callable]] = defaultdict(list)
        self._catch_all: list[Callable] = []

    def on(self, event_type: int) -> Callable:
        """Register a handler for a specific callback type."""
        def decorator(func: Callable) -> Callable:
            self._handlers[event_type].append(func)
            return func
        return decorator

    def on_all(self, func: Callable) -> Callable:
        """Register a catch-all handler for ALL callback types."""
        self._catch_all.append(func)
        return func

    # === Convenience decorators ===

    @property
    def on_instance_status(self) -> Callable:
        return self.on(CallbackType.INSTANCE_STATUS)

    @property
    def on_restart(self) -> Callable:
        return self.on(CallbackType.RESTART)

    @property
    def on_reset(self) -> Callable:
        return self.on(CallbackType.RESET)

    @property
    def on_adb_result(self) -> Callable:
        return self.on(CallbackType.ADB_CMD)

    @property
    def on_app_installed(self) -> Callable:
        return self.on(CallbackType.APP_INSTALL)

    @property
    def on_app_uninstalled(self) -> Callable:
        return self.on(CallbackType.APP_UNINSTALL)

    @property
    def on_app_stopped(self) -> Callable:
        return self.on(CallbackType.APP_STOP)

    @property
    def on_app_restarted(self) -> Callable:
        return self.on(CallbackType.APP_RESTART)

    @property
    def on_app_started(self) -> Callable:
        return self.on(CallbackType.APP_START)

    @property
    def on_file_uploaded(self) -> Callable:
        return self.on(CallbackType.FILE_UPLOAD)

    @property
    def on_image_upgraded(self) -> Callable:
        return self.on(CallbackType.IMAGE_UPGRADE)

    @property
    def on_new_device(self) -> Callable:
        return self.on(CallbackType.ONE_KEY_NEW_DEVICE)

    @property
    def on_image_upload(self) -> Callable:
        return self.on(CallbackType.USER_IMAGE_UPLOAD)

    # === Event Processing ===

    def process(self, data: dict) -> CallbackEvent:
        """Process a callback payload and dispatch to registered handlers.

        Args:
            data: Raw callback JSON dict from VMOS.

        Returns:
            Parsed CallbackEvent.
        """
        event_type = data.get("taskBusinessType", 0)
        event_cls = _EVENT_MAP.get(event_type, CallbackEvent)
        event = event_cls.from_dict(data)

        logger.info(
            "Callback received: type=%d pad=%s task=%s",
            event_type,
            event.pad_code,
            event.task_id,
        )

        # Dispatch to type-specific handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                logger.exception("Error in callback handler for type %d", event_type)

        # Dispatch to catch-all handlers
        for handler in self._catch_all:
            try:
                handler(event)
            except Exception:
                logger.exception("Error in catch-all callback handler")

        return event

    # === Framework Integration ===

    def flask_view(self):
        """Flask view function for webhook endpoint.

        Usage:
            app.route("/webhook", methods=["POST"])(handler.flask_view)
        """
        try:
            from flask import request, jsonify
        except ImportError as e:
            raise ImportError(
                "Flask is required for webhook handler. "
                "Install with: pip install vmos-sdk[callbacks]"
            ) from e

        data = request.get_json(force=True)
        self.process(data)
        return jsonify({"code": 200, "msg": "ok"})
