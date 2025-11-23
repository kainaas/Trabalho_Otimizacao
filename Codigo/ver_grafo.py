import osmnx as ox
import matplotlib.pyplot as plt
from os import path

path_arquivos = 'Arquivos'

ARQUIVO_GRAFO = path.join(path_arquivos,'sao_carlos_grafo_preciso.graphml')

def visualizar_grafo(G):
    """
    Plota e exibe o grafo da cidade.
    """
    if G:
        print("Gerando visualização do grafo (pode levar um momento)...")
        fig, ax = ox.plot_graph(G, show=False, close=False, bgcolor='#FFFFFF', node_size=0, edge_color='k', edge_linewidth=0.5, figsize=(10,10))
        # force a square plot area
        try:
            ax.set_box_aspect(1)  # Matplotlib >= 3.3
        except Exception:
            ax.set_aspect('equal', adjustable='box')
        plt.suptitle("Malha Viária de São Carlos")
        plt.show()
        print("Visualização concluída.")

# --- Execução Principal ---
if __name__ == "__main__":

    G = ox.load_graphml(ARQUIVO_GRAFO)

    # A visualização é opcional, mas útil para confirmar que tudo correu bem
    visualizar_grafo(G)