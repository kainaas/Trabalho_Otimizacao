# -*- coding: utf-8 -*-
"""
Este script resolve o problema de localização de hospitais utilizando um
modelo simplificado e muito mais eficiente.

Abordagem:
1. Carrega o grafo completo de ruas de São Carlos.
2. Identifica os ~476 nós que representam centros populacionais (pop > 0).
3. Calcula a matriz de distâncias de viagem real entre TODOS os nós no grafo completo.
4. Formula e resolve o problema de otimização considerando apenas os centros
   populacionais como possíveis locais para hospitais e como pontos de demanda.
Isto reduz drasticamente a complexidade, tornando a solução rápida e estável.
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
        print("Execute o script '3_5_calculo_distancias.py' primeiro.")
        return None
    print("Carregando matriz de distâncias pré-calculada...")
    with open(arquivo_dist, 'rb') as f:
        return pickle.load(f)

def resolver_otimizacao_simplificada(nos_populacao, populacoes, distancias, n_hospitais):
    """
    Resolve o problema de otimização no grafo simplificado de centros populacionais.
    """
    print("\nFormulando o problema de otimização simplificado...")
    
    # No modelo simplificado, os locais candidatos são os próprios centros populacionais.
    locais_candidatos = nos_populacao
    
    prob = pulp.LpProblem("Localizacao_Hospitais_Simplificada", pulp.LpMinimize)
    
    # Variáveis de decisão
    x = pulp.LpVariable.dicts("Hospital", locais_candidatos, 0, 1, pulp.LpContinuous)
    y = pulp.LpVariable.dicts("Atende", (nos_populacao, locais_candidatos), 0, 1, pulp.LpContinuous)

    # Função Objetivo: Usa as distâncias REAIS pré-calculadas entre os centros populacionais
    objetivo = pulp.lpSum([populacoes[i] * distancias[i][j] * y[i][j] for i in nos_populacao for j in locais_candidatos])
    prob += objetivo

    # Restrições
    prob += pulp.lpSum([x[j] for j in locais_candidatos]) == n_hospitais, "Num_Hospitais"
    for i in nos_populacao:
        prob += pulp.lpSum([y[i][j] for j in locais_candidatos]) == 1, f"Atendimento_Garantido_{i}"
    for i in nos_populacao:
        for j in locais_candidatos:
            prob += y[i][j] <= x[j], f"Logica_Atendimento_{i}_{j}"

    print("A resolver o problema... (Esta etapa agora será muito mais rápida!)")
    start_time = time.time()
    solver = pulp.PULP_CBC_CMD(msg=True, options=['dualSimplex'])
    prob.solve(solver)
    end_time = time.time()
    
    print(f"Problema resolvido em {end_time - start_time:.2f} segundos.")
    print("Status:", pulp.LpStatus[prob.status])
    
    if pulp.LpStatus[prob.status] == 'Optimal':
        return {j: x[j].varValue for j in locais_candidatos}
    else:
        return None


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
    nome_arquivo_saida = os.path.join('Arquivos','resultados_probabilidades.csv')
    df_resultados.to_csv(nome_arquivo_saida, index=False, sep=';', decimal=',')
    
    print(f"✅ Resultados exportados com sucesso para '{nome_arquivo_saida}'")



def visualizar_resultados_simplificados(G_completo, nos_populacao, populacoes, resultados, n_hospitais):
    """
    Visualiza os resultados, mostrando os centros populacionais e os locais ótimos
    sobre o mapa de ruas completo.
    """
    print("\nA gerar visualização dos resultados...")
    pos = {node: (data['x'], data['y']) for node, data in G_completo.nodes(data=True)}
    locais_otimos = sorted(resultados, key=resultados.get, reverse=True)[:n_hospitais]

    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Desenha o mapa de ruas completo como fundo
    ox.plot_graph(G_completo, ax=ax, show=False, close=False, node_size=0, edge_color='#CCCCCC', edge_linewidth=0.4)

    # Desenha apenas os nós que são centros populacionais
    cores_pop = [populacoes.get(node, 0) for node in nos_populacao]
    nodes = nx.draw_networkx_nodes(G_completo, pos=pos, nodelist=nos_populacao, 
                                   node_color=cores_pop, cmap='viridis', 
                                   node_size=25, ax=ax)
    
    # Destaca os locais ótimos (que são um subconjunto dos centros populacionais)
    nx.draw_networkx_nodes(G_completo, pos=pos, nodelist=locais_otimos, 
                           node_color='red', node_shape='*', node_size=300, 
                           ax=ax, label='Hospitais')

    ax.set_title(f'Locais Ótimos para {n_hospitais} Hospitais (Modelo Simplificado)', fontsize=16)
    plt.colorbar(nodes, label='População no Centro do Setor', shrink=0.7)
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
    print("--- Etapa 1: Carregar Dados Reais ---")
    try:
        G_completo = ox.load_graphml(os.path.join('Arquivos', 'sao_carlos_grafo_preciso.graphml'))
        # Use o ficheiro de população que preferir (original ou suavizado)
        with open(os.path.join('Arquivos','populacoes_nos.pkl'), 'rb') as f:
            populacoes_completas = pickle.load(f)
            # AQUI MUDOU: Carrega distâncias
            distancias_completas = carregar_distancias()
            if distancias_completas is None: exit()
        print("Grafo e populações carregados com sucesso!")
    except FileNotFoundError:
        print("Erro: Ficheiros do grafo ou da população não encontrados.")
        exit()

    # --- Etapa 2: Simplificar o Problema ---
    # Criar a lista de nós que realmente importam (aqueles com população)
    nos_populacao = [node for node, pop in populacoes_completas.items() if pop > 0 and node in G_completo.nodes()]
    populacoes_filtradas = {node: pop for node, pop in populacoes_completas.items() if node in nos_populacao}
    print(f"\nProblema simplificado de {len(G_completo.nodes())} para {len(nos_populacao)} nós (centros populacionais).")
    
    # --- PARÂMETROS ---
    NUMERO_DE_HOSPITAIS = 6

    # --- PROCESSAMENTO ---
    # A otimização é feita apenas no conjunto simplificado de nós
    resultados = resolver_otimizacao_simplificada(nos_populacao, populacoes_filtradas, distancias_completas, NUMERO_DE_HOSPITAIS)

    # --- ANÁLISE E EXPORTAÇÃO ---
    if resultados:
        # Mostra o primeiro gráfico (resultados finais)
        visualizar_resultados_simplificados(G_completo, nos_populacao, populacoes_filtradas, resultados, NUMERO_DE_HOSPITAIS)
        # Mostra o segundo gráfico (análise de probabilidades)
        visualizar_probabilidades(G_completo, resultados, NUMERO_DE_HOSPITAIS)
        # Exporta os dados para um arquivo CSV
        exportar_resultados_csv(G_completo, resultados)