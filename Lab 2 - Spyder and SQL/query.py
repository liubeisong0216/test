import sqlite3

DB_NAME = 'imdb_lab.db'

def make_query(query, param=None):
    # Establish connection to db
    conn = sqlite3.connect(DB_NAME)

    # Read and execute query
    cursor = conn.cursor()

    # If passing as parameter (sanitization)
    if param:
        cursor.execute(query, param)
    else:
        # Standard
        cursor.execute(query)

    # Return result
    result = cursor.fetchall()
    
    if param:
        print("\n See query...\n")
        print(query, param)
    else:
        print("\n See query...\n")
        print(query)

    print("\n See query result...\n")
    print(result)

    return result