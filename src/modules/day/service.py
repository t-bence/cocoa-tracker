import json
import logging
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI

from src.common.base import BaseService
from src.common.config import Settings
from src.common.notifications import NotificationService, TelegramNotificationService

logger = logging.getLogger(__name__)


class DayService(BaseService):
    """Service to retrieve Google Calendar events and summarize the day with an LLM."""

    def run(self, **kwargs: Any) -> None:
        logger.info("Starting Day service execution")

        if not self.config.google_service_account_info:
            self.notification_service.send_message(
                "Error: GOOGLE_SERVICE_ACCOUNT_INFO is not configured."
            )
            return

        try:
            user_tz_str, events = self._get_upcoming_events()
            if not events:
                self.notification_service.send_message(
                    "You have no more meetings scheduled for today. Enjoy your day! ☀️"
                )
                return

            event_list = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                try:
                    # Convert UTC event time to user's local time for display
                    dt_utc = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    dt_local = dt_utc.astimezone(ZoneInfo(user_tz_str))
                    time_str = dt_local.strftime("%H:%M")
                except (ValueError, ZoneInfoNotFoundError):
                    time_str = start  # Fallback for all-day events or errors

                event_list.append(f"• {time_str}: {event.get('summary', 'No Title')}")

            raw_list_text = "".join(event_list)

            if self.config.openai_api_key:
                logger.info("Summarizing with LLM")
                summary = self._summarize_with_llm(raw_list_text)
                message = f"""*Your day at a glance:* 📅

{summary}"""
            else:
                logger.warning("OPENAI_API_KEY not set, sending raw list")
                message = f"""*Your remaining day:* 📅

{raw_list_text}"""

            self.notification_service.send_message(message)

        except Exception as e:
            logger.exception("Failed to execute Day service")
            self.notification_service.send_message(f"Error in Day service: {str(e)}")

    def _get_upcoming_events(self) -> tuple[str, list[dict[str, Any]]]:
        """
        Fetches the calendar's timezone and the remaining events for today.
        Returns a tuple of (timezone_string, event_list).
        """
        assert self.config.google_service_account_info is not None
        info = json.loads(self.config.google_service_account_info)
        credentials = service_account.Credentials.from_service_account_info(info)
        scoped_credentials = credentials.with_scopes(
            ["https://www.googleapis.com/auth/calendar.readonly"]
        )

        service = build("calendar", "v3", credentials=scoped_credentials)

        # 1. Fetch calendar metadata to get its timezone
        calendar_info = (
            service.calendars().get(calendarId=self.config.google_calendar_id).execute()
        )
        user_tz_str = calendar_info.get("timeZone", "UTC")
        user_tz = ZoneInfo(user_tz_str)

        # 2. Calculate time range in the calendar's timezone
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(user_tz)

        end_of_day_local = now_local.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        logger.info(
            f"Fetching events from {now_local.isoformat()} to {end_of_day_local.isoformat()} in timezone {user_tz_str}"
        )

        events_result = (
            service.events()
            .list(
                calendarId=self.config.google_calendar_id,
                timeMin=now_utc.isoformat(),
                timeMax=end_of_day_local.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return user_tz_str, events_result.get("items", [])

    def _summarize_with_llm(self, events_text: str) -> str:
        """Uses OpenAI library to summarize via OpenRouter."""
        client = OpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openrouter_base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/google-gemini/cocoa-tracker",
                "X-Title": "Cocoa Tracker",
            },
        )

        prompt = (
            "You are a helpful personal assistant. Below is a list of my remaining meetings for today. "
            "Please provide a very concise, professional, and friendly summary (2-3 sentences max) "
            "of what my day looks like from now on. Use bullet points if it helps clarity."
            f"Meetings: {events_text}"
        )

        response = client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": "You are a concise personal assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=150,
        )

        return response.choices[0].message.content or "Could not generate summary."


def create_day_service(
    config: Settings,
    notification_service: NotificationService | None = None,
) -> DayService:
    notification_service = notification_service or TelegramNotificationService(
        config.telegram_token, config.telegram_chat_id
    )
    return DayService(config, notification_service)
