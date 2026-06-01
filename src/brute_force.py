"""
brute_force.py
==============
Enumeração completa (Força Bruta) de todos os caminhos simples
entre a origem e o destino num grafo pequeno (N ≤ 12).

Papel no sistema:
    - Valida o algoritmo Guloso (Dijkstra)
    - Demonstra a explosão combinatória
    - Serve de oráculo: retorna o caminho ótimo global

Complexidade:
    Tempo  : O(n!) no pior caso (todos os caminhos hamiltonianos)
    Espaço : O(n)  pela pilha de recursão + O(k·n) pelos caminhos salvos
"""

from __future__ import annotations
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_structures import Grafo, construir_grafo_rs, construir_grafo_matopiba


# ---------------------------------------------------------------------------
# Contadores globais (instrumentação)
# ---------------------------------------------------------------------------
_chamadas_recursivas: int = 0
_caminhos_avaliados: int = 0


def resetar_contadores() -> None:
    global _chamadas_recursivas, _caminhos_avaliados
    _chamadas_recursivas = 0
    _caminhos_avaliados = 0


def obter_contadores() -> dict:
    return {
        "chamadas_recursivas": _chamadas_recursivas,
        "caminhos_avaliados": _caminhos_avaliados,
    }


# ---------------------------------------------------------------------------
# Força Bruta — backtracking
# ---------------------------------------------------------------------------

