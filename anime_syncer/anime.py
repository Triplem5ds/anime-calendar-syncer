import requests

ANILIST_URL = "https://graphql.anilist.co"

_SEARCH_QUERY = """
query ($search: String) {
  Page(perPage: 5) {
    media(search: $search, type: ANIME, status_in: [RELEASING]) {
      id
      title { romaji english }
      status
      nextAiringEpisode { airingAt episode }
      episodes
    }
  }
}
"""

_BY_ID_QUERY = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    title { romaji english }
    status
    nextAiringEpisode { airingAt episode }
    episodes
  }
}
"""


def _post(query, variables):
    resp = requests.post(ANILIST_URL, json={"query": query, "variables": variables}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"][0]["message"])
    return data["data"]


def search_anime(name: str) -> list[dict]:
    data = _post(_SEARCH_QUERY, {"search": name})
    return data["Page"]["media"]


def get_anime_by_id(anime_id: int) -> dict:
    data = _post(_BY_ID_QUERY, {"id": anime_id})
    return data["Media"]
