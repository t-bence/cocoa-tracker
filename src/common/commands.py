import logging
from abc import ABC, abstractmethod
from typing import Any

from src.common.base import BaseService
from src.common.config import Settings
from src.modules.concerts.service import create_concert_service
from src.modules.home.service import create_home_service
from src.modules.day.service import create_day_service

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """Abstract base class for all bot commands."""

    def __init__(self, config: Settings):
        self.config = config

    @abstractmethod
    def get_service(self) -> BaseService:
        """Returns the service associated with this command."""
        pass

    def execute(self, **kwargs: Any) -> None:
        """Standard execution flow for all commands."""
        service = self.get_service()
        service.run(**kwargs)


class QueryCommand(BaseCommand):
    """Handles the /query command for concert updates."""

    def get_service(self) -> BaseService:
        return create_concert_service(self.config)

    def execute(self, **kwargs: Any) -> None:
        logger.info("Processing /query command")
        # For /query, we explicitly want to force the check.
        # Pop 'force' if it exists in kwargs to avoid duplicate argument error.
        kwargs.pop("force", None)
        super().execute(force=True, **kwargs)


class HomeCommand(BaseCommand):
    """Handles the /home command for IoT status."""

    def get_service(self) -> BaseService:
        return create_home_service(self.config)


class DayCommand(BaseCommand):
    """Handles the /day command for Google Calendar summary."""

    def get_service(self) -> BaseService:
        return create_day_service(self.config)


class DefaultCommand(BaseCommand):
    """Handles standard scheduled runs (or unknown commands)."""

    def get_service(self) -> BaseService:
        return create_concert_service(self.config)


class CommandRegistry:
    """Registry for bot commands, facilitating easy routing."""

    def __init__(self, config: Settings):
        self.config = config
        self._commands: dict[str, BaseCommand] = {
            "/query": QueryCommand(config),
            "/home": HomeCommand(config),
            "/day": DayCommand(config),
        }
        self._default = DefaultCommand(config)

    def get_command(self, command_text: str | None) -> BaseCommand:
        """Returns the appropriate command object for the given text."""
        if not command_text:
            return self._default
        return self._commands.get(command_text, self._default)
