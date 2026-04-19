import sqlite3
import os
import requests
import jaconv
import json
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
def display_dashboard():
    """
    Shows a quick summary of the current state of the Knowledge Graph.
    Boosts motivation by showing real progress.
    """
    try:
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            
            # Count total words (Nodes)
            cursor.execute("SELECT COUNT(*) FROM Concept")
            total_concepts = cursor.fetchone()[0]
            
            # Count total links (Edges)
            cursor.execute("SELECT COUNT(*) FROM Relationships")
            total_links = cursor.fetchone()[0]
            
            # Count words by JLPT level
            cursor.execute("SELECT jlpt_level, COUNT(*) FROM Concept GROUP BY jlpt_level")
            levels = cursor.fetchall()

            print("\n" + "="*40)
            print("   📊 NIHONGOGRAPH PROGRESS REPORT")
            print("="*40)
            print(f"  • Concepts Learned: {total_concepts}")
            print(f"  • Graph Connections: {total_links}")
            print("-" * 40)
            for lv, count in levels:
                lv_label = f"N{lv}" if lv > 0 else "Unranked"
                print(f"  • {lv_label}: {count} words")
            print("="*40 + "\n")
            
    except sqlite3.Error as e:
        print(f"  [LOG] Could not load dashboard: {e}")
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
    
def create_edge(source_id, target_id, relation="context"):
    """
    Creates a link between concepts only if it doesn't exist yet.
    Ensures graph data integrity.
    """
    try:
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            
            # 1. Check if the connection already exists in either direction
            check_query = """
                SELECT id FROM Relationships 
                WHERE (source_id = ? AND target_id = ?) 
                OR (source_id = ? AND target_id = ?)
            """
            cursor.execute(check_query, (source_id, target_id, target_id, source_id))
            
            if cursor.fetchone():
                print("  [INFO] Esta conexión ya existe en el grafo. Omitiendo...")
                return False
            
            # 2. If it's new, insert it
            cursor.execute("INSERT INTO Relationships (source_id, target_id, relation_type) VALUES (?, ?, ?)", 
                           (source_id, target_id, relation))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"  [LOG] Error al crear la conexión: {e}")
        return False

def export_graph_to_json(filename="graph_data.json"):
    """
    Exports the entire graph (nodes and edges) to a JSON file.
    This is the first step toward a visual interface.
    """
    try:
        with sqlite3.connect('nihongo_graph.db') as conn:
            cursor = conn.cursor()
            
            # Extract Nodes (Concepts)
            cursor.execute("SELECT id, kanji, meaning, jlpt_level FROM Concept")
            nodes = [{"id": r[0], "label": r[1], "title": r[2], "group": r[3]} for r in cursor.fetchall()]
            
            # Extract Edges (Relationships)
            cursor.execute("SELECT source_id, target_id, relation_type FROM Relationships")
            edges = [{"from": r[0], "to": r[1], "label": r[2]} for r in cursor.fetchall()]
            
            graph_data = {"nodes": nodes, "edges": edges}
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n  [SUCCESS] Grafo exportado a {filename}")
    except Exception as e:
        print(f"  [ERROR] La exportación falló: {e}")

if __name__ == '__main__':
    main()