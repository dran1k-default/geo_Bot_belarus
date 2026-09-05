import requests
HEADERS = {
    "User-Agent": "BelarusTravelPlanningBot/1.0 (contact: danila_developer@example.com)"
}
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
#finding places
def get_attractions(region_name, limit=30):
    search_query = f"Attractions in {region_name}"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_query,
        "format": "json",
        "srlimit": limit
    }

    try:
        response = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=10)
        print(f"[get_attractions] GET {response.url} -> {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            print(f"[get_attractions] found {len(search_results)} results for '{search_query}'")
#deleting info about city
            places_list = []
            for item in search_results:
                title = item.get("title")
                if title.lower() == region_name.lower():
                    continue
                places_list.append({"name": title, "type": "Sightseeing"})

#alternative search
            if not places_list:
                params["srsearch"] = region_name
                response = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=10)
                search_results = response.json().get("query", {}).get("search", [])
                for item in search_results:
                    title = item.get("title")
                    if title:
                        places_list.append({"name": title, "type": "Sightseeing"})

            return places_list
        else:
            print(f"Ошибка Википедии (Статус): {response.status_code}")
            return None
    except Exception as e:
        import traceback
        print(f"Ошибка Wikipedia API: {e}")
        traceback.print_exc()
        return None

#perlica
def get_place_image(title):
    params = {
        "action": "query",
        "prop": "pageimages|extracts",
        "piprop": "original",  #getting original picture size
        "exintro": True,  #Only small part of info
        "explaintext": True,  #clean htlm without tags
        "exsentences": 2,  #sentences limit
        "titles": title,
        "format": "json",
        "redirects": 1
    }

    try:
        response = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            image_url = None
            description = "No description available."

            for page_id, page_data in pages.items():
                # getting picture
                if "original" in page_data:
                    image_url = page_data["original"]["source"]
                # getting about
                if "extract" in page_data and page_data["extract"]:
                    description = page_data["extract"]

            return image_url, description
        return None, "Description temporary unavailable."
    except Exception:
        return None, "Description temporary unavailable."


def download_image_bytes(image_url, timeout=10):

    if not image_url:
        return None

    clean_url = image_url.split("?")[0]

    image_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://en.wikipedia.org/",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }
    try:
        resp = requests.get(clean_url, headers=image_headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.content
        print(f"[download_image_bytes] status {resp.status_code} for {clean_url}")
        return None
    except Exception as e:
        print(f"[download_image_bytes] error for {clean_url}: {e}")
        return None