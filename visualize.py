import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph, path_edges=None):
    """
    Visualizes a directed weighted graph using NetworkX.
    `graph` should have .adjacency as a dictionary like:
        { "A": [("B", 6), ("C", 8)], ... }

    `path_edges` is a list of tuples like [("A", "B"), ("B", "D")]
    representing the shortest/selected path to highlight.
    """
    G = nx.DiGraph()

    # Add all edges
    for node in graph.adjacency:
        for neighbor, weight in graph.adjacency[node]:
            G.add_edge(node, neighbor, weight=weight)

    pos = nx.spring_layout(G, seed=42)  # Consistent layout

    # Draw base edges (gray)
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', arrows=True)

    # Highlight path edges if provided
    if path_edges:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=path_edges,
            edge_color='green',
            width=2.5,
            arrows=True
        )

    # Draw nodes and labels
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1800)
    nx.draw_networkx_labels(G, pos, font_size=14, font_color='black')

    # Draw edge weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("✈️ Airport Route Graph", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
