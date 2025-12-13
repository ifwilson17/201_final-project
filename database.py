# Create database tables
import sqlite3
import json
import re

# Create database tables
def init_db(db_name="movies.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

# TMDB table 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tmdb_movies (
        tmdb_id INTEGER PRIMARY KEY,
        imdb_id INTEGER,
        title TEXT,
        budget INTEGER
        );
    """)

# OMDB table 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS omdb_movies (
        omdb_id INTEGER PRIMARY KEY AUTOINCREMENT,
        imdb_id INTEGER,
        title TEXT,
        genre_id INTEGER,
        imdb_rating REAL,
        FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
        );
    """)


# Genre lookup table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
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


# Insert TMDB 
def save_tmdb_movies_to_db(conn, movies):
    cur = conn.cursor()
    count_added = 0
    for movie in movies:
        cur.execute("SELECT 1 FROM tmdb_movies WHERE tmdb_id = ?", (movie["tmdb_id"],))
        if cur.fetchone():
            continue

        if count_added >= 25:
            break

        try:
            cur.execute("""
                INSERT INTO tmdb_movies (tmdb_id, imdb_id, title, budget)
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


# Insert OMDB 
def save_omdb_movies_to_db(conn, movies):
    cur = conn.cursor()
    count_added = 0

    for movie in movies:
        if count_added >= 25:
            break

        imdb_id = movie.get("imdb_id")

        rating = movie.get("imdb_rating")
        if rating in (None, "", "N/A"):
            rating = None
        else:
            try:
                rating = float(rating)
            except:
                rating = None

        genre_string = movie.get("genre")
        if genre_string:
            first_genre = genre_string.split(",")[0].strip()

            cur.execute("SELECT genre_id FROM genres WHERE name = ?", (first_genre,))
            row = cur.fetchone()

            if row:
                genre_id = row[0]
            else:
                cur.execute("INSERT INTO genres (name) VALUES (?)", (first_genre,))
                genre_id = cur.lastrowid
        else:
            genre_id = None

        try:
            cur.execute("""
                INSERT INTO omdb_movies (imdb_id, title, genre_id, imdb_rating)
                VALUES (?, ?, ?, ?);
            """, (imdb_id, movie.get("title", ""), genre_id, rating))

            count_added += 1

        except Exception as e:
            print("Error saving OMDB movie:", e)

    conn.commit()
    print("OMDB: Added", count_added, "movies.")



# Insert youtube trailers 
def save_youtube_trailers_to_db(conn, trailers):
    cur = conn.cursor()
    count_added = 0
    for t in trailers:
        cur.execute("SELECT 1 FROM youtube_trailers WHERE video_id = ?", (t["video_id"],))
        if cur.fetchone():
            continue

        if count_added >= 25:
            break

        try:
            cur.execute("""
                INSERT INTO youtube_trailers 
                (title, video_id, view_count, like_count, comment_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                t["title"],
                t["video_id"],
                t["view_count"],
                t["like_count"],
                t["comment_count"],
            ))
            count_added += 1
        except Exception as e:
            print("Error saving YouTube trailer:", e)

    conn.commit()
    print("YouTube: Added", count_added, "trailers.")


# Main function
def main():
    init_db()
    conn = sqlite3.connect("movies.db")

    # Load TMDB JSON (Using master file)
    with open("movie_master.json", "r") as f:
        tmdb_movies = json.load(f)
    save_tmdb_movies_to_db(conn, tmdb_movies)

    # Load OMDB JSON (Using master file)
    with open("omdb_master.json", "r") as f:
        omdb_movies = json.load(f)
    save_omdb_movies_to_db(conn, omdb_movies)

    # Load YouTube JSON (Using master file)
    with open("youtube_trailers_master.json", "r") as f:
        youtube_trailers = json.load(f)
    save_youtube_trailers_to_db(conn, youtube_trailers)

    conn.close()


if __name__ == "__main__":
    main()

