"""
greedy.py
=========
Algoritmo Guloso — Dijkstra com heap (heapq)
para encontrar o caminho de menor custo de um hub de recursos
até todos os municípios de alto risco.

Variante escolhida: Dijkstra (opção C do enunciado)
Justificativa: O problema central é encontrar ROTAS MÍNIMAS a partir
de um ponto de despacho (hub de defesa civil), não conectar todos os
vértices com custo mínimo. Dijkstra é ideal pois:
  - Resolve fonte-única para todos os destinos em O((V + E) log V)
  - Integra naturalmente com a BST: consulta os municípios de maior
    risco e calcula a rota mais rápida até cada um deles
  - Usa heapq como fila de prioridade, conforme exigido

Razão de escolha local (prova informal de corretude):
    A cada passo, Dijkstra extrai o vértice não-visitado com menor
    dist acumulada. Como os pesos são não-negativos, relaxar esse
    vértice garante que sua distância não pode melhorar posteriormente
    (nenhuma aresta futura reduz o custo já encontrado). Isso é
    suficiente para garantir otimalidade em grafos com pesos ≥ 0.
"""

from __future__ import annotations
import heapq
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_structures import (
    Grafo, BinarySearchTree, construir_grafo_rs,
    construir_grafo_matopiba, construir_bst,
    nome_municipio, risco, custo,
)


# ---------------------------------------------------------------------------
# Dijkstra — caminho mínimo de fonte única
# ---------------------------------------------------------------------------

def dijkstra(grafo: Grafo, origem: int) -> tuple[dict[int, float], dict[int, int | None]]:
    """
    Algoritmo de Dijkstra usando heapq (fila de prioridade mínima).

    Parâmetros
    ----------
    grafo  : Grafo com adjacência ponderada
    origem : id do vértice de partida (hub de recursos)

    Retorna
    -------
    dist : dict  id → menor distância acumulada até esse vértice
    pred : dict  id → predecessor no caminho mínimo (None para origem)

    Complexidade
    ------------
    Tempo : O((V + E) log V)
    Espaço: O(V) para dist e pred; O(V) para o heap no pior caso
    """
    dist: dict[int, float] = {v: float("inf") for v in grafo.ids()}
    pred: dict[int, int | None] = {v: None for v in grafo.ids()}
    dist[origem] = 0.0

    # heap: (custo_acumulado, id_vertice)
    heap: list[tuple[float, int]] = [(0.0, origem)]
    visitados: set[int] = set()

    operacoes = {"relaxamentos": 0, "insercoes_heap": 1, "extraccoes_heap": 0}

    while heap:
        custo_u, u = heapq.heappop(heap)
        operacoes["extraccoes_heap"] += 1

        if u in visitados:
            continue
        visitados.add(u)

        for (v, peso) in grafo.vizinhos(u):
            operacoes["relaxamentos"] += 1
            novo_custo = custo_u + peso
            if novo_custo < dist[v]:
                dist[v] = novo_custo
                pred[v] = u
                heapq.heappush(heap, (novo_custo, v))
                operacoes["insercoes_heap"] += 1

    return dist, pred, operacoes


def reconstruir_caminho(pred: dict, origem: int, destino: int) -> list[int]:
    """
    Reconstrói o caminho mínimo de `origem` até `destino`
    usando o dicionário de predecessores.

    Retorna lista vazia se não existir caminho.
    """
    caminho: list[int] = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        if atual == origem:
            break
        atual = pred.get(atual)
        if atual not in pred and atual != origem:
            return []  # Sem caminho
    if not caminho or caminho[-1] != origem:
        return []
    return caminho[::-1]


# ---------------------------------------------------------------------------
# Integração com a BST — priorização por risco
# ---------------------------------------------------------------------------

def planejar_atendimento(
    grafo: Grafo,
    bst: BinarySearchTree,
    hub: int,
    limiar_risco: float = 0.75,
    orcamento_km: float = float("inf"),
) -> list[dict]:
    """
    Usa a BST para identificar municípios de alto risco (acima do
    limiar) e o Dijkstra para calcular a rota mínima a partir do hub.

    Retorna lista de planos de atendimento ordenados por prioridade
    (maior risco primeiro), filtrados pelo orçamento máximo de
    deslocamento.

    Parâmetros
    ----------
    hub          : id do município que serve como base de operações
    limiar_risco : municípios com risco ≥ limiar são priorizados
    orcamento_km : custo máximo tolerado para atendimento
    """
    # 1. Consulta a BST: municípios de alto risco
    municipios_risco = bst.buscar(limiar_risco, 1.0)

    if not municipios_risco:
        print(f"  Nenhum município com risco ≥ {limiar_risco}")
        return []

    print(f"  Municípios com risco ≥ {limiar_risco}:")
    for m in sorted(municipios_risco, key=lambda v: -risco(v)):
        print(f"    {nome_municipio(m):25s} risco={risco(m):.2f}")

    # 2. Dijkstra a partir do hub
    dist, pred, ops = dijkstra(grafo, hub)

    print(f"\n  Dijkstra a partir de '{grafo.vertices[hub][1]}':")
    print(f"    Relaxamentos   : {ops['relaxamentos']:,}")
    print(f"    Inserções heap : {ops['insercoes_heap']:,}")
    print(f"    Extrações heap : {ops['extraccoes_heap']:,}")

    # 3. Monta plano de atendimento
    planos = []
    for m in municipios_risco:
        vid = m[0]
        if vid == hub:
            continue
        distancia = dist[vid]
        if distancia > orcamento_km:
            continue

        caminho = reconstruir_caminho(pred, hub, vid)
        planos.append({
            "municipio": nome_municipio(m),
            "id": vid,
            "risco": risco(m),
            "custo_atendimento": custo(m),
            "distancia_hub": distancia,
            "caminho_ids": caminho,
            "caminho_nomes": [grafo.vertices[i][1] for i in caminho if i in grafo.vertices],
        })

    # Ordena: maior risco primeiro; empate → menor distância
    planos.sort(key=lambda p: (-p["risco"], p["distancia_hub"]))
    return planos


