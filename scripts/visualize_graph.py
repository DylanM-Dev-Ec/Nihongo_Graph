import json
import os
from pyvis.network import Network

def generate_interactive_graph(json_file="graph_data.json", output_file="nihongo_graph.html"):
    """
    Reads the Knowledge Graph JSON and generates an interactive HTML file.
    Uses pyvis to render a force-directed graph.
    """
    print("  [INFO] Iniciando el motor de visualización...")
    
    # 1. Configure the canvas (Dark background, light text)
    net = Network(height="800px", width="100%", bgcolor="#1a1a1a", font_color="white", directed=True)
    
    # 2. Load the data from the JSON file
    if not os.path.exists(json_file):
        print(f"  [ERROR] No se encontró {json_file}. Asegúrate de exportar desde data_entry.py primero.")
        return

    with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)

    # 3. Draw Nodes (Concepts)
    # Color nodes based on their JLPT level to visualize learning progress
    colors = {
        5: "#ff9999", # N5 (Red/Pink)
        4: "#ffcc99", # N4 (Orange)
        3: "#ffff99", # N3 (Yellow)
        2: "#99ff99", # N2 (Green)
        1: "#99ccff", # N1 (Blue)
        0: "#cccccc"  # Unranked (Gray)
    }

    for node in data.get("nodes", []):
        level = node.get("group", 0)
        node_color = colors.get(level, "#cccccc")
        
        net.add_node(
            node["id"],
            label=node["label"],       # The Kanji or word (always visible)
            title=node["title"],       # The meaning (visible on hover)
            color=node_color,
            size=25                    # Base node size
        )

    # 4. Draw Edges (Relationships)
    for edge in data.get("edges", []):
        net.add_edge(
            edge["from"], 
            edge["to"], 
            title=edge.get("label", ""), # Relationship type on hover
            color="#666666"              # Edge color
        )

    # 5. Apply Physics (Barnes-Hut algorithm for node repulsion)
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150)
    
    # OPTIONAL: Uncomment the following line to show physics control buttons in the HTML
    # net.show_buttons(filter_=['physics'])

    # 6. Generate the HTML file
    net.save_graph(output_file)
    print(f"  [ÉXITO] ¡Grafo renderizado! Abre '{output_file}' en tu navegador web.")

if __name__ == "__main__":
    generate_interactive_graph()