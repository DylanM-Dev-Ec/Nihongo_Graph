import sqlite3
import os
import jaconv
from datetime import date, timedelta

# Dynamically locate the database file based on the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'nihongo_graph.db')

def add_concept(cursor):
    print("\n" + "="*40)
    print("           ADD NEW CONCEPT")
    print("="*40)
    
    kanji = input("Kanji (or Word): ").strip()
    
    # Auto-convert Romaji to Hiragana using jaconv
    romaji_hiragana = input("Hiragana reading (type in romaji): ").strip()
    hiragana = jaconv.alphabet2kana(romaji_hiragana)
    print(f"  -> Converted to: {hiragana}")
    
    # Auto-convert Romaji to Katakana using jaconv
    romaji_katakana = input("Katakana reading (type in romaji, or Enter to skip): ").strip()
    katakana = ""
    if romaji_katakana:
        katakana = jaconv.alphabet2kana(romaji_katakana)
        print(f"  -> Converted to: {katakana}")
    
    try:
        jlpt = int(input("JLPT Level (e.g., 5): ").strip())
    except ValueError:
        jlpt = 5 # Default to N5

    cursor.execute('''
        INSERT INTO Concept (kanji, hiragana, katakana, jlpt_level)
        VALUES (?, ?, ?, ?)
    ''', (kanji, hiragana, katakana, jlpt))
    
    concept_id = cursor.lastrowid
    return concept_id, kanji

def add_components(cursor, target_id, target_kanji):
    print(f"\n--- Link components to [{target_kanji}] ---")
    print("(Enter the component Kanji. Press Enter with a blank line to finish)")
    
    while True:
        source_kanji = input("> Component: ").strip()
        if not source_kanji:
            break
            
        cursor.execute("SELECT concept_id FROM Concept WHERE kanji = ?", (source_kanji,))
        result = cursor.fetchone()
        
        if result:
            source_id = result[0]
            try:
                cursor.execute('''
                    INSERT INTO Connection (source_id, target_id, relationship_type)
                    VALUES (?, ?, 'component')
                ''', (source_id, target_id))
                print(f"  [SUCCESS] Linked: {source_kanji} -> {target_kanji}")
            except sqlite3.IntegrityError:
                print(f"  [WARNING] Link between {source_kanji} and {target_kanji} already exists.")
        else:
            print(f"  [ERROR] Kanji '{source_kanji}' not found. Please add it to the DB first.")

def init_progress(cursor, concept_id):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    cursor.execute('''
        INSERT INTO Progress (concept_id, hit_rate, last_review, next_review)
        VALUES (?, 0.0, ?, ?)
    ''', (concept_id, today, tomorrow))

def main():
    print("Starting NihongoGraph Data Entry Pipeline...")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        while True:
            concept_id, kanji = add_concept(cursor)
            add_components(cursor, concept_id, kanji)
            init_progress(cursor, concept_id)
            
            conn.commit()
            print(f"\n[OK] Concept '{kanji}' fully saved to database.")
            
            cont = input("\nAdd another concept? (y/n): ").strip().lower()
            if cont != 'y':
                print("Exiting pipeline. See you next time!")
                break

if __name__ == '__main__':
    main()