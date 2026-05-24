import caldav
import click

from . import config as cfg

CALDAV_URL = "https://www.google.com/calendar/dav/{email}/"


def get_credentials() -> tuple[str, str]:
    """Return (email, app_password), prompting and saving if not already stored."""
    data = cfg.load_config()
    email = data.get("email")
    app_password = data.get("app_password")

    if not email or not app_password:
        click.echo("\nGoogle Calendar setup (one-time)")
        click.echo("  1. Make sure 2-Step Verification is ON at myaccount.google.com/security")
        click.echo("  2. Go to myaccount.google.com/apppasswords")
        click.echo('  3. Create an App Password (name it anything, e.g. "Anime Syncer")')
        click.echo("  4. Copy the 16-character password shown\n")
        email = click.prompt("Your Gmail address")
        app_password = click.prompt("App Password (16 chars, spaces are fine)", hide_input=True)
        app_password = app_password.replace(" ", "")
        cfg.save_config({"email": email, "app_password": app_password})
        click.echo(f"Credentials saved to {cfg.CONFIG_FILE}\n")

    return email, app_password


def get_calendar() -> caldav.Calendar:
    """Connect to Google CalDAV and return the primary calendar."""
    email, app_password = get_credentials()
    url = CALDAV_URL.format(email=email)
    client = caldav.DAVClient(url=url, username=email, password=app_password)
    principal = client.principal()
    calendars = principal.calendars()
    if not calendars:
        raise RuntimeError("No calendars found in your Google account.")
    return calendars[0]
