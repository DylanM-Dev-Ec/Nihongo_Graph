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
    """
    Saves the concept and returns its unique database ID.
    Required for establishing graph relationships.
    """
    try:
        # Use your exact database filename: nihongo_graph.db
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Concept (kanji, hiragana, jlpt_level, meaning) 
                VALUES (?, ?, ?, ?)
            ''', (option['kanji'], option['reading'], option['jlpt'], option['meaning']))
            conn.commit()
            # This is the 'magic' line: returns the last inserted ID
            return cursor.lastrowid 
    except sqlite3.Error as e:
        print(f"  [Error] Database insertion failed: {e}")
        return None
def find_related_concepts(current_id, meaning_text):
    """
    Scans the database for concepts that share similar meanings.
    """
    try:
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            # We look for words with similar English meanings
            query = "SELECT id, kanji, meaning FROM Concept WHERE meaning LIKE ? AND id != ?"
            search_term = f"%{meaning_text}%"
            cursor.execute(query, (search_term, current_id))
            return cursor.fetchall()
    except sqlite3.Error:
        return []

def link_concepts(source, target, rel_type="context"):
    """
    Creates a new entry in the Relationships table.
    """
    try:
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Relationships (source_id, target_id, relation_type) VALUES (?, ?, ?)",
                           (source, target, rel_type))
            conn.commit()
            return True
    except sqlite3.Error:
        return False
# Main entry point for the CLI application
def main():
    print("--- NIHONGOGRAPH SMART ENTRY (DÍA 2) ---")
    while True:
        choice = input("\nSelecciona un número para guardar (o Enter para omitir): ")
        if choice.isdigit() and 0 < int(choice) <= len(results):
            selected = results[int(choice)-1]
            
            # Step 1: Save and get the ID
            new_concept_id = save_to_db(selected)
            
            if new_concept_id:
                print(f"  [ÉXITO] '{selected['kanji']}' guardado con éxito.")
                
                # Step 2: Intelligent linking
                rel_words = find_related_concepts(new_concept_id, selected['meaning'])
                
                if rel_words:
                    print("\n  [?] He detectado conexiones potenciales en tu grafo:")
                    for r_id, r_kanji, r_meaning in rel_words:
                        link_ask = input(f"      ¿Conectar con '{r_kanji}' ({r_meaning})? (s/n): ")
                        if link_ask.lower() == 's':
                            if link_concepts(new_concept_id, r_id):
                                print(f"      [LINK] Conexión establecida.")
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