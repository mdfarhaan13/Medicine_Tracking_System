import sqlite3

# Database file
DATABASE = 'database/pharmacy.db'

def create_db():
    # Connect to the database (or create it)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create pharmacists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pharmacists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    ''')

    # Create medicines table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        count INTEGER NOT NULL,
        expiry_date DATE NOT NULL
    );
    ''')

    # Create donation_requests table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donation_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        discount_percent INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT "Pending",
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Database and tables created successfully at {DATABASE}.")

# Run the database creation function
if __name__ == '__main__':
    create_db()
