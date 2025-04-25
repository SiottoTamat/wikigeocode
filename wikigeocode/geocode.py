import wikipedia
import wikipediaapi
from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
USER_AGENT = os.getenv("WIKI_USER_AGENT", "wikigeocode/0.1 (unknown user)")
if not USER_AGENT:
    raise ValueError("Missing WIKI_USER_AGENT in environment variables!")
# Set common headers
HEADERS = {"User-Agent": USER_AGENT}


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


def get_related_pages_from_wikipedia(place_name):
    try:
        # First get the page name via search
        search_results = wikipedia.search(place_name)
        if not search_results:
            return None
        return search_results

    except Exception as e:
        print(f"Error looking up '{place_name}': {e}")
        return None


def get_coordinates_from_wikidata(title: str):
    try:
        # First, get Wikidata ID from Wikipedia page
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": title,
            "prop": "pageprops",
            "format": "json",
        }
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        wikidata_id = None
        for page_id, page_data in pages.items():
            wikidata_id = page_data.get("pageprops", {}).get("wikibase_item")

        if not wikidata_id:
            return None

        # Query Wikidata for coordinates
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        entities = data.get("entities", {})
        entity = entities.get(wikidata_id, {})
        claims = entity.get("claims", {})
        coords_claim = claims.get("P625")

        if not coords_claim:
            return None

        coords_data = (
            coords_claim[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
        )
        lat = coords_data.get("latitude")
        lon = coords_data.get("longitude")

        if lat is not None and lon is not None:
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            return {
                "page_id": wikidata_id,
                "page_url": page_url,
                "latitude": lat,
                "longitude": lon,
            }

    except Exception as e:
        print(f"Error getting coordinates from Wikidata for '{title}': {e}")

    return None


def scrape_coordinates_from_wikipedia(title: str):
    try:
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        geo = soup.find(class_="geo")
        if geo:
            lat, lon = geo.text.split(";")
            return {
                "page_url": url,
                "latitude": float(lat.strip()),
                "longitude": float(lon.strip()),
            }
    except Exception as e:
        print(f"Error scraping coordinates for '{title}': {e}")

    return None


def get_coordinates_from_page_wikipedia(title: str):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "coordinates",
        "format": "json",
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            coords = page_data.get("coordinates", [{}])[0]
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            if coords:
                return {
                    "page_url": page_url,
                    "page_id": page_id,
                    "latitude": coords.get("lat"),
                    "longitude": coords.get("lon"),
                }
    except Exception as e:
        print(f"Error getting coordinates from Wikipedia API for '{title}': {e}")
    return None


def get_best_coordinates(place_name: str):
    """
    Tries to get coordinates for a place using Wikipedia API, Wikidata, and HTML scraping.
    """

    pages = get_related_pages_from_wikipedia(place_name)
    if not pages:
        return None

    title = pages[0]  # take the most relevant page

    # 1. Try Wikipedia API
    result = get_coordinates_from_page_wikipedia(title)
    if result:
        return result

    # 2. Try Wikidata
    result = get_coordinates_from_wikidata(title)
    if result:
        return result

    # 3. Try Scraping
    result = scrape_coordinates_from_wikipedia(title)
    if result:
        return result

    return None
