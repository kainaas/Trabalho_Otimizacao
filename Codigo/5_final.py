# -*- coding: utf-8 -*-
"""
Este script resolve o problema de localização de hospitais para São Carlos,
gera visualizações e exporta os resultados detalhados para um arquivo CSV.
"""
import networkx as nx
import pulp
import matplotlib.pyplot as plt
import osmnx as ox
import pickle
import time
import pandas as pd
import os

def carregar_distancias():
    arquivo_dist = os.path.join('Arquivos', 'matriz_distancias.pkl')
    if not os.path.exists(arquivo_dist):
        print("❌ Erro: Matriz de distâncias não encontrada.")
        print("Execute o script '3_5_calculo_distancias.py' primeiro.")
        return None
    
    print("Carregando matriz de distâncias pré-calculada...")
    with open(arquivo_dist, 'rb') as f:
        distancias = pickle.load(f)
    print("✅ Matriz carregada.")
    return distancias

def resolver_localizacao_hospitais(G, populacoes, distancias, n_hospitais, populacao_minima):
    """
    Resolve o problema de otimização linear.
    """
    print("\nFormulando o problema de otimização...")
    
    nos_populacao = list(G.nodes())
    locais_candidatos = [node for node, pop in populacoes.items() if pop >= populacao_minima and node in G.nodes()]
    
    print(f"Reduzindo o espaço de busca: de {len(nos_populacao)} para {len(locais_candidatos)} locais candidatos (com pop >= {populacao_minima}).")
    
    if not locais_candidatos or len(locais_candidatos) < n_hospitais:
        print("❌ Erro: Não há locais candidatos suficientes com os critérios definidos.")
        return None

    prob = pulp.LpProblem("Localizacao_Hospitais", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("Hospital", locais_candidatos, 0, 1, pulp.LpContinuous)
    y = pulp.LpVariable.dicts("Atende", (nos_populacao, locais_candidatos), 0, 1, pulp.LpContinuous)

    objetivo = pulp.lpSum([populacoes.get(i, 0) * distancias[i][j] * y[i][j] for i in nos_populacao for j in locais_candidatos])
    prob += objetivo

    prob += pulp.lpSum([x[j] for j in locais_candidatos]) == n_hospitais, "Num_Hospitais"
    for i in nos_populacao:
        prob += pulp.lpSum([y[i][j] for j in locais_candidatos]) == 1, f"Atendimento_Garantido_{i}"
    for i in nos_populacao:
        for j in locais_candidatos:
            prob += y[i][j] <= x[j], f"Logica_Atendimento_{i}_{j}"

    print("Resolvendo o problema... (Isso pode levar alguns minutos)")
    start_time = time.time()
    solver = pulp.PULP_CBC_CMD(msg=True, options=['dualSimplex'])
    prob.solve(solver)
    end_time = time.time()
    
    print(f"Problema resolvido em {end_time - start_time:.2f} segundos.")
    print("Status:", pulp.LpStatus[prob.status])

    return {j: x[j].varValue for j in locais_candidatos}

# --- NOVA FUNÇÃO ---
def exportar_resultados_csv(G, resultados):
    """
    Exporta os resultados da otimização para um arquivo CSV.
    """
    print("\nExportando resultados para arquivo CSV...")
    
    # Prepara os dados para o DataFrame
    dados_para_csv = []
    for node_id, probabilidade in resultados.items():
        dados_no = G.nodes[node_id]
        dados_para_csv.append({
            'ID do Cruzamento': node_id,
            'Posicao_X': dados_no.get('x'),
            'Posicao_Y': dados_no.get('y'),
            'Probabilidade': probabilidade
        })
        
    # Cria o DataFrame com o pandas
    df_resultados = pd.DataFrame(dados_para_csv)
    
    # Ordena o DataFrame pela probabilidade, da maior para a menor
    df_resultados = df_resultados.sort_values(by='Probabilidade', ascending=False)
    
    # Salva em um arquivo CSV
    nome_arquivo_saida = 'resultados_probabilidades.csv'
    df_resultados.to_csv(nome_arquivo_saida, index=False, sep=';', decimal=',')
    
    print(f"✅ Resultados exportados com sucesso para '{nome_arquivo_saida}'")

def visualizar_resultados(G, populacoes, resultados, n_hospitais):
    print("\nGerando visualização dos locais ótimos...")
    # ... (código de visualização sem alterações)
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    locais_otimos = sorted(resultados, key=resultados.get, reverse=True)[:n_hospitais]
    fig, ax = plt.subplots(figsize=(15, 15))
    ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color='gray', edge_linewidth=0.5)
    cores_pop = [populacoes.get(node, 0) for node in G.nodes()]
    nodes = nx.draw_networkx_nodes(G, pos=pos, node_color=cores_pop, cmap='viridis', node_size=15, ax=ax)
    nx.draw_networkx_nodes(G, pos=pos, nodelist=locais_otimos, node_color='red', node_shape='*', node_size=250, ax=ax, label='Hospitais')
    ax.set_title(f'Locais Ótimos para {n_hospitais} Hospitais em São Carlos', fontsize=16)
    plt.colorbar(nodes, label='População Atribuída ao Nó', shrink=0.7)
    plt.legend()
    plt.show()

