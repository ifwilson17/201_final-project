import csv
import sqlite3
import matplotlib.pyplot as plt
import re

def calculation_1_budget_vs_rating(conn):
    print("Calculation #1: Highest Budget and Highest IMDb Rating")

    cur = conn.cursor()

    # Join TMDB and OMDB tables together using imdb_id
    cur.execute("""
        SELECT tmdb_movies.title, tmdb_movies.budget, omdb_movies.imdb_rating
        FROM tmdb_movies
        JOIN omdb_movies
        ON tmdb_movies.imdb_id = omdb_movies.imdb_id;
    """)

    rows = cur.fetchall()

    if not rows:
        print("Not enough data to calculate.")
        return

    cleaned_rows = []

    for row in rows:
        title = row[0]
        budget = row[1]
        rating_value = row[2]

        try:
            rating = float(rating_value)
        except:
            continue

        cleaned_rows.append((title, budget, rating))

    if not cleaned_rows:
        print("No valid rating data found.")
        return

    highest_budget_row = max(cleaned_rows, key=lambda r: r[1])
    highest_rating_row = max(cleaned_rows, key=lambda r: r[2])

    print("Highest Budget Movie:")
    print(f"  Title: {highest_budget_row[0]}")
    print(f"  Budget: ${highest_budget_row[1]}")

    print("Highest Rated Movie:")
    print(f"  Title: {highest_rating_row[0]}")
    print(f"  IMDb Rating: {highest_rating_row[2]}")

    # Visualization 1: scatterplot for budget and imdb rating
    budgets = [r[1] for r in cleaned_rows]
    ratings = [r[2] for r in cleaned_rows]

    plt.figure(figsize=(8, 6))
    plt.scatter(budgets, ratings)
    plt.title("Budget vs IMDb Rating")
    plt.xlabel("Budget (USD)")
    plt.ylabel("IMDb Rating")
    plt.show()

    # Visualization 2: histogram showing budget distribution
    plt.figure(figsize=(10, 6))
    plt.hist(budgets, bins=10, color='green', edgecolor='black')
    plt.xlabel("Budget")
    plt.ylabel("Number of Movies")
    plt.title("Budget Distribution of Movies")
    plt.show()

    return {
        "highest_budget_movie": highest_budget_row,
        "highest_rated_movie": highest_rating_row
    }


def calculation_2_avg_rating_by_genre(conn):
    print("Calculation #2: Average IMDb Rating by Genre")
    cur = conn.cursor()
    cur.execute("""
        SELECT genres.name, omdb_movies.imdb_rating
        FROM omdb_movies
        JOIN genres ON omdb_movies.genre_id = genres.genre_id;
    """)

    rows = cur.fetchall()
    if not rows:
        print("No OMDB data found.")
        return

    genre_totals = {}
    genre_counts = {}

    for genre_name, rating_value in rows:
        if not genre_name or not rating_value:
            continue

        try:
            rating = float(rating_value)
        except:
            continue

        if genre_name not in genre_totals:
            genre_totals[genre_name] = 0
            genre_counts[genre_name] = 0

        genre_totals[genre_name] += rating
        genre_counts[genre_name] += 1

    avg_ratings = {g: genre_totals[g] / genre_counts[g] for g in genre_totals}

    print("Average IMDb Rating by Genre:")
    for genre, avg in avg_ratings.items():
        print(f"  {genre}: {avg:.2f}")

    # Visualization #1: bar chart for average imdb rating by genre 
    plt.figure(figsize=(12, 6))
    plt.bar(avg_ratings.keys(), avg_ratings.values())
    plt.title("Average IMDb Rating by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Average Rating")
    plt.xticks(rotation=45)
    plt.show()

    # Visualization #2: pie chart of genre counts
    plt.figure(figsize=(10, 8))
    plt.pie(genre_counts.values(), labels=genre_counts.keys(), autopct="%1.1f%%")
    plt.title("Genre Distribution in OMDb Movies")
    plt.show()

    return avg_ratings


