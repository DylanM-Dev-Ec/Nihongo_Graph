import sqlite3

def seed_database():
    print("  [INFO] Inyectando datos de prueba...")
    conn = sqlite3.connect('data/nihongo_graph.db')
    cursor = conn.cursor()

    try:
        # 1. Insertar 3 Conceptos de prueba (Nivel N5)
        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('水', 'みず', 5)") # Agua
        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('飲む', 'のむ', 5)") # Beber
        cursor.execute("INSERT INTO Concept (kanji, hiragana, jlpt_level) VALUES ('お茶', 'おちゃ', 5)") # Té
        
        # 2. Conectar los conceptos (El Agua y el Té se beben)
        cursor.execute("INSERT INTO Connection (source_id, target_id, relationship_type) VALUES (1, 2, 'verbo_asociado')")
        cursor.execute("INSERT INTO Connection (source_id, target_id, relationship_type) VALUES (3, 2, 'verbo_asociado')")
        
        conn.commit()
        print("  [ÉXITO] Kanjis insertados correctamente en la base de datos.")
    except sqlite3.IntegrityError:
        print("  [AVISO] Los datos de prueba ya estaban insertados.")
    finally:
        conn.close()

if __name__ == '__main__':
    seed_database()