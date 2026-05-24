# Anime Calendar Syncer

Syncs anime airing schedules from [AniList](https://anilist.co) to your Google Calendar, converted to Africa/Cairo time.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate a Google App Password (one-time)

No Google Cloud account needed — just:

1. Make sure **2-Step Verification** is enabled on your Google account
   → [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create a new App Password (name it anything, e.g. "Anime Syncer")
4. Copy the 16-character password shown

The tool will ask for your Gmail address and this password the first time you run `add` or `list`. Credentials are saved to `config.json` so you only enter them once.

---

## Usage

```bash
# Search for a currently-airing anime
python cli.py search "Dandadan"

# Add an anime by name (prompts to pick if multiple results)
python cli.py add "Dandadan"

# Add by AniList ID (more precise, get the ID from search)
python cli.py add 171018

# List all synced anime
python cli.py list

# Remove an anime from your calendar
python cli.py remove "Dandadan"
python cli.py remove 171018
```

## Notes

- Only **currently airing** anime have schedule data on AniList.
- Events are **weekly recurring** in your primary Google Calendar.
- If the anime has a known episode count, the recurrence ends after the final episode.
- All times are in **Africa/Cairo** timezone.
- Credentials stored in `config.json` — keep it private, don't commit it.
