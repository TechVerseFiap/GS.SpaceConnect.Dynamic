"""
performance_monitor.py
======================
Monitoramento de desempenho: tempo (perf_counter), memória
(tracemalloc) e contadores de operações para ambos os algoritmos
em diferentes tamanhos de instância.

Registra e exibe:
    - Tempo de execução (ms)
    - Memória alocada (MB)
    - Número de operações elementares
    - Escalabilidade empírica: curva N × tempo
"""

from __future__ import annotations
import time
import tracemalloc
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from data_structures import Grafo, criar_vertice, construir_bst
from brute_force import forca_bruta_caminhos
from greedy import dijkstra


# ---------------------------------------------------------------------------
# Gerador de grafos sintéticos com N vértices
# ---------------------------------------------------------------------------

def gerar_grafo_sintetico(n: int, denso: bool = False) -> tuple[Grafo, int, int]:
    """
    Gera um grafo sintético com N vértices.
    - denso=False: grafo esparso (cada vértice conectado a ~3 vizinhos)
    - denso=True : grafo completo
    Retorna (grafo, origem_id, destino_id).
    """
    import random
    random.seed(42)

    g = Grafo()
    ids = list(range(n))

    for i in ids:
        v = criar_vertice(
            i,
            f"Municipio_{i}",
            round(random.uniform(0.1, 0.99), 2),
            float(random.randint(100, 2000)),
            random.randint(5000, 1_500_000),
        )
        g.adicionar_vertice(v)

    if denso:
        for i in range(n):
            for j in range(i + 1, n):
                g.adicionar_aresta(i, j, round(random.uniform(0.5, 10.0), 2))
    else:
        # Garante conectividade com uma cadeia + arestas extras aleatórias
        for i in range(n - 1):
            g.adicionar_aresta(i, i + 1, round(random.uniform(0.5, 5.0), 2))
        extras = min(n * 2, n * (n - 1) // 2)
        arestas_existentes = {(i, i + 1) for i in range(n - 1)}
        tentativas = 0
        while extras > 0 and tentativas < n * n:
            u, v = random.sample(ids, 2)
            if u > v:
                u, v = v, u
            if (u, v) not in arestas_existentes:
                g.adicionar_aresta(u, v, round(random.uniform(0.5, 8.0), 2))
                arestas_existentes.add((u, v))
                extras -= 1
            tentativas += 1

    return g, ids[0], ids[-1]


# ---------------------------------------------------------------------------
# Benchmark individual
# ---------------------------------------------------------------------------

def benchmark_forca_bruta(n: int) -> dict:
    """Executa FB para um grafo de n vértices e retorna métricas."""
    g, origem, destino = gerar_grafo_sintetico(n, denso=True)

    tracemalloc.start()
    t0 = time.perf_counter()
    resultado = forca_bruta_caminhos(g, origem, destino)
    t1 = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algoritmo": "Força Bruta",
        "n": n,
        "tempo_ms": (t1 - t0) * 1000,
        "memoria_mb": pico / 1024 / 1024,
        "operacoes": resultado["chamadas"],
        "caminhos_avaliados": resultado["avaliados"],
        "custo_otimo": resultado["melhor_custo"],
    }


def benchmark_dijkstra(n: int) -> dict:
    """Executa Dijkstra para um grafo de n vértices e retorna métricas."""
    g, origem, destino = gerar_grafo_sintetico(n, denso=False)

    tracemalloc.start()
    t0 = time.perf_counter()
    dist, pred, ops = dijkstra(g, origem)
    t1 = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algoritmo": "Dijkstra (Guloso)",
        "n": n,
        "tempo_ms": (t1 - t0) * 1000,
        "memoria_mb": pico / 1024 / 1024,
        "operacoes": ops["relaxamentos"],
        "insercoes_heap": ops["insercoes_heap"],
        "custo_otimo": dist[destino],
    }


# ---------------------------------------------------------------------------
# Benchmark comparativo em múltiplos tamanhos
# ---------------------------------------------------------------------------

