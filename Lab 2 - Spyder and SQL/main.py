from import_data import *
from query import make_query
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Create our database
    create_db()

    ## Create ratings table
    # Write query to create the table from ratings
    # Create keys and specify data types for schema
    query = """
    CREATE TABLE IF NOT EXISTS ratings (
    movie_id TEXT PRIMARY KEY,
    avg_rating REAL,
    total_ratings INTEGER,
    median_rating REAL
    )
    """
    create_update_db_table(query)

    # DROP TABLE ratings to drop if needed
    # Now we will populate our table
    insert_from_csv(RATINGS_CSV)
    print("\n\n\n")

    ## Create movies table
    # Write query to create the table from movies
    # Create keys and specify data types for schema
    query = """
    CREATE TABLE IF NOT EXISTS movies (
    id TEXT PRIMARY KEY,
    title TEXT,
    year INTEGER,
    duration INTEGER,
    country TEXT,
    worldwide_gross_income INTEGER,
    production_company TEXT
    )
    """

    create_update_db_table(query)

    # Now we will populate our table
    insert_from_csv(MOVIES_CSV)
    print("\n\n\n")

    ## Now let's query the ratings table

    # First query, retrieve first 5 records (don't overload machine)
    query = """
    SELECT * 
    FROM ratings 
    LIMIT 5;
    """

    make_query(query)

    # Second query, filtering by WHERE and ordering by ORDER BY
    # Indicate direction with DESC (ASC defaults)
    query = """
    SELECT * 
    FROM ratings 
    WHERE median_rating > 9
    ORDER BY total_ratings DESC
    LIMIT 5;
    """

    make_query(query)

    # Third query, filtering and ordering, w/ sanitation
    query = """
    SELECT * 
    FROM ratings 
    WHERE median_rating > ?
    ORDER BY total_ratings DESC
    LIMIT 5;
    """
    param = (9,)

    make_query(query, param)

    # Fourth query, filtering and ordering multiple columns, w/ sanitation
    query = """
    SELECT * 
    FROM ratings 
    WHERE median_rating > ?
    ORDER BY median_rating DESC, avg_rating DESC, total_ratings DESC
    LIMIT 5;
    """

    param = (9,)

    make_query(query, param)

    # Fifth query, filtering and aggregation using AVG(), w/ sanitation
    query = """
    SELECT AVG(total_ratings) 
    FROM ratings 
    WHERE median_rating > ?;
    """

    param = (9,)

    make_query(query, param)

    # Sixth query, simple aggregation (COUNT DISTINCT)
    query = """
    SELECT COUNT(DISTINCT median_rating) 
    FROM ratings;
    """

    make_query(query)

    # Challengee: Seventh query, subquery to extract the average ratings
    # of movies with above the median number of total_ratings (total ratings)
    # First query: get the median index with n-1/2
    # Second query: get median index w/ offset, extract the 1 total_ratings number (median)
    # Third query: only retrieve values above that median total_ratings
    query = """
    SELECT avg_rating, total_ratings
    FROM ratings
    WHERE total_ratings > (
        SELECT total_ratings
        FROM ratings
        ORDER BY total_ratings
        LIMIT 1 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM ratings)
    )
    ORDER BY avg_rating DESC, total_ratings DESC
    LIMIT 5;
    """

    make_query(query)

    # Challenge: Eighth query, CTE w/ subquery
    # Define a table as a result set, with the median ratings
    # Then use that result set in your subquery to check
    query = """
    WITH medianRatings AS (
        SELECT total_ratings
        FROM ratings
        ORDER BY total_ratings
        LIMIT 1 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM ratings)
    )

    SELECT avg_rating, total_ratings
    FROM ratings
    WHERE total_ratings > (SELECT total_ratings FROM medianRatings)
    ORDER BY avg_rating DESC, total_ratings DESC
    LIMIT 5;
    """

    make_query(query)

    ## Now we'll shift to movies table
    # First query, easy
    query = """
    SELECT *
    FROM movies
    LIMIT 5;
    """

    make_query(query)

    # Fix the '' in each table, set to NULL
    query = """
    UPDATE movies
    SET worldwide_gross_income = NULL
    WHERE worldwide_gross_income = '';
    """
    create_update_db_table(query)
    
    query = """
    UPDATE movies
    SET production_company = NULL
    WHERE production_company = '';
    """
    create_update_db_table(query)

    # Second query, see the changes
    query = """
    SELECT *
    FROM movies
    LIMIT 5;
    """

    make_query(query)

    # Third query, work with NULL values
    # Don't use = in lookups, use IS or IS NOT NULL. Except for SET, although that is rare.
    query = """
    SELECT *
    FROM movies
    WHERE worldwide_gross_income AND production_company NOT NULL
    LIMIT 5;
    """

    make_query(query)

    # Fourth query, aggregation and filtering
    # GROUP BY to get the groups, HAVING to filter on groups (not WHERE, that is for individual records)
    # Note the alias with AS, we do this to define the column name, else it would be ROUND(AVG)...
    query = """
    SELECT production_company, country, COUNT(production_company), ROUND(AVG(worldwide_gross_income), 2) AS avg_income
    FROM movies
    GROUP BY production_company
    HAVING COUNT(production_company) > 5 AND worldwide_gross_income IS NOT NULL
    ORDER BY avg_income DESC
    LIMIT 5;
    """

    make_query(query)

    # Fifth query, joins
    # INNER JOIN here (default of JOIN). Bring together datasets on movie id
    # Notice use of alias for ease (else would need movies.id, ratings.avg_rating, etc)
    query = """
    SELECT m.id, m.title, r.avg_rating, r.total_ratings, m.worldwide_gross_income, m.production_company
    FROM movies AS m
    JOIN ratings AS r
    ON m.id = r.movie_id
    LIMIT 10;
    """

    make_query(query)

    # Sixth query, add character filters (like wildcard, get movie titles that start with W)
    query = """
    SELECT m.id, m.title, r.avg_rating, r.total_ratings, m.worldwide_gross_income, m.production_company
    FROM movies AS m
    JOIN ratings AS r
    ON m.id = r.movie_id
    WHERE m.title LIKE 'W%'
    LIMIT 10;
    """

    results = make_query(query) 

    # Why do we do this? Easy downstream analysis
    # Try to get a pandas df for analysis
    columns = ['id', 'title', 'avg_rating', 'total_ratings', 'ww_gross', 'prod_company']
    df = pd.DataFrame(data=results, columns=columns)
    print(df.head())

    # Create plot object (scatter)
    plt.figure(figsize=(10, 6))

    # Get total ratings v average rating
    plt.scatter(df['total_ratings'], df['avg_rating'], alpha=0.5, color='indigo')

    # Label axes, title
    plt.title('Average Rating vs. Total Ratings of Movies Starting w/ W', fontsize=15)
    plt.xlabel('Total Ratings', fontsize=12)
    plt.ylabel('Average Rating', fontsize=12)

    # Annotate points with movie titles
    for i in range(len(df)):
        plt.annotate(df['title'][i], (df['total_ratings'][i], df['avg_rating'][i]), fontsize=9, alpha=0.7)

    # Show the plot
    plt.show()


if __name__ == "__main__":
    main()