def calculation_3_compare_trailer_popularity_to_budget(conn):
    print("Calculation #3: Comparing Movie Trailer Popularity to Budget")
    cur = conn.cursor()

    cur.execute("SELECT tmdb_id, title, budget FROM tmdb_movies")
    movies = cur.fetchall()

    cur.execute("SELECT title, view_count, like_count, comment_count FROM youtube_trailers")
    trailers = cur.fetchall()

    if not movies or not trailers:
        print("Not enough data found.")
        return

    cleaned_rows = []

    for tmdb_id, movie_title, budget in movies:
        movie_clean = re.sub(r"[^\w\s]", "", movie_title.lower()).strip()

        matched = [
            t for t in trailers
            if movie_clean in re.sub(r"[^\w\s]", "", t[0].lower()).strip()
        ]

        if matched:
            total_views = sum(t[1] for t in matched)
            total_likes = sum(t[2] for t in matched)
            total_comments = sum(t[3] for t in matched)

            cleaned_rows.append((movie_title, budget, total_views, total_likes, total_comments))

    if not cleaned_rows:
        print("No matching trailer data found.")
        return

    top_movie = max(cleaned_rows, key=lambda r: r[2])

    print("Movie with the Most Trailer Views:")
    print(f" Title: {top_movie[0]}")
    print(f" Budget: ${top_movie[1]}")
    print(f" Total Views: {top_movie[2]}")

    budgets = [r[1] / 1_000_000 for r in cleaned_rows]  # millions
    views = [r[2] for r in cleaned_rows]
    titles = [r[0] for r in cleaned_rows]

    # Visualization: scatter plot
    plt.figure(figsize=(12, 6))
    plt.scatter(budgets, views, color='teal')
    plt.title("YouTube Trailer Views vs Movie Budget")
    plt.xlabel("Movie Budget (Millions USD)")
    plt.ylabel("Total Trailer Views")

    top_indices = sorted(range(len(views)), key=lambda i: views[i], reverse=True)[:5]

    for i in top_indices:
        plt.text(budgets[i], views[i], titles[i], fontsize=9)

    plt.show()

    return [
        {
            "title": r[0],
            "budget": r[1],
            "total_views": r[2],
            "total_likes": r[3],
            "total_comments": r[4]
        }
        for r in cleaned_rows
    ]


def save_results_to_csv(calc1_results, calc2_results, calc3_results, filename="movie_results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Calculation 1
        writer.writerow(["Calculation 1: Highest Budget and IMDb Rating"])
        if calc1_results:
            hb = calc1_results["highest_budget_movie"]
            hr = calc1_results["highest_rated_movie"]
            writer.writerow(["Category", "Title", "Budget"])
            writer.writerow(["Highest Budget Movie", hb[0], hb[1]])
            writer.writerow(["Category", "Title", "Rating"])
            writer.writerow(["Highest Rated Movie", hr[0], hr[2]])
        writer.writerow([])

        # Calculation 2
        writer.writerow(["Calculation 2: Average IMDb Rating by Genre"])
        writer.writerow(["Genre", "IMDb Rating"])
        if calc2_results:
            for genre, avg in calc2_results.items():
                writer.writerow([genre, avg])
        writer.writerow([])

        # Calculation 3
        writer.writerow(["Calculation 3: Movie Trailer Popularity vs Budget"])
        writer.writerow(["Title", "Budget", "Total_Views", "Total_Likes", "Total_Comments"])
        if calc3_results:
            for movie in calc3_results:
                writer.writerow([
                    movie["title"],
                    movie["budget"],
                    movie["total_views"],
                    movie["total_likes"],
                    movie["total_comments"]
                ])

def main():
    conn = sqlite3.connect("movies.db")

    calc1_results = calculation_1_budget_vs_rating(conn)
    calc2_results = calculation_2_avg_rating_by_genre(conn)
    calc3_results = calculation_3_compare_trailer_popularity_to_budget(conn)

    save_results_to_csv(calc1_results, calc2_results, calc3_results)

    conn.close()


if __name__ == "__main__":
    main()



