import mysql.connector
from mysql.connector import Error

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        
    "password": "password", 
    "database": "2d_closet"
}

def get_db_connection():
    """Establishes and returns a connection to the database."""
    return mysql.connector.connect(**DB_CONFIG)

def initialize_data():
    """Seeds the database with a user, items, and an outfit if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print("Checking/Seeding initial data...")

        # 1. Ensure User exists
        cursor.execute("INSERT IGNORE INTO users (user_id, username, password) VALUES (1, 'hp_user', 'secure_pass')")

        # 2. Ensure Items exist
        items = [
            (101, 1, 'top', 'assets/clothes/red_hoodie.png'),
            (102, 1, 'pant', 'assets/clothes/denim_jeans.png'),
            (103, 1, 'dress', 'assets/clothes/summer_dress.png')
        ]
        cursor.executemany("INSERT IGNORE INTO items (item_id, user_id, category, image_path) VALUES (%s, %s, %s, %s)", items)

        # 3. Ensure an Outfit exists (Linking User 1 to Top 101 and Pant 102)
        cursor.execute("""
            INSERT IGNORE INTO outfits (outfit_id, user_id, top_id, bottom_id, outfit_name) 
            VALUES (1, 1, 101, 102, 'Casual Friday')
        """)

        conn.commit()
        print("Database ready and seeded.")

    except Error as e:
        print(f"Error during initialization: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def fetch_closet_data(user_id):
    """Fetches all outfits for a specific user and prints their details."""
    try:
        conn = get_db_connection()
        # Use dictionary=True so we can access columns by name like outfit['outfit_name']
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            o.outfit_name,
            i_top.image_path AS top_img,
            i_bottom.image_path AS bottom_img,
            i_dress.image_path AS dress_img
        FROM outfits o
        LEFT JOIN items i_top ON o.top_id = i_top.item_id
        LEFT JOIN items i_bottom ON o.bottom_id = i_bottom.item_id
        LEFT JOIN items i_dress ON o.dress_id = i_dress.item_id
        WHERE o.user_id = %s;
        """

        cursor.execute(query, (user_id,))
        results = cursor.fetchall()

        print(f"\n--- DISPLAYING OUTFITS FOR USER {user_id} ---")
        if not results:
            print("No outfits found in the database.")
        else:
            for outfit in results:
                print(f"Outfit Name: {outfit['outfit_name']}")
                if outfit['dress_img']:
                    print(f"  -> Wearing Dress: {outfit['dress_img']}")
                else:
                    print(f"  -> Top: {outfit['top_img']}")
                    print(f"  -> Bottom: {outfit['bottom_img']}")
                print("-" * 30)

    except Error as e:
        print(f"Error fetching data: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Step 1: Add the data
    initialize_data()
    
    # Step 2: Show the data
    fetch_closet_data(1)