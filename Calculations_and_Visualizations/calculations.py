import csv
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
        title = row[0]
        budget = row[1]
        rating_value = row[2]

        # IMDb ratings are stored as strings like "6.5" or "N/A"
        # If they cannot convert to float, skip them
        try:
            rating = float(rating_value)
        except:
            continue

        cleaned_rows.append((title, budget, rating))

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

    return {
        "highest_budget_movie": highest_budget_row, 
        "highest_rated_movie": highest_rating_row
    }


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
                genre_totals[genre] = genre_totals.get(genre, 0) + rating
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    avg_ratings = {genre: genre_totals[genre]/genre_counts[genre] for genre in genre_totals}

    # Print average rating for each genre
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

    # Visualization #2: pie chart of genre counts, how many movies per genre

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
        print("No trailer data found.")
        return 
    
    cleaned_rows = []
    for tmdb_id, movie_title, budget in movies: 
        movie_official = re.sub(r"[^\w\s]", "", movie_title.lower()).strip()
        matched_trailers = [
            t for t in trailers
            if movie_official in re.sub(r"[^\w\s]", "", t[0].lower()).strip()
        ]
        if matched_trailers: 
            total_views = sum(t[1] for t in matched_trailers)
            total_likes = sum(t[2] for t in matched_trailers)
            total_comments = sum(t[3] for t in matched_trailers)

            cleaned_rows.append((movie_title, budget, total_views, total_likes, total_comments))

    if not cleaned_rows: 
        print("No matching trailer data found.")
        return

    top_movie = max(cleaned_rows, key=lambda r:r[2])
    print("Movie with the most trailer views")
    print(f" Title: {top_movie[0]}")
    print(f" Budget: ${top_movie[1]}")
    print(f" Total Views: {top_movie[2]}")

    budgets = [r[1]/1_000_000 for r in cleaned_rows]
    views = [r[2] for r in cleaned_rows]
    titles = [r[0] for r in cleaned_rows]

    plt.figure(figsize=(12,6))
    plt.scatter(budgets, views, color='teal')
    plt.title("Youtube Trailer Views vs. Movie Budget")
    plt.xlabel("Movie Budget (Millions USD)")
    plt.ylabel("Total Trailer Views")

    top_n_labels = 5
    top_indices = sorted(range(len(views)), key=lambda i: views[i], reverse=True)[:top_n_labels]
    for i in top_indices: 
        plt.text(budgets[i], views[i], titles[i], fontsize=9)

    plt.show()

    result_list = []
    for r in cleaned_rows:
        result_list.append({
            "title": r[0],
            "budget": r[1],
            "total_views": r[2],
            "total_likes": r[3],
            "total_comments": r[4],
        })
    return result_list

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

    # Save all results to CSV
    save_results_to_csv(calc1_results, calc2_results, calc3_results)

    conn.close()
   
if __name__ == "__main__":
    main()


