# Import libraries
import sqlite3
import csv

DB_NAME = 'imdb_lab.db'
RATINGS_CSV = 'ratings.csv'
MOVIES_CSV = 'movies.csv'

# Create our database
def create_db():
    # Create the connection
    conn = sqlite3.connect(DB_NAME)
    print(f"Created db: {conn}")

    # Close our connection when done
    conn.close()

# Function to create the table with movie data
def create_update_db_table(query):
    # Create connection to database
    conn = sqlite3.connect(DB_NAME)

    # Create the cursor to iterate through query
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)

    # Commit changes and close the connection -> write
    conn.commit()
    conn.close()

def insert_from_csv(file_name):
    # Read csv file
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        # Use DictReader to read CSV as a list of dictionaries
        reader = csv.DictReader(file)

        print("Read csv, printing field names...")
        print(reader.fieldnames)

        # Use list comprehension to extract tuples
        if file_name == "ratings.csv":
            to_db = [(i['movie_id'], i['avg_rating'], i['total_ratings'], i['median_rating']) for i in reader]
        elif file_name == "movies.csv":
            to_db = [(i['id'], i['title'], i['year'], i['duration'], i['country'], i['worldwide_gross_income'], i['production_company']) for i in reader]
        else:
            raise ValueError("Put in a correct file.")


    # Connect to db, get cursor
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Execute many insertions at once, use ? as a placeholder to insert variables (our data) in each row safely (sanitization)
    if file_name == "ratings.csv":
        cursor.executemany("INSERT OR IGNORE INTO ratings (movie_id, avg_rating, total_ratings, median_rating) VALUES (?, ?, ?, ?);", to_db)
    elif file_name == "movies.csv":
        cursor.executemany("INSERT OR IGNORE INTO movies (id, title, year, duration, country, worldwide_gross_income, production_company) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)
    else:
        raise ValueError("Please put in correct file.")
    
    conn.commit()
    conn.close()
    print("\n")
    print(f"See first 5: {to_db[0:5]}")
        