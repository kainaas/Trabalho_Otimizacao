"""
Mapa dos hospitais e UPAs de São Carlos (SP) usando OSMnx + GeoPandas
Salve este arquivo como `mapa_hospitais_saocarlos.py` e execute localmente.

Requisitos:
  pip install osmnx geopandas matplotlib contextily

O script:
- geocodifica os endereços/nome das unidades (adiciona ", Sao Carlos, SP, Brazil" para precisão)
- baixa a malha viária da cidade (network_type='drive')
- plota a malha e marca os pontos com rótulos
- salva `mapa_hospitais_saocarlos.png`

Observação: a geocodificação e o download de dados OSM dependem de internet.
"""

import os
import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# ox.config não é mais necessário nas versões novas do OSMnx
# Apenas removido

# Lista de locais solicitados (nome amigável -> consulta para geocodificação)
places = {
    "HU-UFSCar": "Hospital Universitario Professor Doutor Horacio Carlos Panepucci, Sao Carlos, SP, Brazil",
    "Santa Casa": "Santa Casa de Sao Carlos, Sao Carlos, SP, Brazil",
    "Norden": "Norden Hospital Sao Carlos, Sao Carlos, SP, Brazil",
    "Hospital Unimed I": "Hospital Unimed Sao Carlos Unidade I, Sao Carlos, SP, Brazil",
    "Hospital Unimed II": "Hospital Unimed Sao Carlos Unidade II, Sao Carlos, Sao Carlos, SP, Brazil",
    "UPA Vila Prado": "UPA Vila Prado, Sao Carlos, SP, Brazil",
    "UPA Cidade Aracy": "UPA Cidade Aracy, Sao Carlos, SP, Brazil",
    "UPA Santa Felicia": "UPA Santa Felicia, Sao Carlos, SP, Brazil",
}

# Geocodifica cada local e armazena em um GeoDataFrame
geocoded = []
for key, query in places.items():
    try:
        gdf = ox.geocoder.geocode_to_gdf(query)
        gdf = gdf.assign(name=key)
        geocoded.append(gdf)
        print(f"Geocodificado: {key} -> {gdf.geometry.iloc[0].y:.6f}, {gdf.geometry.iloc[0].x:.6f}")
    except Exception as e:
        print(f"Falha ao geocodificar {key}: {e}")

if not geocoded:
    raise SystemExit("Nenhum ponto foi geocodificado. Verifique a conexão de internet e as dependências.")

points_gdf = gpd.GeoDataFrame(pd.concat(geocoded, ignore_index=True)) if len(geocoded) > 1 else geocoded[0]
points_gdf = points_gdf.set_crs(epsg=4326)

# Baixa o grafo de ruas de São Carlos
place_name = "São Carlos, São Paulo, Brazil"
print("Baixando malha viária de São Carlos (pode demorar alguns segundos)...")
G = ox.graph_from_place(place_name, network_type="drive")

# Converte o grafo para GeoDataFrames (nodes/edges) e projeta tudo para coordenadas métricas
nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
nodes_proj = ox.projection.project_gdf(nodes)
edges_proj = ox.projection.project_gdf(edges)
points_proj = points_gdf.to_crs(nodes_proj.crs)

# Plot
fig, ax = plt.subplots(figsize=(12, 12))

# desenha as vias
edges_proj.plot(ax=ax, linewidth=0.4)

# desenha os pontos (hospitais e UPAs)
points_proj.plot(ax=ax, markersize=80, marker='o', zorder=3, color='red')

# anota os pontos
for idx, row in points_proj.iterrows():
    # Usa centróide caso a geometria não seja ponto
    pt = row.geometry.centroid if row.geometry.geom_type != 'Point' else row.geometry
    x, y = pt.x, pt.y
    ax.annotate(row['name'], xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=9)

ax.set_title('Hospitais e UPAs - S\u00e3o Carlos (SP)')
ax.axis('off')

try:
    ax.set_box_aspect(1)  # Matplotlib >= 3.3
except Exception:
    ax.set_aspect('equal', adjustable='box')

outfn = os.path.join('..','Relatorio', 'Imagens', 'mapa_hospitais_saocarlos.pdf')
plt.tight_layout()
plt.savefig(outfn, dpi=300)
print(f"Mapa salvo em: {os.path.abspath(outfn)}")
plt.show()
