# -*- coding: utf-8 -*-
"""
Este script baixa a malha viária da área urbana de São Carlos, SP,
utilizando a biblioteca OSMnx, e a salva em um arquivo no formato GraphML.

Versão corrigida para garantir que o arquivo do grafo seja salvo corretamente.
"""
import osmnx as ox
import matplotlib.pyplot as plt
from os import path

path_arquivos = 'Arquivos'

def extrair_e_salvar_grafo():
    """
    Extrai o grafo da malha viária de São Carlos a partir do seu polígono
    geográfico e o salva em disco.
    """
    nome_cidade = "São Carlos, São Paulo, Brazil"
    arquivo_saida = path.join(path_arquivos, 'sao_carlos_grafo_preciso.graphml')
    
    print(f"Definindo a cidade de interesse: {nome_cidade}")
    
    try:
        # Passo 1: Obter o polígono geográfico preciso da cidade
        print("Obtendo o polígono geográfico da cidade...")
        gdf = ox.geocode_to_gdf(nome_cidade)
        poligono = gdf.unary_union
        
        # Passo 2: Baixar o grafo estritamente de dentro do polígono
        print("Baixando o grafo da malha viária de dentro do polígono...")
        G = ox.graph_from_polygon(poligono, network_type='drive', simplify=False)
        print("Grafo bruto baixado com sucesso!")
        
        # Passo 3: Projetar o grafo para um sistema de coordenadas métricas (UTM)
        print("Projetando o grafo para o sistema de coordenadas UTM...")
        G_projetado = ox.project_graph(G)

        # Passo 4: Simplificar o grafo para manter apenas as interseções
        print("Simplificando o grafo...")
        G_simplificado = ox.simplify_graph(G_projetado)
        print("Grafo simplificado com sucesso!")
        
        # Passo 5: Salvar o grafo final em disco
        print(f"Salvando o grafo simplificado em '{arquivo_saida}'...")
        ox.save_graphml(G_simplificado, filepath=arquivo_saida)
        print("Grafo salvo!")
        
        return G_simplificado

    except Exception as e:
        print(f"Ocorreu um erro durante o processo: {e}")
        print("Verifique sua conexão com a internet e se o nome da cidade está correto.")
        return None

def visualizar_grafo(G):
    """
    Plota e exibe o grafo da cidade.
    """
    if G:
        print("Gerando visualização do grafo (pode levar um momento)...")
        fig, ax = ox.plot_graph(G, show=False, close=False, bgcolor='#FFFFFF', node_size=0, edge_color='k', edge_linewidth=0.5)
        plt.suptitle("Malha Viária de São Carlos (Apenas Interseções)")
        plt.show()
        print("Visualização concluída.")

# --- Execução Principal ---
if __name__ == "__main__":
    # Esta é a parte que foi corrigida. Agora a função é chamada e o resultado é salvo.
    grafo_sc = extrair_e_salvar_grafo()
    
    if grafo_sc:
        # A visualização é opcional, mas útil para confirmar que tudo correu bem
        visualizar_grafo(grafo_sc)