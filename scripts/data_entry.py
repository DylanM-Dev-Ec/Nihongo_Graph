import sqlite3
import os

# Dynamically locate the database file based on the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'nihongo_graph.db')

def initialize_db():
    """Initializes the database schema with strict foreign key constraints."""
    
    # Ensure the target directory exists before creating the file
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Critical: Enforce foreign key constraints in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Core Table (Nodes): Stores individual kanji or vocabulary words
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Concept (
                concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kanji TEXT NOT NULL,
                hiragana TEXT NOT NULL,
                katakana TEXT,
                jlpt_level INTEGER
            )
        ''')
        
        # Edge Table (Graph Links): Defines relationships between concepts
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
        
        # Spaced Repetition System (SRS) Table: Tracks user memory progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Progress (
                concept_id INTEGER UNIQUE,
                hit_rate REAL DEFAULT 0.0,
                last_review DATE,
                next_review DATE,
                FOREIGN KEY (concept_id) REFERENCES Concept(concept_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print("[OK] Database schema and constraints initialized successfully.")

if __name__ == '__main__':
    print("Starting database initialization...")
    initialize_db()