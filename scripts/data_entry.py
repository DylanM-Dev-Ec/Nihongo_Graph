import sqlite3
import os
import requests
import jaconv
from datetime import date, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'nihongo_graph.db')

def fetch_api_options(romaji_input):
    kana_query = jaconv.alphabet2kana(romaji_input)
    url = f"https://jisho.org/api/v1/search/words?keyword={kana_query}"
    try:
        response = requests.get(url)
        data = response.json()
        options = []
        for item in data.get('data', [])[:5]:
            japanese = item.get('japanese', [{}])[0]
            kanji = japanese.get('word', japanese.get('reading'))
            reading = japanese.get('reading', '')
            meaning = item.get('senses', [{}])[0].get('english_definitions', ['No meaning'])[0]
            options.append({'kanji': kanji, 'reading': reading, 'meaning': meaning})
        return options
    except:
        return []

def save_to_db(option):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        try:
            cursor.execute('''INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES (?, ?, ?)''', 
                           (option['kanji'], option['reading'], 5))
            concept_id = cursor.lastrowid
            # Init Progress for SRS
            today = date.today()
            cursor.execute('''INSERT INTO Progress (concept_id, last_review, next_review) VALUES (?, ?, ?)''',
                           (concept_id, today, today + timedelta(days=1)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("  [!] Concept already exists in your graph.")
            return False

def main():
    print("--- NIHONGOGRAPH SMART ENTRY (DAY 2) ---")
    while True:
        query = input("\nSearch word in Romaji (or 'q' to quit): ").strip()
        if query.lower() == 'q': break
        
        results = fetch_api_options(query)
        if not results:
            print("No results found.")
            continue
            
        for i, opt in enumerate(results):
            print(f"[{i+1}] {opt['kanji']} ({opt['reading']}) - {opt['meaning']}")
            
        choice = input("\nSelect number to save (or Enter to skip): ")
        if choice.isdigit() and 0 < int(choice) <= len(results):
            selected = results[int(choice)-1]
            if save_to_db(selected):
                print(f"  [SUCCESS] {selected['kanji']} added to your graph.")

if __name__ == '__main__':
    main()