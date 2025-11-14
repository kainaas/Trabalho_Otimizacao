# -*- coding: utf-8 -*-
"""
Este script lê o dicionário de população discreto e aplica um algoritmo
de suavização sobre o grafo. Ele "espalha" a população de cada nó para
seus vizinhos de forma iterativa, criando uma distribuição mais contínua
e realista, enquanto conserva a população total.
"""
import osmnx as ox
import pickle
import os
import copy

path_arquivos = 'Arquivos'

def suavizar_distribuicao_populacional():
    """
    Carrega a população, aplica o algoritmo de difusão e salva o resultado.
    """
    # --- 1. CONFIGURAÇÃO DOS ARQUIVOS E PARÂMETROS ---
    ARQUIVO_GRAFO = os.path.join(path_arquivos,'sao_carlos_grafo_preciso.graphml')
    ARQUIVO_POPULACAO_ORIGINAL = os.path.join(path_arquivos,'populacoes_nos.pkl')
    ARQUIVO_POPULACAO_SAIDA = os.path.join(path_arquivos,'populacoes_suavizadas.pkl')

    # --- PARÂMETROS DE SUAVIZAÇÃO (Você pode experimentar com estes!) ---
    # Quantas vezes o processo de "espalhar" será repetido.
    # Mais iterações = mais espalhado. Valores entre 2 e 5 são bons.
    NUMERO_DE_ITERACOES = 3

    # A fração da população que cada nó "mantém" para si em cada iteração.
    # O restante (1.0 - FATOR_DE_RETENCAO) será dividido entre os vizinhos.
    # Valores entre 0.4 e 0.6 funcionam bem.
    FATOR_DE_RETENCAO = 0.4

    # --- 2. CARREGAR OS DADOS ---
    print("Carregando grafo e população original...")
    if not all(os.path.exists(f) for f in [ARQUIVO_GRAFO, ARQUIVO_POPULACAO_ORIGINAL]):
        print("❌ Erro: Arquivos de entrada não encontrados.")
        return

    G = ox.load_graphml(ARQUIVO_GRAFO)
    with open(ARQUIVO_POPULACAO_ORIGINAL, 'rb') as f:
        populacoes_atuais = pickle.load(f)

    # Guarda a população total original para verificação no final
    populacao_total_original = sum(populacoes_atuais.values())
    print(f"População total original: {populacao_total_original:,.0f}")

    # --- 3. ALGORITMO DE SUAVIZAÇÃO (DIFUSÃO) ---
    print(f"\nIniciando processo de suavização com {NUMERO_DE_ITERACOES} iterações...")

    for i in range(NUMERO_DE_ITERACOES):
        # Usamos um novo dicionário para armazenar o resultado desta iteração
        novas_populacoes = {node: 0.0 for node in G.nodes()}
        
        # Para cada nó no grafo...
        for node, pop in populacoes_atuais.items():
            if pop == 0:
                continue

            # O nó mantém uma parte de sua própria população
            pop_retida = pop * FATOR_DE_RETENCAO
            novas_populacoes[node] += pop_retida
            
            # O restante é espalhado para os vizinhos
            pop_distribuida = pop * (1.0 - FATOR_DE_RETENCAO)
            vizinhos = list(G.neighbors(node))
            
            if vizinhos:
                share_por_vizinho = pop_distribuida / len(vizinhos)
                for vizinho in vizinhos:
                    novas_populacoes[vizinho] += share_por_vizinho
        
        # Atualiza o dicionário para a próxima iteração
        populacoes_atuais = novas_populacoes
        print(f"Iteração {i+1} concluída. População total: {sum(populacoes_atuais.values()):,.0f}")

    # --- 4. FINALIZAÇÃO E VERIFICAÇÃO ---
    # Arredonda os valores finais para inteiros
    populacoes_finais = {node: round(pop) for node, pop in populacoes_atuais.items()}
    
    # Ajuste final para garantir que a soma seja EXATAMENTE a mesma
    populacao_total_final = sum(populacoes_finais.values())
    diferenca = round(populacao_total_original - populacao_total_final)
    if diferenca != 0:
        # Adiciona ou remove a pequena diferença (devido a arredondamentos)
        # do nó com a maior população para minimizar o impacto.
        no_mais_populoso = max(populacoes_finais, key=populacoes_finais.get)
        populacoes_finais[no_mais_populoso] += diferenca

    populacao_total_verificada = sum(populacoes_finais.values())

    print("\n--- Verificação Final ---")
    print(f"População Original: {populacao_total_original:,.0f}")
    print(f"População Suavizada: {populacao_total_verificada:,.0f}")
    
    if int(populacao_total_original) == int(populacao_total_verificada):
        print("✅ A conservação da população foi mantida com sucesso!")
    else:
        print("⚠️ Atenção: Houve uma pequena perda/ganho de população no processo.")

    # --- 5. SALVAR O RESULTADO ---
    with open(ARQUIVO_POPULACAO_SAIDA, 'wb') as f:
        pickle.dump(populacoes_finais, f)
        
    print(f"\n✅ Processo concluído! Nova distribuição salva em '{ARQUIVO_POPULACAO_SAIDA}'.")

# --- Execução Principal ---
if __name__ == "__main__":
    suavizar_distribuicao_populacional()

