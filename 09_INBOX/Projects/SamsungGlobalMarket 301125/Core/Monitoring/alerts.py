# MEMORY_ID: TASK_AUTOMATION_MONITORING
# TIMESTAMP: 2025-11-09T21:35:30+01:00
# AUTHOR: Cursor_Omega

"""
Gestão de alertas por Slack Webhook e e-mail.
"""

from __future__ import annotations

import json
import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict, Optional

import requests

from Core.Config import ConfigManager
from Core.Logger import get_logger

logger = get_logger("prometheus.alerts")


class AlertManager:
    def __init__(self, config: Optional[Dict] = None) -> None:
        manager = ConfigManager.get_instance()
        self.config = config or manager.get("alerts", default={})
        self.slack_webhook: Optional[str] = self.config.get("slack_webhook")
        self.email_cfg: Dict = self.config.get("email", {})

    def notify(self, title: str, message: str) -> None:
        self._notify_slack(title, message)
        self._notify_email(title, message)

    def _notify_slack(self, title: str, message: str) -> None:
        if not self.slack_webhook:
            return
        payload = {
            "text": f"*{title}*\n{message}",
        }
        try:
            response = requests.post(self.slack_webhook, data=json.dumps(payload), timeout=5)
            response.raise_for_status()
            logger.info("Alerta Slack enviado.")
        except Exception as exc:
            logger.warning("Falha ao enviar alerta Slack: %s", exc)

    def _notify_email(self, subject: str, body: str) -> None:
        if not self.email_cfg or not self.email_cfg.get("enabled"):
            return

        recipients = self.email_cfg.get("recipients", [])
        if not recipients:
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.email_cfg.get("username")
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(self.email_cfg.get("smtp_server"), self.email_cfg.get("smtp_port", 587)) as server:
                server.starttls(context=context)
                server.login(self.email_cfg.get("username"), self.email_cfg.get("password"))
                server.send_message(msg)
            logger.info("Alerta e-mail enviado.")
        except Exception as exc:
            logger.warning("Falha ao enviar alerta e-mail: %s", exc)

