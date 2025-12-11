# SI 201 Final Project
# Your names: Isa Wilson, Amani, Rahma
# Your emails: ifwilson@umich.edu, aaggour@umich.edu, rmusse@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): ChatGPT
# If you worked with generative AI also add a statement for how you used it. We used ChatGPT for assistance debugging the code.
# e.g.: 
# Asked Chatgpt hints for debugging and suggesting the general sturcture of the code
import os
import json
import requests
import re
from API_keys import tmdb_key
from API_keys import omdb_key 
from API_keys import yt_key


def get_tmdb_movies(pages=5, output_file="movie.json"):
    movies = []

    for page in range(1, pages + 1):

        # Endpoint for popular movies
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            "api_key": tmdb_key.api_key,
            "language": "en-US",
            "page": page
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Loop through movies on the page
        for movie in data.get("results", []):
            tmdb_id = movie["id"]

            # Fetch detailed info
            detail_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
            detail_params = {
                "api_key": tmdb_key.api_key,
                "language": "en-US"
            }

            detail_res = requests.get(detail_url, params=detail_params)
            detail_data = detail_res.json()

            # Save relevant fields
            movies.append({
                "title": detail_data.get("title"),
                "tmdb_id": tmdb_id,
                "imdb_id": detail_data.get("imdb_id"),
                "budget": detail_data.get("budget")
            })

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=4)

    return movies



def get_omdb_ratings(imdb_ids, output_file="omdb_movies.json"):


    movies = []
    base_url = "http://www.omdbapi.com/"

    for imdb_id in imdb_ids:

        params = {
            "apikey": omdb_key.api_key,
            "i": imdb_id
        }
        detail = requests.get(base_url, params=params).json()

        # Store only fields we need
        movies.append({
            "title": detail.get("Title"),
            "imdb_id": imdb_id,
            "genre": detail.get("Genre"),
            "imdb_rating": detail.get("imdbRating")
        })

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=4)

    return movies


def get_youtube_trailers(output_file="youtube_trailers.json"):
    trailers = []
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    next_page_token = None

    for i in range(4): 
        params_search = {
            "key": yt_key.api_key,
            "q": "official trailer", 
            "type": "video",
            "part": "snippet",
            "maxResults": 50
        }

        if next_page_token: 
            params_search["pageToken"] = next_page_token

        response = requests.get(search_url, params=params_search)
        data = response.json()
        items = data.get("items", [])

        if not items: 
            break 

        for item in items: 
            title = item["snippet"]["title"]
            title = re.sub(r"&#39;", "'", title)
            title = re.sub(r"[^\x20-\x7E]", "", title).strip()
            video_id = item["id"]["videoId"]

            if any(x in title.lower() for x in ["season"]): 
                continue

            stats_response = requests.get(video_url, params={
                "key": yt_key.api_key,
                "id": video_id,
                "part": "statistics"
            }).json()

            items_stats = stats_response.get("items", [])
            if not items_stats: 
                continue
            s = items_stats[0].get("statistics", {})
                               
            trailers.append({
                "title": title,
                "video_id": video_id,
                "view_count": int(s.get("viewCount", 0)), 
                "like_count": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0))
            })

        next_page_token = data.get("nextPageToken")
        if not next_page_token: 
            break

    seen_vid = []
    unique_trailers = []

    for t in trailers: 
        title = t["title"].lower()
        base = re.split(r"\|", title)[0]
        base = re.split(r"official", base)[0]
        base = "".join(re.split(r"\(.*?\)", base))
        words = re.findall(r"[a-z0-9]+", base)
        cleaned_title = " ".join(words)
        if cleaned_title not in seen_vid: 
            seen_vid.append(cleaned_title)
            unique_trailers.append(t)

    with open(output_file, "w", encoding="utf-8") as f: 
        json.dump(unique_trailers, f, indent=4)

    return unique_trailers


def main():
    # 1. Fetch TMDB movies
    tmdb_movies = get_tmdb_movies(pages=6)
    print("TMDB movies collected:", len(tmdb_movies))

    # 2. Extract IMDb IDs from TMDB movies
    imdb_ids = [m["imdb_id"] for m in tmdb_movies if m.get("imdb_id")]

    # 3. Fetch OMDB ratings using the IMDb IDs
    omdb_movies = get_omdb_ratings(imdb_ids)
    print("OMDB movies collected:", len(omdb_movies))

    youtube_trailers = get_youtube_trailers()
    print("Youtube trailers collected:", len(youtube_trailers))


if __name__ == "__main__":
    main()