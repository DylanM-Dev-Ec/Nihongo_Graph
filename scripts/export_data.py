import sqlite3
import json
import os

def export_to_json():
    """
    Connects to the SQLite database, extracts concepts and connections,
    and formats them into a JSON file for pyvis rendering.
    """
    db_path = "data/nihongo_graph.db"

    if not os.path.exists(db_path):
        print(f"  [ERROR] No se encontró la base de datos en: {db_path}")
        return

    print(f"  [INFO] Extrayendo datos de {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Get Concepts (Nodes)
    # Extracting from the 'Concept' table
    cursor.execute("SELECT concept_id, kanji, hiragana, jlpt_level FROM Concept")
    nodes = []
    for row in cursor.fetchall():
        concept_id = row[0]
        kanji = row[1]
        hiragana = row[2]
        jlpt_level = row[3]
        
        # Display logic: Show Kanji if available, otherwise show Hiragana
        display_label = kanji if kanji else hiragana
        # Hover logic: Show Hiragana reading when hovering over the Kanji
        hover_title = hiragana if kanji else "Concepto"

        nodes.append({
            "id": concept_id,
            "label": display_label,
            "title": hover_title,
            "group": jlpt_level or 0
        })

    # 2. Get Connections (Edges)
    # Extracting from the 'Connection' table
    cursor.execute("SELECT source_id, target_id, relationship_type FROM Connection")
    edges = []
    for row in cursor.fetchall():
        edges.append({
            "from": row[0],
            "to": row[1],
            "label": row[2]
        })

    conn.close()

    # 3. Save to JSON (Ensure correct encoding for Japanese characters)
    graph_data = {"nodes": nodes, "edges": edges}
    with open("graph_data.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=4, ensure_ascii=False)
    
    print("  [ÉXITO] Archivo 'graph_data.json' creado correctamente.")

if __name__ == "__main__":
    export_to_json()