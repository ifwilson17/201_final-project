import sqlite3
import matplotlib.pyplot as plt
import re

# Find the movie with the highest budget AND the movie with the highest IMDb rating. 
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

    # If the join returned nothing, we can't calculate anything
    if not rows:
        print("Not enough data to calculate.")
        return

    # We will save cleaned rows here after converting rating from string to float
    cleaned_rows = []

    # Loop through each row from the JOIN
    for row in rows:
        title_id = row[0]
        budget = row[1]
        rating_value = row[2]

        # IMDb ratings are stored as strings like "6.5" or "N/A"
        # If they cannot convert to float, skip them
        try:
            rating = float(rating_value)
        except:
            continue

        cleaned_rows.append((title_id, budget, rating))

    # If every rating was invalid, we cannot continue
    if not cleaned_rows:
        print("No valid rating data found.")
        return

    # Find the row with the highest budget 
    highest_budget_row = max(cleaned_rows, key=lambda r: r[1])

    # Find the row with the highest rating 
    highest_rating_row = max(cleaned_rows, key=lambda r: r[2])

    # Print results
    print("Highest Budget Movie:")
    print(f"  Title ID: {highest_budget_row[0]}")
    print(f"  Budget: ${highest_budget_row[1]}")

    print("Highest Rated Movie:")
    print(f"  Title ID: {highest_rating_row[0]}")
    print(f"  IMDb Rating: {highest_rating_row[2]}")

    # Visualization 1: scatterplot for budget and imdb rating
    budgets = []
    ratings = []

    for row in cleaned_rows:
        budgets.append(row[1])   
        ratings.append(row[2])   

    # Now draw the scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(budgets, ratings)

    plt.title("Budget vs IMDb Rating")
    plt.xlabel("Budget (USD)")
    plt.ylabel("IMDb Rating")
    plt.show()

    # Visualization 2: histogram showing budget distribution
    budgets = []
    for movie in cleaned_rows:
        budgets.append(movie[1])  

    # Step 2: Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(budgets, bins=10, color='green', edgecolor='black')
    plt.xlabel("Budget")
    plt.ylabel("Number of Movies")
    plt.title("Budget Distribution of Movies")
    plt.show()


# Calculate the average IMDb rating for each movie genre.
def calculation_2_avg_rating_by_genre(conn):
    print("Calculation #2: Average IMDb Rating by Genre")

    cur = conn.cursor()

    # Get all genres + ratings from OMDB table
    cur.execute("""
        SELECT omdb_movies.genre, omdb_movies.imdb_rating
        FROM omdb_movies;
    """)

    rows = cur.fetchall()

    # If no OMDB data exists, stop early
    if not rows:
        print("No OMDB data found.")
        return

    # genre_totals stores the SUM of ratings for each genre
    genre_totals = {}

    # genre_counts stores how many movies belong to each genre
    genre_counts = {}

    # Loop through all OMDB rows
    for row in rows:
        genre_string = row[0]
        rating_value = row[1]

        # Skip rows missing either genre or rating
        if not genre_string or not rating_value:
            continue

        # Convert rating to float
        # Skip invalid values like "N/A"
        try:
            rating = float(rating_value)
        except:
            continue

        # A movie can have multiple genres, separated by commas
        genres = [g.strip() for g in genre_string.split(",")]

        # Add rating to each genre individually
        for genre in genres:
            if genre not in genre_totals:
                genre_totals[genre] = 0.0
                genre_counts[genre] = 0

            genre_totals[genre] += rating
            genre_counts[genre] += 1

    # Print average rating for each genre
    print("Average IMDb Rating by Genre:")
    for genre in genre_totals:
        avg = genre_totals[genre] / genre_counts[genre]
        print(f"  {genre}: {avg:.2f}")
    
    # Visualization #1: bar chart for average imdb rating by genre 
    genres_list = []
    averages_list = []

    for genre in genre_totals:
        avg = genre_totals[genre] / genre_counts[genre]
        genres_list.append(genre)
        averages_list.append(avg)

    plt.figure(figsize=(12, 6))
    plt.bar(genres_list, averages_list)
    plt.title("Average IMDb Rating by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Average Rating")
    plt.xticks(rotation=45)
    plt.show()

    # Visualization #2: pie chart of genre counts, how many movies per genre
    genre_names = []
    genre_sizes = []

    for genre in genre_counts:
        genre_names.append(genre)
        genre_sizes.append(genre_counts[genre])

    plt.figure(figsize=(10, 8))
    plt.pie(genre_sizes, labels=genre_names, autopct="%1.1f%%")
    plt.title("Genre Distribution in OMDb Movies")
    plt.show()

def compare_trailer_popularity_to_budget():
    conn = sqlite3.connect("movies.db")
    cur = conn.cursor()

    cur.execute("SELECT tmdb_id, title, budget FROM tmdb_movies")
    movies = cur.fetchall()

    cur.execute("SELECT title, view_count, like_count, comment_count FROM youtube_trailers")
    trailers = cur.fetchall()

    results = []

    for tmdb_id, movie_title, budget in movies: 
        movie_official = re.sub(r"[^\w\s]", "", movie_title.lower()).strip()
        matched = [
            t for t in trailers
            if movie_official in re.sub(r"[^\w\s]", "", t[0].lower()).strip()
        ]
        if matched: 
            total_views = sum(t[1] for t in matched)
            total_likes = sum(t[2] for t in matched)
            total_comments = sum(t[3] for t in matched)

            results.append ({
                "movie_title": movie_title, 
                "budget": budget,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
            })

    conn.close()
    return results

def plot_trailer_vs_budget(data, top_n_labels=5): 
    budgets = [d['budget']/1_000_000 for d in data]
    views = [d['total_views'] for d in data]
    titles = [d['movie_title'] for d in data]

    plt.figure(figsize=(12,6))
    plt.scatter(budgets, views, color='teal', alpha=0.7, edgecolors='k')
    plt.title("Youtube Trailer Views vs. Movie Budget")
    plt.xlabel("Movie Budget (Millions USD)")
    plt.ylabel("Total Trailer Views")
    plt.grid(True, linestyle='--', alpha=0.5)

    top_indices = sorted(range(len(views)), key=lambda i: views[i], reverse=True)[:top_n_labels]
    for i in top_indices: 
        plt.text(budgets[i], views[i], titles[i], fontsize=9, ha='right', va='bottom')

    plt.show()


def main():
    conn = sqlite3.connect("movies.db")

    calculation_1_budget_vs_rating(conn)
    calculation_2_avg_rating_by_genre(conn)

    data = compare_trailer_popularity_to_budget()
    plot_trailer_vs_budget(data)

    conn.close()


if __name__ == "__main__":
    main()
