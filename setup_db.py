import sqlite3

def create_schema():
    # Fix 1: La ruta debe coincidir con el nombre exacto que veo en tu VS Code
    db_path = 'nihongo_graph.db' 
    
    # Fix 2: Inicializamos la conexión en None para evitar el UnboundLocalError
    connection = None
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            target_id INTEGER,
            relation_type TEXT,
            strength REAL DEFAULT 1.0,
            FOREIGN KEY (source_id) REFERENCES Concept(id),
            FOREIGN KEY (target_id) REFERENCES Concept(id)
        );
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        
        print("--- [SUCCESS] ---")
        print(f"Tabla 'Relationships' creada correctamente en: {db_path}")
        
    except sqlite3.Error as e:
        print(f"--- [ERROR DE SQLITE] ---")
        print(f"No se pudo abrir o modificar la base de datos: {e}")
        
    finally:
        # Ahora el 'if connection' no dará error porque la variable existe
        if connection:
            connection.close()

if __name__ == "__main__":
    create_schema()