import sqlite3
from datetime import date, timedelta

def insert_test_data():
    # Connect to the database
    with sqlite3.connect('nihongo_graph.db') as conn:
        cursor = conn.cursor()
        
        # MANDATORY: Enable foreign key constraints in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        print("Inserting concept nodes...")
        # 1. Insert Kanjis into the 'Concept' table
        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('人', 'ひと', 5)")
        person_id = cursor.lastrowid 

        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('木', 'き', 5)")
        tree_id = cursor.lastrowid 

        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('休', 'やす', 5)")
        rest_id = cursor.lastrowid 

        print("Creating neural connections (edges)...")
        # 2. Insert relationships into the 'Connection' table
        # Person -> Rest
        cursor.execute('''
            INSERT INTO Connection (source_id, target_id, relationship_type) 
            VALUES (?, ?, 'component')
        ''', (person_id, rest_id))

        # Tree -> Rest
        cursor.execute('''
            INSERT INTO Connection (source_id, target_id, relationship_type) 
            VALUES (?, ?, 'component')
        ''', (tree_id, rest_id))

        print("Logging study progress...")
        # 3. Insert a review state in 'Progress' for the combined concept
        today = date.today()
        tomorrow = today + timedelta(days=1)
        cursor.execute('''
            INSERT INTO Progress (concept_id, hit_rate, last_review, next_review) 
            VALUES (?, 0.0, ?, ?)
        ''', (rest_id, today, tomorrow))

        conn.commit()

        # --- VALIDATION PHASE ---
        print("\n--- DATABASE TEST SUCCESSFUL ---")
        print("Graph Traversal Output:")
        cursor.execute('''
            SELECT c1.kanji, c2.kanji, con.relationship_type 
            FROM Connection con
            JOIN Concept c1 ON con.source_id = c1.concept_id
            JOIN Concept c2 ON con.target_id = c2.concept_id
        ''')
        
        for row in cursor.fetchall():
            print(f"[{row[0]}] is a {row[2]} of [{row[1]}]")

if __name__ == '__main__':
    try:
        insert_test_data()
    except sqlite3.IntegrityError as e:
        print(f"\nENGINEERING ERROR: Foreign key or constraint violation. Details: {e}")