import sqlite3
import json

# Create database tables
import sqlite3
import json

# Create database tables
def init_db(db_name="movies.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # TMDB table 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tmdb_movies (
            tmdb_id INTEGER PRIMARY KEY,
            imdb_id TEXT,
            title TEXT,
            budget INTEGER
        );
    """)

    # OMDB table 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS omdb_movies (
            omdb_id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT,
            title TEXT,
            genre TEXT,
            imdb_rating REAL
        );
    """)

    # Youtube trailers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS youtube_trailers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, 
            video_id TEXT UNIQUE, 
            view_count INTEGER,
            like_count INTEGER, 
            comment_count INTEGER
        );
    """)

    conn.commit()
    conn.close()


# Insert TMDB row
def save_tmdb_movies_to_db(conn, movies):
    cur = conn.cursor()
    count_added = 0
    for movie in movies:
        if count_added >= 25:
            break
        try:
            cur.execute("""
                INSERT OR REPLACE INTO tmdb_movies (tmdb_id, imdb_id, title, budget)
                VALUES (?, ?, ?, ?);
            """, (
                movie["tmdb_id"],
                movie.get("imdb_id"),
                movie.get("title", ""),
                movie.get("budget")
            ))
            count_added += 1
        except Exception as e:
            print("Error saving TMDB movie:", e)
    conn.commit()
    print("TMDB: Added", count_added, "movies.")


# Insert OMDB row
def save_omdb_movies_to_db(conn, movies):
    cur = conn.cursor()
    count_added = 0
    for movie in movies:
        if count_added >= 25:
            break

        # Handle bad ratings
        rating = movie.get("imdb_rating")
        if rating is None or rating == "" or rating == "N/A":
            rating = None
        else:
            try:
                rating = float(rating)
            except:
                rating = None

        try:
            cur.execute("""
                INSERT INTO omdb_movies (imdb_id, title, genre, imdb_rating)
                VALUES (?, ?, ?, ?);
            """, (
                movie.get("imdb_id"),
                movie.get("title", ""),
                movie.get("genre"),
                rating
            ))
            count_added += 1
        except Exception as e:
            print("Error saving OMDB movie:", e)
    conn.commit()
    print("OMDB: Added", count_added, "movies.")


def save_youtube_trailers_to_db(conn, trailers): 
    cur = conn.cursor()
    count_added = 0 
    for t in trailers: 
        if count_added >= 25:
                break  
        try: 
            before = conn.total_changes
            cur.execute("""
                INSERT OR IGNORE INTO youtube_trailers 
                (title, video_id, view_count, like_count, comment_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                t["title"],
                t["video_id"],
                t["view_count"],
                t["like_count"],
                t["comment_count"],
            ))
            after = conn.total_changes

            if after > before: 
                count_added += 1

        except Exception as e:
            print("Error saving YouTube trailers:", e)

    conn.commit()

    print("YouTube: Added", count_added, "trailers.")
# MAIN function for database.py
# Reads JSON files and inserts them
def main():
    init_db()
    conn = sqlite3.connect("movies.db")

    # Load TMDB JSON and save
    with open("movie.json", "r") as f:
        tmdb_movies = json.load(f)
    save_tmdb_movies_to_db(conn, tmdb_movies)

    # Load OMDB JSON and save
    with open("omdb_movies.json", "r") as f:
        omdb_movies = json.load(f)
    save_omdb_movies_to_db(conn, omdb_movies)

    # Load YouTube JSON 
    with open("youtube_trailers.json", "r") as f:
        youtube_trailers = json.load(f)
    save_youtube_trailers_to_db(conn, youtube_trailers)

    conn.close()
    print("Database successfully populated.")



if __name__ == "__main__":
    main()