def visualizar_probabilidades(G, resultados, n_hospitais):
    print("\nGerando visualização do mapa de probabilidades...")
    # ... (código de visualização sem alterações)
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    locais_candidatos = list(resultados.keys())
    valores_prob = list(resultados.values())
    locais_otimos = sorted(resultados, key=resultados.get, reverse=True)[:n_hospitais]
    fig, ax = plt.subplots(figsize=(15, 15))
    ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color='gray', edge_linewidth=0.5)
    nodes = nx.draw_networkx_nodes(G, pos=pos, nodelist=locais_candidatos, node_color=valores_prob, cmap='plasma', node_size=30, ax=ax)
    nx.draw_networkx_nodes(G, pos=pos, nodelist=locais_otimos, node_size=30, ax=ax, edgecolors='black', linewidths=1.5)
    ax.set_title(f'Mapa de Aptidão (Probabilidade) dos Locais Candidatos', fontsize=16)
    plt.colorbar(nodes, label='Probabilidade (Aptidão) do Local', shrink=0.7)
    plt.show()

# --- Execução Principal ---
if __name__ == "__main__":
    print("--- Etapa 1: Carregando Dados ---")
    try:
        G = ox.load_graphml(os.path.join('Arquivos','sao_carlos_grafo_preciso.graphml'))
        with open(os.path.join('Arquivos', 'populacoes_suavizadas.pkl'), 'rb') as f:
            populacoes = pickle.load(f)
        
        # AQUI MUDOU: Carrega em vez de calcular
        distancias = carregar_distancias()
        if distancias is None: exit()
            
        print("Dados carregados com sucesso!")
    except FileNotFoundError:
        print("Erro: Arquivos base não encontrados.")
        exit()

    populacoes_filtradas = {node: pop for node, pop in populacoes.items() if node in G.nodes()}

    # --- PARÂMETROS ---
    NUMERO_DE_HOSPITAIS = 9
    POPULACAO_MINIMA_CANDIDATO = 200 

    # --- PROCESSAMENTO ---
    resultados = resolver_localizacao_hospitais(G, populacoes_filtradas, distancias, NUMERO_DE_HOSPITAIS, POPULACAO_MINIMA_CANDIDATO)

    # --- ANÁLISE E EXPORTAÇÃO ---
    if resultados:
        # Mostra o primeiro gráfico (resultados finais)
        visualizar_resultados(G, populacoes_filtradas, resultados, NUMERO_DE_HOSPITAIS)
        # Mostra o segundo gráfico (análise de probabilidades)
        visualizar_probabilidades(G, resultados, NUMERO_DE_HOSPITAIS)
        # Exporta os dados para um arquivo CSV
        exportar_resultados_csv(G, resultados)

