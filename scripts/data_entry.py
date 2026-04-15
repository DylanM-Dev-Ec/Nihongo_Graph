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
            
            # --- AQUÍ CALCULAMOS EL JLPT ---
            jlpt_list = item.get('jlpt', [])
            jlpt_num = int(jlpt_list[0].replace('jlpt-n', '')) if jlpt_list else 0
            
            # --- AQUÍ VA TU LÍNEA (Reemplaza a la vieja) ---
            options.append({'kanji': kanji, 'reading': reading, 'meaning': meaning, 'jlpt': jlpt_num})
            
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

# Main entry point for the CLI application
def main():
    print("--- NIHONGOGRAPH SMART ENTRY (DÍA 2) ---")
    while True:
        # Prompt user for Romaji input
        query = input("\nBusca una palabra en Romaji (o 'q' para salir): ").strip()
        if query.lower() == 'q': 
            break
        
        # Fetch data from Jisho API using the provided query
        results = fetch_api_options(query)
        
        # Handle empty responses from the API
        if not results:
            print("  [!] No se encontraron resultados. Intenta otra lectura.")
            continue
            
        # Iterate through the API results and display them to the user
        for i, opt in enumerate(results):
            # Format JLPT level for display. Example: 'N5' or 'Sin nivel'
            jlpt_display = f"N{opt['jlpt']}" if opt['jlpt'] > 0 else "Sin nivel"
            print(f"[{i+1}] {opt['kanji']} ({opt['reading']}) - {opt['meaning']} | JLPT: {jlpt_display}")
            
        # Handle user selection and execute database insertion
        choice = input("\nSelecciona un número para guardar (o presiona Enter para saltar): ")
        if choice.isdigit() and 0 < int(choice) <= len(results):
            selected = results[int(choice)-1]
            if save_to_db(selected):
                print(f"  [ÉXITO] '{selected['kanji']}' agregado a tu grafo de conocimiento.")

if __name__ == '__main__':
    main()