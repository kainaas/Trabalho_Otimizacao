# -*- coding: utf-8 -*-
"""
Script 4: Pré-cálculo da Matriz de Distâncias
Este script carrega o grafo, calcula a distância real (caminho mínimo)
entre TODOS os pares de nós e salva o resultado em um arquivo .pkl.
Isso evita recalcular distâncias a cada execução do modelo de otimização.
"""
import networkx as nx
import osmnx as ox
import pickle
import os
import time

path_arquivos = 'Arquivos'

def pre_calcular_distancias():
    # --- 1. CARREGAR O GRAFO ---
    ARQUIVO_GRAFO = os.path.join(path_arquivos, 'sao_carlos_grafo_preciso.graphml')
    ARQUIVO_SAIDA_DISTANCIAS = os.path.join(path_arquivos, 'matriz_distancias.pkl')

    if not os.path.exists(ARQUIVO_GRAFO):
        print("❌ Erro: Grafo não encontrado.")
        return

    print("Carregando grafo...")
    G = ox.load_graphml(ARQUIVO_GRAFO)
    
    # Converter para não-direcionado (permite ir e voltar na mesma rua)
    # Importante para a matriz ser simétrica e o cálculo ser consistente
    G_undirected = G.to_undirected()
    
    # --- 2. CÁLCULO PESADO ---
    print(f"Iniciando cálculo de distâncias para {len(G.nodes())} nós...")
    print("Isso pode levar alguns minutos. Vá tomar um café...")
    
    start_time = time.time()
    # all_pairs_dijkstra_path_length retorna um gerador, convertemos para dict
    # Estrutura: {origem: {destino: distancia, destino2: distancia2...}}
    distancias = dict(nx.all_pairs_dijkstra_path_length(G_undirected, weight='length'))
    end_time = time.time()
    
    tempo_total = end_time - start_time
    print(f"✅ Cálculo concluído em {tempo_total:.2f} segundos ({tempo_total/60:.2f} minutos).")

    # --- 3. SALVAR EM DISCO ---
    print(f"Salvando matriz de distâncias em '{ARQUIVO_SAIDA_DISTANCIAS}'...")
    with open(ARQUIVO_SAIDA_DISTANCIAS, 'wb') as f:
        pickle.dump(distancias, f)
    
    print("✅ Arquivo salvo!")

if __name__ == "__main__":
    pre_calcular_distancias()