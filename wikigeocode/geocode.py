import wikipedia
import wikipediaapi


def get_coordinates_from_wikipedia(place_name):
    """
    Tries to get latitude and longitude from a Wikipedia page about the place.

    Args:
        place_name (str): The name of the location to search.

    Returns:
        tuple or None: (latitude, longitude) if found, otherwise None.
    """
    wiki_wiki = wikipediaapi.Wikipedia("en")

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