def rodar_benchmark_completo(
    tamanhos: list[int] = None,
    limite_fb: int = 12,
) -> dict:
    """
    Executa benchmarks de FB e Dijkstra para todos os tamanhos.
    FB é limitado ao máximo `limite_fb` para evitar travamento.

    Retorna dicionário com as listas de resultados.
    """
    if tamanhos is None:
        tamanhos = [5, 8, 10, 12, 20, 50, 100]

    resultados_fb = []
    resultados_dij = []

    print("\n" + "=" * 70)
    print(f"{'N':>5} | {'Algoritmo':20s} | {'Tempo (ms)':>12} | "
          f"{'Memória (MB)':>12} | {'Operações':>12}")
    print("-" * 70)

    for n in tamanhos:
        # Dijkstra — sempre
        r_dij = benchmark_dijkstra(n)
        resultados_dij.append(r_dij)
        print(f"{n:>5} | {'Dijkstra':20s} | {r_dij['tempo_ms']:>12.3f} | "
              f"{r_dij['memoria_mb']:>12.4f} | {r_dij['operacoes']:>12,d}")

        # Força Bruta — só até limite_fb
        if n <= limite_fb:
            r_fb = benchmark_forca_bruta(n)
            resultados_fb.append(r_fb)
            print(f"{n:>5} | {'Força Bruta':20s} | {r_fb['tempo_ms']:>12.3f} | "
                  f"{r_fb['memoria_mb']:>12.4f} | {r_fb['operacoes']:>12,d}")
        else:
            print(f"{n:>5} | {'Força Bruta':20s} | {'INVIÁVEL (N>12)':>12} | "
                  f"{'--':>12} | {'--':>12}")

    print("=" * 70)

    # Gap de otimalidade (somente para instâncias onde FB foi executado)
    print("\n[Gap de otimalidade FB × Dijkstra]")
    print(f"  {'N':>4} | {'Custo FB':>12} | {'Custo Dij':>12} | {'Gap %':>8}")
    print(f"  {'-'*45}")
    for r_fb in resultados_fb:
        n = r_fb["n"]
        r_dij_match = next((r for r in resultados_dij if r["n"] == n), None)
        if r_dij_match and r_fb["custo_otimo"] > 0:
            gap = abs(r_dij_match["custo_otimo"] - r_fb["custo_otimo"]) / r_fb["custo_otimo"] * 100
            print(f"  {n:>4} | {r_fb['custo_otimo']:>12.3f} | "
                  f"{r_dij_match['custo_otimo']:>12.3f} | {gap:>8.2f}%")

    print("\n  Nota: os grafos de FB e Dijkstra são diferentes (instâncias")
    print("  sintéticas independentes com mesma semente). Para comparação")
    print("  exata, veja a função comparar_mesmo_grafo() abaixo.")

    return {"forca_bruta": resultados_fb, "dijkstra": resultados_dij}


def comparar_mesmo_grafo(tamanhos_fb: list[int] = None) -> list[dict]:
    """
    Compara FB e Dijkstra no MESMO grafo para cada N ≤ 12.
    Retorna lista de dicts com gap de otimalidade exato.
    """
    if tamanhos_fb is None:
        tamanhos_fb = [4, 5, 6, 7, 8, 9, 10, 11, 12]

    comparacoes = []
    print("\n[Comparação no mesmo grafo]")
    print(f"  {'N':>4} | {'Custo FB':>10} | {'Custo Dij':>10} | "
          f"{'Gap %':>7} | {'Tempo FB (ms)':>14} | {'Tempo Dij (ms)':>14}")
    print(f"  {'-'*70}")

    for n in tamanhos_fb:
        g, origem, destino = gerar_grafo_sintetico(n, denso=True)

        # FB
        t0 = time.perf_counter()
        res_fb = forca_bruta_caminhos(g, origem, destino)
        t_fb = (time.perf_counter() - t0) * 1000

        # Dijkstra
        t0 = time.perf_counter()
        dist, _, _ = dijkstra(g, origem)
        t_dij = (time.perf_counter() - t0) * 1000

        custo_fb  = res_fb["melhor_custo"]
        custo_dij = dist[destino]

        if custo_fb > 0 and custo_fb != float("inf"):
            gap = abs(custo_dij - custo_fb) / custo_fb * 100
        else:
            gap = 0.0

        comparacoes.append({
            "n": n,
            "custo_fb": custo_fb,
            "custo_dijkstra": custo_dij,
            "gap_pct": gap,
            "tempo_fb_ms": t_fb,
            "tempo_dij_ms": t_dij,
        })

        print(f"  {n:>4} | {custo_fb:>10.3f} | {custo_dij:>10.3f} | "
              f"{gap:>7.2f}% | {t_fb:>14.3f} | {t_dij:>14.3f}")

    return comparacoes


# ---------------------------------------------------------------------------
# Demonstração
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("MONITORAMENTO DE DESEMPENHO — Global Solution 2026")
    print("=" * 65)

    # Benchmark completo
    resultados = rodar_benchmark_completo(
        tamanhos=[5, 8, 10, 12, 20, 50, 100],
        limite_fb=12,
    )

    # Comparação no mesmo grafo
    comparacoes = comparar_mesmo_grafo([4, 5, 6, 7, 8, 9, 10, 11, 12])

    # Salva resultados
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/benchmark_resultados.json", "w") as f:
        json.dump({
            "benchmark": resultados,
            "comparacoes": comparacoes,
        }, f, indent=2)

    print("\n  Resultados salvos em data/processed/benchmark_resultados.json")

    # Análise do cruzamento das curvas
    print("\n[Análise de viabilidade — Força Bruta]")
    for r in resultados["forca_bruta"]:
        n, t = r["n"], r["tempo_ms"]
        viavel = "✓" if t < 1000 else "✗ LENTO"
        print(f"  N={n:2d}: {t:8.2f}ms  {viavel}")

    print("\n  Conclusão: A Força Bruta se torna inviável a partir de N≈10–12")
    print("  em grafos completos. O Dijkstra permanece eficiente para N=100+")
    print("  graças à complexidade O((V+E) log V) vs O(n!) da FB.")

    print("\n✓ performance_monitor.py executado com sucesso.")
