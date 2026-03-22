from abc import ABC, abstractmethod
from typing import Any

from src.common.config import Settings
from src.common.notifications import NotificationService


class BaseService(ABC):
    """Abstract base class for all application services."""

    def __init__(self, config: Settings, notification_service: NotificationService):
        self.config = config
        self.notification_service = notification_service

    @abstractmethod
    def run(self, **kwargs: Any) -> None:
        """
        Main entry point for service execution.
        Subclasses must implement their specific logic here.
        """
        pass
