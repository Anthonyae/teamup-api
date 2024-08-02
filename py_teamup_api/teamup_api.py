"""
This module provides functions for managing resources in TeamUp (calendar app).
"""

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MAIN_CALENDAR_IDENTIFIER = "zrqurm"

TEAMUP_TOKEN = os.getenv("TEAMUP_TOKEN")
TEAMUP_BEARER_TOKEN = os.getenv("TEAMUP_BEARER_TOKEN")
if not TEAMUP_TOKEN or not TEAMUP_BEARER_TOKEN:
    raise EnvironmentError(
        "Required environment variables TEAMUP_TOKEN or BEARER_TOKEN not set."
    )


class UtilityFile:
    """
    Class for handling files
    """

    def save_json(self, data_obj: dict, filename: str) -> None:
        """
        Saves dict to json filename.
        """
        filename = filename.replace(".json", "") + ".json"
        data_file_path = os.path.join(DATA_DIR, filename)
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)

        with open(data_file_path, "w", encoding="utf-8") as f:
            json.dump(data_obj, f, indent=4)

    def open_json(self, filename: str, create_if_not_exits=False) -> dict:
        """
        Returns dict of given filename
        """
        filename = str(filename).replace(".json", "") + ".json"
        data_file_path = os.path.join(DATA_DIR, filename)

        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            if create_if_not_exits:
                os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
                with open(data_file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                return {}
            raise FileNotFoundError(
                f"File '{filename}' not found and create_if_not_exists is False."
            ) from e


class TeamUP:
    """
    Returns an object for interacting with the TeamUP.
    """

    _BASE_URL = "https://api.teamup.com/"

    def __init__(self):
        self.headers = {
            "Teamup-Token": TEAMUP_TOKEN,
            "Accept": "application/json",
            "Authorization": f"Bearer {TEAMUP_BEARER_TOKEN}",
        }

    def _request(self, method: str, resource: str, **kwargs) -> dict:
        url = self._BASE_URL + resource
        response = requests.request(
            method=method, url=url, headers=self.headers, timeout=20.00, **kwargs
        )
        try:
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to {method} for url -> {url}: {response.status_code} - {response.text}"
            ) from e

    def get(self, resource: str, params=None) -> dict:
        """General request"""
        return self._request(method="GET", resource=resource, params=params)

    def put(self, resource: str, params=None) -> dict:
        """General request"""
        return self._request(method="PUT", resource=resource, params=params)

    def delete(self, resource: str, params=None) -> dict:
        """General request"""
        return self._request(method="DELETE", resource=resource, params=params)

    def post(self, resource: str, params: dict = None, data: dict = None) -> dict:
        """General request"""
        return self._request(method="POST", resource=resource, params=params, json=data)

    def get_calendar(self, calendar_key_or_id: int) -> dict:
        """
        Get calendar:
            - Either the calendar_secret_key (ksXXXXX)
            - Or calendar_id (tied to user account - requires login creds)
        """
        return self.get(f"calendars/{calendar_key_or_id}")

    def get_subcalendars(self, calendar_key_or_id: str) -> list[dict]:
        """Returns children calendars for given calendar id."""
        return self.get(f"{calendar_key_or_id}/subcalendars")["subcalendars"]

    def get_subcalendar_by_name(
        self, calendar_key_or_id: str, calendar_name: str
    ) -> int:
        """
        Returns subcalendar_id for the given calendar_name under the main_calendar_K_ID provided.
        """
        sub_calendars = self.get_subcalendars(calendar_key_or_id)
        for sub_calendar in sub_calendars:
            if sub_calendar["name"] == calendar_name:
                return sub_calendar["id"]
        return None

    def get_calendar_events(
        self, calendar_key_or_id: str, query: dict = None
    ) -> list[dict]:
        """
        Returns events for today if date range not given.

        Ex. Query parameters for events for the specific date.
        dates = {
            "startDate": "2024-07-19",
            "endDate": "2024-07-19",
        }
        """
        return self.get(f"{calendar_key_or_id}/events", params=query)["events"]

    def create_calendar_event(
        self, calendar_key_or_id: str, calendar_event: "CalendarEvent"
    ) -> dict:
        """
        Creates event for specified calendar, provided the CalendarEvent object.
        """
        if not isinstance(calendar_event, self.CalendarEvent):
            raise BaseException(
                "The method create_calendar_event requires a CalendarEvent object."
            )
        return self.post(f"{calendar_key_or_id}/events", data=calendar_event.to_dict())

    def delete_calendar_event(
        self,
        calendar_key_or_id: str,
        event_id: str,
        recuring_deletion: "RecurringDeletion" = None,
    ) -> int:
        """
        Deletes an event from the specified calendar.

        Returns: undo_id for this deletion action.
        """
        params = {"reddit": recuring_deletion.value if recuring_deletion else None}
        return self.delete(
            resource=f"{calendar_key_or_id}/events/{event_id}", params=params
        )["undo_id"]

    @dataclass
    class CalendarEvent:
        """
        Data class used to create events in teamup. By default all parameters are null except:
            - Required parameters of subcalendar_ids and title. The minimum information required to
            create an event.
            - start_dt and end_dt, these are set to be all day events (by default).

        """

        subcalendar_ids: List[int]  # required
        title: Optional[str]  # required
        start_dt: datetime = field(
            default_factory=lambda: datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        )  # required
        end_dt: datetime = field(
            default_factory=lambda: datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            )
        )  # required
        all_day: bool = False
        rrule: Optional[str] = None
        notes: Optional[str] = None
        location: Optional[str] = None
        who: Optional[str] = None
        signup_enabled: bool = False
        comments_enabled: bool = False
        custom: Optional[Dict[str, Union[str, List[str]]]] = None

        def to_dict(self):
            event_dict = asdict(self)
            # Convert datetime fields to string format
            if isinstance(event_dict["start_dt"], datetime):
                event_dict["start_dt"] = event_dict["start_dt"].isoformat()
            if isinstance(event_dict["end_dt"], datetime):
                event_dict["end_dt"] = event_dict["end_dt"].isoformat()
            return event_dict

    class RecurringDeletion(Enum):
        SINGLE = "single"
        FUTURE = "future"
        ALL = "all"


def add_numbers(a: int, b: int) -> int:
    """
    Test doc string.
    """
    return a + b


if __name__ == "__main__":
    x = TeamUP()
    # z = x.get_subcalendars(MAIN_CALENDAR_IDENTIFIER)
    # z = x.get_subcalendar_by_name(calendar_key_or_id=MAIN_CALENDAR_IDENTIFIER, "habit")
    # z = x.get_calendar_events(MAIN_CALENDAR_IDENTIFIER)
    z = x.create_calendar_event(
        MAIN_CALENDAR_IDENTIFIER,
        TeamUP.CalendarEvent(
            [13458686],
            "testing new creation",
            datetime(2024, 7, 19, 22),
            datetime(2024, 7, 19, 23),
        ),
    )
    # z = x.delete_calendar_event(MAIN_CALENDAR_IDENTIFIER, 1714783406)