# ---------------------------------------------------------------------------
# Demonstração
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("ALGORITMO GULOSO (DIJKSTRA) — Global Solution 2026")
    print("=" * 65)

    # -----------------------------------------------------------------------
    # Cenário A — RS
    # -----------------------------------------------------------------------
    print("\n[1] Cenário A — RS (Enchentes 2024)")
    g_rs = construir_grafo_rs()
    bst_rs = construir_bst(g_rs)

    hub_rs = 4314902  # Porto Alegre
    print(f"\n  Hub de recursos: {g_rs.vertices[hub_rs][1]}")

    planos_rs = planejar_atendimento(
        grafo=g_rs,
        bst=bst_rs,
        hub=hub_rs,
        limiar_risco=0.77,
    )

    print(f"\n  Plano de Atendimento (ordenado por prioridade):")
    print(f"  {'Município':25s} {'Risco':>6} {'Distância':>10} {'Caminho'}")
    print(f"  {'-'*70}")
    for p in planos_rs:
        print(f"  {p['municipio']:25s} {p['risco']:>6.2f} "
              f"{p['distancia_hub']:>10.2f}h  "
              f"{' → '.join(p['caminho_nomes'])}")

    # Dijkstra completo — distâncias de Porto Alegre a todos
    print(f"\n  Distâncias mínimas de Porto Alegre a todos os municípios:")
    dist_rs, pred_rs, _ = dijkstra(g_rs, hub_rs)
    for vid in sorted(dist_rs.keys()):
        if vid == hub_rs:
            continue
        nome = g_rs.vertices[vid][1]
        d = dist_rs[vid]
        if d == float("inf"):
            print(f"    {nome:25s} → INALCANÇÁVEL")
        else:
            cam = reconstruir_caminho(pred_rs, hub_rs, vid)
            nomes_cam = [g_rs.vertices[i][1] for i in cam]
            print(f"    {nome:25s} → {d:.2f}h  ({' → '.join(nomes_cam)})")

    # -----------------------------------------------------------------------
    # Cenário B — MATOPIBA
    # -----------------------------------------------------------------------
    print("\n[2] Cenário B — MATOPIBA (Seca)")
    g_mat = construir_grafo_matopiba()
    bst_mat = construir_bst(g_mat)

    hub_mat = 1721000  # Palmas (TO) — hub logístico
    print(f"\n  Hub de recursos: {g_mat.vertices[hub_mat][1]}")

    planos_mat = planejar_atendimento(
        grafo=g_mat,
        bst=bst_mat,
        hub=hub_mat,
        limiar_risco=0.80,
        orcamento_km=1000,
    )

    print(f"\n  Plano de Atendimento (orçamento ≤ 1000km):")
    print(f"  {'Município':25s} {'Risco':>6} {'Distância':>10} {'Caminho'}")
    print(f"  {'-'*70}")
    for p in planos_mat:
        print(f"  {p['municipio']:25s} {p['risco']:>6.2f} "
              f"{p['distancia_hub']:>10.0f}km  "
              f"{' → '.join(p['caminho_nomes'])}")

    # -----------------------------------------------------------------------
    # Comparação FB × Greedy (via caminho único)
    # -----------------------------------------------------------------------
    print("\n[3] Comparação Força Bruta × Dijkstra")
    from brute_force import forca_bruta_caminhos
    import time

    origem_cmp, destino_cmp = 4314902, 4315602  # POA → Rio Grande

    t0 = time.perf_counter()
    res_fb = forca_bruta_caminhos(g_rs, origem_cmp, destino_cmp)
    t_fb = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    dist_dij, pred_dij, _ = dijkstra(g_rs, origem_cmp)
    cam_dij = reconstruir_caminho(pred_dij, origem_cmp, destino_cmp)
    t_dij = (time.perf_counter() - t0) * 1000

    custo_fb  = res_fb["melhor_custo"]
    custo_dij = dist_dij[destino_cmp]
    gap = abs(custo_dij - custo_fb) / custo_fb * 100 if custo_fb > 0 else 0

    print(f"  {'Algoritmo':15s} {'Custo':>10} {'Tempo':>10} {'Caminhos avaliados':>20}")
    print(f"  {'-'*60}")
    print(f"  {'Força Bruta':15s} {custo_fb:>10.2f} {t_fb:>9.2f}ms "
          f"{res_fb['avaliados']:>20,d}")
    print(f"  {'Dijkstra':15s} {custo_dij:>10.2f} {t_dij:>9.2f}ms {'1 (fonte única)':>20}")
    print(f"\n  Gap de otimalidade: {gap:.2f}%  "
          f"({'ótimo' if gap == 0 else 'subótimo'})")

    print("\n✓ greedy.py executado com sucesso.")
