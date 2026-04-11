import sqlite3

def initialize_db():
    with sqlite3.connect('nihongo_graph.db') as conn:
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

        # 3. Progress Table (User Tracking)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_id INTEGER UNIQUE,
            hit_rate REAL DEFAULT 0.0,
            last_review DATE,
            next_review DATE,
            FOREIGN KEY (concept_id) REFERENCES Concept(concept_id) ON DELETE CASCADE
        )
        ''')

        conn.commit()
        print("Database 'nihongo_graph.db' created successfully.")

if __name__ == '__main__':
    initialize_db()