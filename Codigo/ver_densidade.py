# -*- coding: utf-8 -*-
"""
Este script cria uma visualização comparativa da densidade populacional.

Ele gera dois mapas:
1. O mapa de calor completo com todos os pontos.
2. Um mapa filtrado, mostrando apenas os nós com população acima de um
   determinado limite, para destacar as áreas mais densas.
"""
import osmnx as ox
import pickle
import matplotlib.pyplot as plt
import networkx as nx
import os

path_arquivos = 'Arquivos'

def visualizar_mapas_comparativos():
    """
    Gera e exibe os dois mapas de densidade populacional.
    """
    # --- 1. CONFIGURAÇÃO DOS ARQUIVOS E PARÂMETROS ---
    ARQUIVO_GRAFO = os.path.join(path_arquivos,'sao_carlos_grafo_preciso.graphml')
    # Escolha qual arquivo de população você quer visualizar:
    ARQUIVO_POPULACAO = os.path.join('populacoes_suavizadas.pkl') # Ou 'populacoes_nos.pkl'

    # !! PARÂMETRO CHAVE !!
    # Define a população mínima para que um nó seja exibido no mapa da direita.
    # Experimente com valores como 1, 10, 50 para ver o efeito.
    POPULACAO_MINIMA_PARA_EXIBIR = 1
    # --- 2. CARREGAR OS DADOS ---
    print("Carregando grafo e população...")
    if not all(os.path.exists(f) for f in [ARQUIVO_GRAFO, ARQUIVO_POPULACAO]):
        print("❌ Erro: Arquivos de entrada não encontrados.")
        return

    G = ox.load_graphml(ARQUIVO_GRAFO)
    with open(ARQUIVO_POPULACAO, 'rb') as f:
        populacoes = pickle.load(f)

    # --- 3. PREPARAR PARA A VISUALIZAÇÃO ---
    print("Preparando os dados para a plotagem...")
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    
    # --- 4. GERAR OS GRÁFICOS COMPARATIVOS ---
    print(f"Gerando visualizações... (Filtro: População >= {POPULACAO_MINIMA_PARA_EXIBIR})")
    
    # Cria uma figura com dois subplots (1 linha, 2 colunas)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 10))

    # --- Gráfico 1: Completo (Esquerda) ---
    ax1.set_title('Distribuição Completa', fontsize=16)
    ox.plot_graph(G, ax=ax1, show=False, close=False, node_size=0, edge_color='#CCCCCC')
    valores_completos = [populacoes.get(node, 0) for node in G.nodes()]
    nodes1 = nx.draw_networkx_nodes(G, pos=pos, node_color=valores_completos,
                                    cmap='plasma', node_size=10, ax=ax1)
    fig.colorbar(nodes1, ax=ax1, shrink=0.6, label='População Atribuída')

    # --- Gráfico 2: Filtrado (Direita) ---
    ax2.set_title(f'Distribuição Filtrada (Pop. >= {POPULACAO_MINIMA_PARA_EXIBIR})', fontsize=16)
    ox.plot_graph(G, ax=ax2, show=False, close=False, node_size=0, edge_color='#CCCCCC')

    # Filtra os nós que atendem ao critério
    nos_para_exibir = [node for node, pop in populacoes.items() if pop >= POPULACAO_MINIMA_PARA_EXIBIR]
    valores_filtrados = [populacoes[node] for node in nos_para_exibir]

    if nos_para_exibir:
        nodes2 = nx.draw_networkx_nodes(G, pos=pos, nodelist=nos_para_exibir,
                                        node_color=valores_filtrados, cmap='plasma',
                                        node_size=15, ax=ax2)
        fig.colorbar(nodes2, ax=ax2, shrink=0.6, label='População Atribuída')
    else:
        ax2.text(0.5, 0.5, 'Nenhum nó atende ao critério', ha='center', va='center', transform=ax2.transAxes)

    fig.suptitle(f'Comparativo da Densidade Populacional de São Carlos ({os.path.basename(ARQUIVO_POPULACAO)})', fontsize=20)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("✅ Visualização pronta! Mostrando o gráfico...")
    plt.show()

# --- Execução Principal ---
if __name__ == "__main__":
    visualizar_mapas_comparativos()