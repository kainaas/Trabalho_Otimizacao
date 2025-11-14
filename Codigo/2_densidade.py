# -*- coding: utf-8 -*-
import geopandas as gpd
import pandas as pd
import osmnx as ox
import pickle
import os

Arquivos_path = 'Arquivos'

def integrar_populacao_ao_grafo():
    # --- 1. CONFIGURAÇÃO DOS ARQUIVOS DE ENTRADA ---
    ARQUIVO_GRAFO = os.path.join(Arquivos_path, 'sao_carlos_grafo_preciso.graphml')
    ARQUIVO_SHAPEFILE_SETORES = os.path.join(Arquivos_path, 'SP_Setores_CD2022.shp')
    ARQUIVO_CSV_POPULACAO = os.path.join(Arquivos_path, 'Agregados_por_setores_basico_BR_20250417.csv')
    CODIGO_MUNICIPIO_SAO_CARLOS = '3548906'
    
    for f in [ARQUIVO_GRAFO, ARQUIVO_SHAPEFILE_SETORES, ARQUIVO_CSV_POPULACAO]:
        if not os.path.exists(f):
            print(f"❌ Erro: Arquivo de entrada não encontrado: '{f}'")
            return

    # --- 2. CARREGAR OS DADOS ---
    try:
        print(f"Carregando o grafo de ruas de '{ARQUIVO_GRAFO}'...")
        G = ox.load_graphml(ARQUIVO_GRAFO)
        
        print(f"Carregando o shapefile dos setores de '{ARQUIVO_SHAPEFILE_SETORES}'...")
        gdf_setores = gpd.read_file(ARQUIVO_SHAPEFILE_SETORES)
        
        print(f"Carregando os dados de população de '{ARQUIVO_CSV_POPULACAO}'...")
        df_pop = pd.read_csv(ARQUIVO_CSV_POPULACAO, sep=';', encoding='latin-1', dtype=str)
    except Exception as e:
        print(f"❌ Erro ao carregar os arquivos: {e}")
        return

    # --- 3. LIMPEZA E PREPARAÇÃO DOS DADOS ---
    print("\nLimpando e preparando os dados...")
    
    # Renomeia as colunas para um padrão ('CD_CENSO')
    gdf_setores.rename(columns={'CD_SETOR': 'CD_CENSO'}, inplace=True)
    df_pop.rename(columns={'CD_SETOR': 'CD_CENSO', 'v0001': 'POPULACAO'}, inplace=True)
    
    # Filtra apenas as colunas que vamos usar
    df_pop_filtrado = df_pop[['CD_CENSO', 'CD_MUN', 'POPULACAO']].copy()
    df_pop_filtrado['POPULACAO'] = pd.to_numeric(df_pop_filtrado['POPULACAO'], errors='coerce').fillna(0).astype(int)
    
    # Filtra apenas os dados de São Carlos
    df_pop_sc = df_pop_filtrado[df_pop_filtrado['CD_MUN'] == CODIGO_MUNICIPIO_SAO_CARLOS]

    # --- NOVO: DEBUG E CORREÇÃO DE TIPO DE DADO ---
    print(f"Tipo de dado da coluna 'CD_CENSO' no Shapefile: {gdf_setores['CD_CENSO'].dtype}")
    print(f"Tipo de dado da coluna 'CD_CENSO' na População: {df_pop_sc['CD_CENSO'].dtype}")
    print("Amostra dos códigos (Shapefile): \n", gdf_setores['CD_CENSO'].head(3))
    print("Amostra dos códigos (População): \n", df_pop_sc['CD_CENSO'].head(3))

    # ** A CORREÇÃO CRÍTICA ESTÁ AQUI **
    # Força AMBAS as colunas a serem do tipo 'string' antes de unir
    gdf_setores['CD_CENSO'] = gdf_setores['CD_CENSO'].astype(str)
    df_pop_sc['CD_CENSO'] = df_pop_sc['CD_CENSO'].astype(str)
    
    # --- 4. UNIÃO (MERGE) DOS DADOS ---
    print("\nUnindo mapa e população...")
    gdf_sc = gdf_setores.merge(df_pop_sc, on='CD_CENSO')
    
    if len(gdf_sc) == 0:
        print("❌ ATENÇÃO: A união dos dados resultou em 0 setores. Verifique se os códigos 'CD_CENSO' nos arquivos são compatíveis.")
        return
        
    print(f"✅ Encontrados e processados {len(gdf_sc)} setores censitários para São Carlos.")
    gdf_sc = gdf_sc.to_crs(G.graph['crs'])

    # --- 5. MAPEAMENTO E AGREGAÇÃO ---
    print("Mapeando população dos setores para os nós do grafo...")
    gdf_sc['centroide'] = gdf_sc['geometry'].centroid
    nos_proximos = ox.nearest_nodes(G, X=gdf_sc['centroide'].x, Y=gdf_sc['centroide'].y)
    gdf_sc['no_mais_proximo'] = nos_proximos
    
    populacao_por_no = gdf_sc.groupby('no_mais_proximo')['POPULACAO'].sum()
    dict_populacao = populacao_por_no.to_dict()
    
    for node_id in G.nodes():
        if node_id not in dict_populacao:
            dict_populacao[node_id] = 0

    # --- 6. SALVAR O RESULTADO ---
    ARQUIVO_SAIDA = os.path.join(Arquivos_path, 'populacoes_nos.pkl')
    with open(ARQUIVO_SAIDA, 'wb') as f:
        pickle.dump(dict_populacao, f)
    
    print(f"\n✅ Processo concluído! Dicionário de população salvo em '{ARQUIVO_SAIDA}'.")
    
if __name__ == "__main__":
    integrar_populacao_ao_grafo()

