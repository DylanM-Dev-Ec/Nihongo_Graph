import sqlite3
import os

# Dynamically locate the database file to ensure it goes to the 'data' folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'kioku_engine.db')

def initialize_db():
    # Ensure 'data' directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Connect using the absolute path
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Enforce foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. Concept Table (Nodes)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Concept (
            concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kanji TEXT,
            hiragana TEXT,
            katakana TEXT,
            jlpt_level INTEGER
        )
        ''')

        # 2. Connection Table (Edges/Relationships)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Connection (
            source_id INTEGER,
            target_id INTEGER,
            relationship_type TEXT,
            PRIMARY KEY (source_id, target_id),
            FOREIGN KEY (source_id) REFERENCES Concept(concept_id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES Concept(concept_id) ON DELETE CASCADE
        )
        ''')

        # 3. Progress Table (User Tracking - SM-2 Refactored)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_id INTEGER UNIQUE,
            interval_days INTEGER DEFAULT 0,
            repetitions INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            last_review DATE,
            next_review DATE,
            FOREIGN KEY (concept_id) REFERENCES Concept(concept_id) ON DELETE CASCADE
        )
        ''')

        conn.commit()
        print(f"[OK] Database created successfully at: {DB_PATH}")

if __name__ == '__main__':
    initialize_db()