import wikipedia
import wikipediaapi
from dotenv import load_dotenv
import requests
import os


load_dotenv()
USER_AGENT = os.getenv("WIKI_USER_AGENT", "wikigeocode/0.1 (unknown user)")
if not USER_AGENT:
    raise ValueError("Missing WIKI_USER_AGENT in environment variables!")


def get_API_coordinates_from_wikipedia(place_name):
    """
    Tries to get latitude and longitude from a Wikipedia page about the place.

    Args:
        place_name (str): The name of the location to search.

    Returns:
        tuple or None: (latitude, longitude) if found, otherwise None.
    """
    wiki_wiki = wikipediaapi.Wikipedia(language="en", user_agent=USER_AGENT)

    try:
        # First get the page name via search
        search_results = wikipedia.search(place_name)
        if not search_results:
            return None

        page_title = search_results[0]
        page = wiki_wiki.page(page_title)

        if not page.exists():
            return None

        # Try to extract coordinates from the raw page content (usually in the infobox)
        lat = page.coordinates[0] if hasattr(page, "coordinates") else None
        lon = page.coordinates[1] if hasattr(page, "coordinates") else None

        if lat and lon:
            return lat, lon
        else:
            return None

    except Exception as e:
        print(f"Error looking up '{place_name}': {e}")
        return None


def get_coordinates_from_wikipedia(title: str):

    headers = {"User-Agent": USER_AGENT}
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "titles": title,
        "prop": "coordinates",
        "format": "json",
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        coords = page_data.get("coordinates", [{}])[0]
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        if coords:
            return {
                "page_url": page_url,
                "latitude": coords.get("lat"),
                "longitude": coords.get("lon"),
            }
    return None