def forca_bruta_caminhos(
    grafo: Grafo,
    origem: int,
    destino: int,
) -> dict:
    """
    Enumera todos os caminhos simples (sem repetição de vértice)
    entre `origem` e `destino`.

    Retorna
    -------
    dict com:
        melhor_caminho  : lista de ids
        melhor_custo    : float
        todos_caminhos  : lista de (caminho, custo)
        chamadas        : int  — número de chamadas recursivas
        avaliados       : int  — número de caminhos completos avaliados
    """
    global _chamadas_recursivas, _caminhos_avaliados
    resetar_contadores()

    melhor: dict = {"custo": float("inf"), "caminho": []}
    todos: list = []

    def backtrack(atual: int, caminho: list[int], custo: float,
                  visitados: set[int]) -> None:
        global _chamadas_recursivas, _caminhos_avaliados
        _chamadas_recursivas += 1

        if atual == destino:
            _caminhos_avaliados += 1
            todos.append((list(caminho), custo))
            if custo < melhor["custo"]:
                melhor["custo"] = custo
                melhor["caminho"] = list(caminho)
            return

        for (vizinho, peso) in grafo.vizinhos(atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                caminho.append(vizinho)
                backtrack(vizinho, caminho, custo + peso, visitados)
                caminho.pop()
                visitados.remove(vizinho)

    visitados_inicial: set[int] = {origem}
    backtrack(origem, [origem], 0.0, visitados_inicial)

    return {
        "melhor_caminho": melhor["caminho"],
        "melhor_custo": melhor["custo"],
        "todos_caminhos": todos,
        "chamadas": _chamadas_recursivas,
        "avaliados": _caminhos_avaliados,
    }


# ---------------------------------------------------------------------------
# Explosão combinatória — experimento de crescimento
# ---------------------------------------------------------------------------

def experimento_crescimento(tamanhos: list[int] = None) -> list[dict]:
    """
    Gera grafos sintéticos com N vértices (completos) e mede
    o número de caminhos e o tempo de execução da Força Bruta.

    Limitado a N ≤ 12 para evitar travamento.
    """
    if tamanhos is None:
        tamanhos = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    resultados = []

    for n in tamanhos:
        # Grafo completo sintético com n vértices
        g = Grafo()
        for i in range(n):
            from data_structures import criar_vertice
            v = criar_vertice(i, f"Mun{i}", round(0.1 * (i + 1), 2),
                              float(100 + i * 50), 10000 + i * 1000)
            g.adicionar_vertice(v)
        # Adiciona todas as arestas (grafo completo)
        ids = g.ids()
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                g.adicionar_aresta(ids[i], ids[j], float(i + j + 1))

        inicio = time.perf_counter()
        resultado = forca_bruta_caminhos(g, ids[0], ids[-1])
        fim = time.perf_counter()

        resultados.append({
            "n": n,
            "tempo_ms": (fim - inicio) * 1000,
            "caminhos_avaliados": resultado["avaliados"],
            "chamadas_recursivas": resultado["chamadas"],
            "melhor_custo": resultado["melhor_custo"],
        })

        print(f"  N={n:2d} | caminhos={resultado['avaliados']:8,d} | "
              f"chamadas={resultado['chamadas']:10,d} | "
              f"tempo={resultados[-1]['tempo_ms']:.2f}ms")

    return resultados


# ---------------------------------------------------------------------------
# Demonstração
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("FORÇA BRUTA — Global Solution 2026")
    print("=" * 65)

    # --- Cenário A (RS) — grafo de 12 vértices ---
    print("\n[1] Cenário A — RS (N=12 vértices)")
    g_rs = construir_grafo_rs()
    ids_rs = g_rs.ids()
    print(f"  Grafo: {g_rs}")

    # Menor caminho de Porto Alegre (4314902) → Rio Grande (4315602)
    origem, destino = 4314902, 4315602
    print(f"\n  Força Bruta: {g_rs.vertices[origem][1]} → "
          f"{g_rs.vertices[destino][1]}")

    t0 = time.perf_counter()
    res = forca_bruta_caminhos(g_rs, origem, destino)
    t1 = time.perf_counter()

    if res["melhor_caminho"]:
        nomes = [g_rs.vertices[i][1] for i in res["melhor_caminho"]]
        print(f"  Melhor caminho : {' → '.join(nomes)}")
        print(f"  Custo ótimo    : {res['melhor_custo']:.2f} h")
    else:
        print("  Sem caminho encontrado.")

    print(f"  Caminhos avaliados  : {res['avaliados']:,}")
    print(f"  Chamadas recursivas : {res['chamadas']:,}")
    print(f"  Tempo de execução   : {(t1 - t0)*1000:.2f} ms")

    if res["todos_caminhos"]:
        print(f"\n  Top 5 melhores caminhos:")
        top5 = sorted(res["todos_caminhos"], key=lambda x: x[1])[:5]
        for cam, custo in top5:
            nomes = [g_rs.vertices[i][1] for i in cam]
            print(f"    custo={custo:.2f}h  {' → '.join(nomes)}")

    # --- Cenário B (MATOPIBA) ---
    print("\n[2] Cenário B — MATOPIBA")
    g_mat = construir_grafo_matopiba()
    ids_mat = g_mat.ids()
    print(f"  Grafo: {g_mat}")

    origem_m = 1721000   # Palmas (hub)
    destino_m = 2933307  # Luís Eduardo Magalhães
    print(f"\n  Força Bruta: {g_mat.vertices[origem_m][1]} → "
          f"{g_mat.vertices[destino_m][1]}")

    t0 = time.perf_counter()
    res_m = forca_bruta_caminhos(g_mat, origem_m, destino_m)
    t1 = time.perf_counter()

    if res_m["melhor_caminho"]:
        nomes_m = [g_mat.vertices[i][1] for i in res_m["melhor_caminho"]]
        print(f"  Melhor caminho : {' → '.join(nomes_m)}")
        print(f"  Custo ótimo    : {res_m['melhor_custo']:.0f} km")
    print(f"  Caminhos avaliados  : {res_m['avaliados']:,}")
    print(f"  Chamadas recursivas : {res_m['chamadas']:,}")
    print(f"  Tempo               : {(t1 - t0)*1000:.2f} ms")

    # --- Experimento de crescimento ---
    print("\n[3] Experimento de Explosão Combinatória")
    print("  (grafos completos sintéticos, N ≤ 12)")
    dados_crescimento = experimento_crescimento()

    print("\n  Resumo:")
    for d in dados_crescimento:
        print(f"    N={d['n']:2d} | caminhos={d['caminhos_avaliados']:8,d} | "
              f"tempo={d['tempo_ms']:.2f}ms")

    # Salva resultados para uso pelo performance_monitor
    import json, os
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/fb_crescimento.json", "w") as f:
        json.dump(dados_crescimento, f, indent=2)

    print("\n✓ brute_force.py executado com sucesso.")
