import sqlite3
import os
from datetime import date

# Dynamically locate the database file based on the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'kioku_engine.db')

def seed_database():
    """Inserts test data to validate the SM-2 algorithm."""
    print("Seeding database with dummy concepts...")
    today = date.today()

    # Data format: (Kanji, Hiragana, Katakana, JLPT Level)
    dummy_concepts = [
        ("水", "みず", "ミズ", 5),
        ("火", "ひ", "ヒ", 5),
        ("木", "き", "キ", 5)
    ]

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        for kanji, hiragana, katakana, jlpt in dummy_concepts:
            # 1. Insert into Concept table
            cursor.execute('''
                INSERT INTO Concept (kanji, hiragana, katakana, jlpt_level)
                VALUES (?, ?, ?, ?)
            ''', (kanji, hiragana, katakana, jlpt))
            
            concept_id = cursor.lastrowid
            
            # 2. Insert initial SM-2 state into Progress table
            cursor.execute('''
                INSERT INTO Progress (concept_id, interval_days, repetitions, ease_factor, next_review)
                VALUES (?, 0, 0, 2.5, ?)
            ''', (concept_id, today))

        conn.commit()
        print("[OK] Test data successfully injected into Kioku Engine.")

if __name__ == '__main__':
    seed_database()