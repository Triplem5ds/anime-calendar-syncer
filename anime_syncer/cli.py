import sys
from datetime import datetime, timezone

import click
import pytz

from . import anime as anime_api
from . import calendar_sync

USER_TZ = pytz.timezone("Africa/Cairo")


def _fmt_airing(next_airing: dict | None) -> str:
    if not next_airing:
        return "No upcoming episode"
    utc = datetime.fromtimestamp(next_airing["airingAt"], tz=timezone.utc)
    local = utc.astimezone(USER_TZ)
    return local.strftime("%A, %d %b %Y at %H:%M %Z")


@click.group()
def cli():
    """Sync anime airing schedules to your Google Calendar."""


@cli.command()
@click.argument("name")
def search(name):
    """Search for a currently airing anime by name."""
    click.echo(f'Searching AniList for "{name}"...')
    try:
        results = anime_api.search_anime(name)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not results:
        click.echo("No currently-airing anime found.")
        return

    for media in results:
        title = media["title"]["english"] or media["title"]["romaji"]
        airing_str = _fmt_airing(media.get("nextAiringEpisode"))
        ep_total = media.get("episodes") or "?"
        click.echo(f"  [{media['id']}] {title}  —  Next: {airing_str}  (total eps: {ep_total})")


@cli.command()
@click.argument("name_or_id")
def add(name_or_id):
    """Add an anime to your Google Calendar by name or AniList ID."""
    if name_or_id.isdigit():
        click.echo(f"Fetching AniList ID {name_or_id}...")
        try:
            chosen = anime_api.get_anime_by_id(int(name_or_id))
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    else:
        click.echo(f'Searching for "{name_or_id}"...')
        try:
            results = anime_api.search_anime(name_or_id)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        if not results:
            click.echo("No currently-airing anime found with that name.")
            sys.exit(1)

        if len(results) == 1:
            chosen = results[0]
        else:
            click.echo("\nMultiple results found:")
            for i, media in enumerate(results):
                title = media["title"]["english"] or media["title"]["romaji"]
                airing_str = _fmt_airing(media.get("nextAiringEpisode"))
                click.echo(f"  {i + 1}. [{media['id']}] {title}  —  Next: {airing_str}")
            idx = click.prompt("Pick a number", type=click.IntRange(1, len(results))) - 1
            chosen = results[idx]

    title = chosen["title"]["english"] or chosen["title"]["romaji"]
    next_airing = chosen.get("nextAiringEpisode")

    if not next_airing:
        click.echo(f'"{title}" has no upcoming episode schedule on AniList right now.')
        sys.exit(1)

    airing_str = _fmt_airing(next_airing)
    click.echo(f'\nReady to add "{title}"')
    click.echo(f"  Next episode ({next_airing['episode']}): {airing_str}")
    click.echo(f"  AniList ID: {chosen['id']}")

    if not click.confirm("\nAdd to Google Calendar?"):
        click.echo("Cancelled.")
        return

    click.echo("Connecting to Google Calendar...")
    try:
        uid = calendar_sync.add_anime(chosen)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f'Done! Weekly event created for "{title}".')
    click.echo(f"  Airing time (Cairo): {airing_str}")
    click.echo(f"  Event UID: {uid}")


@cli.command("list")
def list_cmd():
    """List anime currently synced to your Google Calendar."""
    entries = calendar_sync.list_synced_anime()

    if not entries:
        click.echo("No anime synced yet. Use `anime-syncer add` to get started.")
        return

    for entry in entries:
        click.echo(f"  [{entry['anilist_id']}] {entry['title']}")


@cli.command()
@click.argument("name_or_id")
def remove(name_or_id):
    """Remove an anime from your Google Calendar by name or AniList ID."""
    if name_or_id.isdigit():
        anilist_id = int(name_or_id)
    else:
        click.echo(f'Searching for "{name_or_id}"...')
        try:
            results = anime_api.search_anime(name_or_id)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

        if not results:
            click.echo("Anime not found on AniList.")
            sys.exit(1)

        if len(results) == 1:
            chosen = results[0]
        else:
            for i, media in enumerate(results):
                title = media["title"]["english"] or media["title"]["romaji"]
                click.echo(f"  {i + 1}. [{media['id']}] {title}")
            idx = click.prompt("Pick a number", type=click.IntRange(1, len(results))) - 1
            chosen = results[idx]

        anilist_id = chosen["id"]

    if not click.confirm(f"Remove anime (AniList ID: {anilist_id}) from Google Calendar?"):
        click.echo("Cancelled.")
        return

    click.echo("Connecting to Google Calendar...")
    try:
        found = calendar_sync.remove_anime(anilist_id)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not found:
        click.echo("That anime isn't in your synced list.")
    else:
        click.echo("Removed from your Google Calendar.")
