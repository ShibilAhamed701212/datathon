import networkx as nx
from typing import Dict, List, Optional

def build_crime_graph(limit: int = 10) -> Dict:
    from . import database
    firs = database.query_firs(limit=limit)

    G = nx.Graph()
    nodes = {}
    edges = []

    for fir in firs[:limit]:
        fir_node_id = f"fir_{fir['fir_id']}"
        G.add_node(fir_node_id, label=f"FIR {fir['fir_id']}: {fir['crime_type']}", type="fir", fir_id=fir['fir_id'])
        nodes[fir_node_id] = {"label": f"FIR {fir['fir_id']}: {fir['crime_type']}", "type": "fir", "fir_id": fir['fir_id']}

        involvements = database.query_involvements(fir_id=fir['fir_id'])
        for inv in involvements:
            person_node_id = f"person_{inv['person_id']}"
            if person_node_id not in nodes:
                G.add_node(person_node_id, label=inv['person_name'], type="person", role=inv['role'])
                nodes[person_node_id] = {"label": inv['person_name'], "type": "person", "role": inv['role']}

            edge_key = f"{person_node_id}-{fir_node_id}"
            G.add_edge(person_node_id, fir_node_id, role=inv['role'])
            edges.append({"source": person_node_id, "target": fir_node_id, "role": inv['role']})

    return {
        "nodes": [{"id": nid, **attrs} for nid, attrs in nodes.items()],
        "edges": edges
    }

def build_person_network(person_name: Optional[str] = None) -> Dict:
    from . import database
    persons = database.query_persons(name=person_name) if person_name else database.query_persons()

    G = nx.Graph()
    nodes = {}
    edges = []

    for person in persons[:20]:
        p_id = f"person_{person['person_id']}"
        G.add_node(p_id, label=person['name'], type="person", role=person['role'])
        nodes[p_id] = {"label": person['name'], "type": "person", "role": person['role']}

        involvements = database.query_involvements(person_id=person['person_id'])
        for inv in involvements[:5]:
            fir_id = f"fir_{inv['fir_id']}"
            if fir_id not in G:
                from . import database as db
                fir_data = db.query_firs(fir_id=inv['fir_id'])
                if fir_data:
                    f = fir_data[0]
                    G.add_node(fir_id, label=f"FIR {f['fir_id']}: {f['crime_type']}", type="fir", location=f['location'])
                    nodes[fir_id] = {"label": f"FIR {f['fir_id']}: {f['crime_type']}", "type": "fir", "location": f['location']}
            if not G.has_edge(p_id, fir_id):
                G.add_edge(p_id, fir_id, role=inv['role'])
                edges.append({"source": p_id, "target": fir_id, "role": inv['role']})

    return {
        "nodes": [{"id": nid, **attrs} for nid, attrs in nodes.items()],
        "edges": edges
    }
