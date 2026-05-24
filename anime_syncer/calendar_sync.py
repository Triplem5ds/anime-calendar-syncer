import uuid
from datetime import datetime, timedelta, timezone

import pytz
from icalendar import Calendar, Event

from . import auth
from . import config as cfg

USER_TZ = pytz.timezone("Africa/Cairo")


def _build_ical(anime: dict) -> tuple[str, str]:
    """Return (uid, ical_string) for the anime's weekly recurring event."""
    next_airing = anime["nextAiringEpisode"]
    airing_utc = datetime.fromtimestamp(next_airing["airingAt"], tz=timezone.utc)
    airing_local = airing_utc.astimezone(USER_TZ)

    total_episodes = anime.get("episodes")
    current_episode = next_airing["episode"]
    remaining = (total_episodes - current_episode + 1) if total_episodes else None

    title = anime["title"]["english"] or anime["title"]["romaji"]

    cal = Calendar()
    cal.add("prodid", "-//Anime Calendar Syncer//EN")
    cal.add("version", "2.0")

    event = Event()
    uid = str(uuid.uuid4())
    event.add("uid", uid)
    event.add("summary", f"[Anime] {title}")
    event.add("description", f"AniList ID: {anime['id']}\nEpisode {current_episode} onward")
    event.add("dtstart", airing_local)
    event.add("dtend", airing_local + timedelta(minutes=24))

    rrule: dict = {"freq": "weekly"}
    if remaining:
        rrule["count"] = remaining
    event.add("rrule", rrule)

    cal.add_component(event)
    return uid, cal.to_ical().decode("utf-8")


def add_anime(anime: dict) -> str:
    """Create a weekly recurring CalDAV event. Returns the UID."""
    uid, ical = _build_ical(anime)
    calendar = auth.get_calendar()
    calendar.save_event(ical)

    title = anime["title"]["english"] or anime["title"]["romaji"]
    synced = cfg.load_synced()
    synced[str(anime["id"])] = {"uid": uid, "title": title}
    cfg.save_synced(synced)

    return uid


def list_synced_anime() -> list[dict]:
    """Return locally tracked synced anime."""
    synced = cfg.load_synced()
    return [{"anilist_id": aid, **info} for aid, info in synced.items()]


def remove_anime(anilist_id: int) -> bool:
    """Delete the calendar event for the given AniList ID. Returns True if found."""
    synced = cfg.load_synced()
    key = str(anilist_id)
    entry = synced.get(key)
    if not entry:
        return False

    uid = entry["uid"]
    calendar = auth.get_calendar()

    try:
        event = calendar.event_by_uid(uid)
        event.delete()
    except Exception:
        pass  # event may have been manually deleted already

    del synced[key]
    cfg.save_synced(synced)
    return True
