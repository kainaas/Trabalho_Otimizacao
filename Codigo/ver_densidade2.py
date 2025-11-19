# -*- coding: utf-8 -*-
"""
Este script visualiza a distribuição da população de São Carlos
diretamente nos seus setores censitários.

Ele gera um mapa onde cada polígono (setor) é colorido de acordo
com a sua população total, criando um mapa coroplético da cidade.
"""
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os


path_arquivos = 'Arquivos'
def gerar_mapa_coropletico_sao_carlos():
    """
    Carrega os dados geográficos e demográficos, une-os e gera o mapa.
    """
    # --- 1. CONFIGURAÇÃO DOS FICHEIROS E CÓDIGO DO MUNICÍPIO ---
    # Verifique se os nomes dos seus ficheiros correspondem a estes.
    ARQUIVO_SHAPEFILE_SETORES = os.path.join(path_arquivos, 'SP_Setores_CD2022.shp')
    ARQUIVO_CSV_POPULACAO = os.path.join(path_arquivos,'Agregados_por_setores_basico_BR_20250417.csv')
    CODIGO_MUNICIPIO_SAO_CARLOS = '3548906'

    # Verifica se os ficheiros de entrada existem
    for f in [ARQUIVO_SHAPEFILE_SETORES, ARQUIVO_CSV_POPULACAO]:
        if not os.path.exists(f):
            print(f"❌ Erro: Ficheiro de entrada não encontrado: '{f}'")
            print("Verifique se todos os ficheiros necessários estão na mesma pasta que o script.")
            return

    # --- 2. CARREGAR E PREPARAR OS DADOS ---
    try:
        print(f"A carregar o shapefile dos setores de '{ARQUIVO_SHAPEFILE_SETORES}'...")
        gdf_setores = gpd.read_file(ARQUIVO_SHAPEFILE_SETORES)
        
        print(f"A carregar os dados de população de '{ARQUIVO_CSV_POPULACAO}'...")
        df_pop = pd.read_csv(ARQUIVO_CSV_POPULACAO, sep=';', encoding='latin-1', dtype=str)
    except Exception as e:
        print(f"❌ Erro ao carregar os ficheiros: {e}")
        return

    # --- 3. FILTRAR E UNIR OS DADOS PARA SÃO CARLOS ---
    print("A filtrar dados para São Carlos e a preparar a união...")
    
    # Renomeia as colunas para um padrão ('CD_CENSO')
    gdf_setores.rename(columns={'CD_SETOR': 'CD_CENSO'}, inplace=True)
    df_pop.rename(columns={'CD_SETOR': 'CD_CENSO', 'v0001': 'POPULACAO'}, inplace=True)
    
    # Filtra apenas os dados de São Carlos da tabela de população
    df_pop_sc = df_pop[df_pop['CD_MUN'] == CODIGO_MUNICIPIO_SAO_CARLOS]
    df_pop_sc = df_pop_sc[['CD_CENSO', 'POPULACAO']].copy()
    df_pop_sc['POPULACAO'] = pd.to_numeric(df_pop_sc['POPULACAO'], errors='coerce').fillna(0)

    # Une o mapa de setores com os dados de população correspondentes
    # 'inner' merge garante que apenas setores com dados de população serão incluídos
    mapa_sc = gdf_setores.merge(df_pop_sc, on='CD_CENSO', how='inner')

    if len(mapa_sc) == 0:
        print("❌ Erro: A união dos dados não encontrou nenhum setor correspondente para São Carlos.")
        print("Verifique se os códigos de município e de setor estão corretos nos ficheiros.")
        return
        
    print(f"✅ Dados de {len(mapa_sc)} setores de São Carlos preparados para visualização.")

    # --- 4. GERAR O MAPA ---
    print("A gerar o mapa coroplético...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    
    mapa_sc.plot(column='POPULACAO',   # Coluna que define a cor
                 cmap='viridis',      # Paleta de cores (do mais escuro/baixo ao mais claro/alto)
                 linewidth=0.5,       # Espessura da borda dos polígonos
                 ax=ax,
                 edgecolor='0.8',     # Cor da borda (cinza)
                 legend=True,         # Mostrar a barra de legenda
                 legend_kwds={'label': "População por Setor Censitário",
                              'orientation': "horizontal",
                              'shrink': 0.7}) # Parâmetros da legenda

    # Configurações finais do gráfico
    ax.set_title('População por Setor Censitário em São Carlos (Censo 2022)', fontsize=16)
    ax.set_axis_off() # Remove os eixos X e Y para um visual mais limpo

    print("✅ Visualização pronta! A mostrar o mapa...")
    plt.show()

# --- Execução Principal ---
if __name__ == "__main__":
    gerar_mapa_coropletico_sao_carlos()
