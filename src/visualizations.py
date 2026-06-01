"""
visualizations.py
=================
Gera todas as figuras obrigatórias do projeto:

    1. Grafo de municípios com arestas e destaque das rotas mínimas
    2. Representação visual da BST (10–15 nós)
    3. Gráfico comparativo de desempenho: tempo × N
    4. Tabela de estruturas de dados
    5. Gráfico de gap de otimalidade FB × Greedy
"""

from __future__ import annotations
import os
import sys
import time
import json

import matplotlib
matplotlib.use("Agg")  # Sem display — salva em arquivo
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

sys.path.insert(0, os.path.dirname(__file__))
from data_structures import (
    Grafo, BinarySearchTree, Node,
    construir_grafo_rs, construir_grafo_matopiba,
    construir_bst, nome_municipio, risco, id_municipio,
)
from greedy import dijkstra, reconstruir_caminho
from performance_monitor import (
    rodar_benchmark_completo, comparar_mesmo_grafo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUTPUT_DIR = "report/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def salvar(fig: plt.Figure, nome: str) -> str:
    caminho = os.path.join(OUTPUT_DIR, nome)
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figura salva: {caminho}")
    return caminho


# ---------------------------------------------------------------------------
# Figura 1 — Grafo de municípios com rotas mínimas destacadas
# ---------------------------------------------------------------------------

def figura_grafo_rs() -> str:
    """
    Visualiza o grafo do RS com networkx + matplotlib.
    Destaca a Árvore de Caminhos Mínimos a partir de Porto Alegre.
    """
    g = construir_grafo_rs()
    hub = 4314902  # Porto Alegre

    # Calcula caminhos mínimos
    dist, pred, _ = dijkstra(g, hub)

    # Monta grafo networkx
    G = nx.Graph()
    for vid, v in g.vertices.items():
        G.add_node(vid, label=nome_municipio(v), risco=risco(v))
    for u, vizinhos in g.adj.items():
        for v, peso in vizinhos:
            if u < v:
                G.add_edge(u, v, weight=round(peso, 2))

    # Arestas do caminho mínimo (predecessores)
    arestas_mst = set()
    for v, p in pred.items():
        if p is not None:
            arestas_mst.add((min(p, v), max(p, v)))

    # Layout
    pos = nx.spring_layout(G, seed=42, k=2.5)

    # Cores dos nós pelo risco
    riscos = [g.vertices[n]["risco"] if isinstance(g.vertices[n], dict)
              else g.vertices[n][2] for n in G.nodes()]
    # risco é o índice 2 da tupla
    riscos = [g.vertices[n][2] for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(14, 9))

    # Arestas normais
    arestas_normais = [(u, v) for u, v in G.edges()
                       if (min(u, v), max(u, v)) not in arestas_mst]
    nx.draw_networkx_edges(G, pos, edgelist=arestas_normais,
                           alpha=0.25, edge_color="#999999", width=1, ax=ax)

    # Arestas da MST (caminhos mínimos)
    arestas_dest = [(u, v) for u, v in G.edges()
                    if (min(u, v), max(u, v)) in arestas_mst]
    nx.draw_networkx_edges(G, pos, edgelist=arestas_dest,
                           edge_color="#E74C3C", width=2.5, ax=ax,
                           label="Rota mínima (Dijkstra)")

    # Nós
    sc = nx.draw_networkx_nodes(G, pos, node_size=600,
                                node_color=riscos, cmap="YlOrRd",
                                vmin=0, vmax=1, ax=ax)

    # Rótulos
    labels = {n: g.vertices[n][1].split()[0] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)

    # Pesos das arestas
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels,
                                 font_size=6, alpha=0.7, ax=ax)

    plt.colorbar(sc, ax=ax, label="Índice de Risco", shrink=0.6)
    ax.set_title(
        "Figura 1 — Grafo RS: Municípios e Rotas Mínimas (Dijkstra)\n"
        "Vértices = municípios afetados pelas enchentes 2024 | "
        "Cor = índice de risco | Arestas vermelhas = caminhos mínimos a partir de Porto Alegre",
        fontsize=10, pad=12,
    )
    ax.legend(handles=[
        mpatches.Patch(color="#E74C3C", label="Rota mínima (Dijkstra)"),
        mpatches.Patch(color="#999999", label="Aresta normal"),
    ], loc="lower left", fontsize=8)
    ax.text(0.01, -0.06,
            "Fonte: Dados sintéticos baseados na malha viária DNIT e Defesa Civil RS. "
            "Arestas vermelhas representam a árvore de caminhos mínimos (SPT) "
            "calculada pelo algoritmo de Dijkstra a partir de Porto Alegre. "
            "A cor dos nós indica o índice de risco de inundação.",
            transform=ax.transAxes, fontsize=7, wrap=True,
            verticalalignment="top", style="italic")
    ax.axis("off")
    return salvar(fig, "fig1_grafo_rs.png")


def figura_grafo_matopiba() -> str:
    """Visualiza o grafo MATOPIBA com risco de seca."""
    g = construir_grafo_matopiba()
    hub = 1721000  # Palmas

    dist, pred, _ = dijkstra(g, hub)
    G = nx.Graph()
    for vid, v in g.vertices.items():
        G.add_node(vid, label=nome_municipio(v))
    for u, vizinhos in g.adj.items():
        for v, peso in vizinhos:
            if u < v:
                G.add_edge(u, v, weight=int(peso))

    arestas_mst = {(min(p, v), max(p, v)) for v, p in pred.items() if p}
    pos = nx.spring_layout(G, seed=7, k=3)
    riscos = [g.vertices[n][2] for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(12, 8))
    arestas_norm = [(u, v) for u, v in G.edges()
                    if (min(u, v), max(u, v)) not in arestas_mst]
    arestas_dest = [(u, v) for u, v in G.edges()
                    if (min(u, v), max(u, v)) in arestas_mst]

    nx.draw_networkx_edges(G, pos, edgelist=arestas_norm,
                           alpha=0.25, edge_color="#aaaaaa", width=1, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=arestas_dest,
                           edge_color="#2980B9", width=2.5, ax=ax)
    sc = nx.draw_networkx_nodes(G, pos, node_size=600,
                                node_color=riscos, cmap="Oranges",
                                vmin=0, vmax=1, ax=ax)
    labels = {n: g.vertices[n][1][:12] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels,
                                 font_size=6, alpha=0.7, ax=ax)
    plt.colorbar(sc, ax=ax, label="Índice de Risco (Seca)", shrink=0.6)
    ax.set_title(
        "Figura 1b — Grafo MATOPIBA: Risco de Seca e Rotas de Atendimento (Dijkstra)\n"
        "Vértices = municípios MA/TO/PI/BA | Cor = risco derivado de NDVI+precipitação | "
        "Arestas azuis = caminhos mínimos a partir de Palmas (TO)",
        fontsize=9, pad=12,
    )
    ax.text(0.01, -0.06,
            "Fonte: Dados sintéticos baseados em NDVI MODIS/NASA e INMET. "
            "O peso das arestas representa a distância rodoviária estimada (km). "
            "As arestas azuis correspondem à árvore de caminhos mínimos calculada "
            "pelo Dijkstra com hub em Palmas (TO).",
            transform=ax.transAxes, fontsize=7, wrap=True,
            verticalalignment="top", style="italic")
    ax.axis("off")
    return salvar(fig, "fig1b_grafo_matopiba.png")


# ---------------------------------------------------------------------------
# Figura 2 — Visualização da BST
# ---------------------------------------------------------------------------

def _posicionar_bst(no: Node, x: float, y: float, dx: float,
                    posicoes: dict, nos: list) -> None:
    if no is None:
        return
    posicoes[id(no)] = (x, y)
    nos.append(no)
    _posicionar_bst(no.esquerda, x - dx, y - 1.2, dx / 1.8, posicoes, nos)
    _posicionar_bst(no.direita,  x + dx, y - 1.2, dx / 1.8, posicoes, nos)


def _desenhar_arestas_bst(ax: plt.Axes, no: Node, posicoes: dict) -> None:
    if no is None:
        return
    if no.esquerda:
        x0, y0 = posicoes[id(no)]
        x1, y1 = posicoes[id(no.esquerda)]
        ax.plot([x0, x1], [y0, y1], "k-", linewidth=1.2, zorder=1)
        _desenhar_arestas_bst(ax, no.esquerda, posicoes)
    if no.direita:
        x0, y0 = posicoes[id(no)]
        x1, y1 = posicoes[id(no.direita)]
        ax.plot([x0, x1], [y0, y1], "k-", linewidth=1.2, zorder=1)
        _desenhar_arestas_bst(ax, no.direita, posicoes)


def figura_bst(tamanho: int = 12) -> str:
    """
    Visualiza a BST com 10–15 nós construída a partir do grafo RS.
    """
    from data_structures import criar_vertice
    import random
    random.seed(10)

    # Usa somente os primeiros `tamanho` vértices do RS
    g = construir_grafo_rs()
    bst = BinarySearchTree()
    ids = list(g.vertices.keys())[:tamanho]
    random.shuffle(ids)
    for vid in ids:
        bst.inserir(g.vertices[vid])

    posicoes: dict = {}
    nos: list = []
    _posicionar_bst(bst.raiz, 0, 0, 4.0, posicoes, nos)

    fig, ax = plt.subplots(figsize=(14, 8))
    _desenhar_arestas_bst(ax, bst.raiz, posicoes)

    for no in nos:
        x, y = posicoes[id(no)]
        r = no.chave
        cor = plt.cm.YlOrRd(r)
        circle = plt.Circle((x, y), 0.4, color=cor, zorder=2, linewidth=1.5,
                             edgecolor="#333333")
        ax.add_patch(circle)
        ax.text(x, y + 0.05, f"{r:.2f}", ha="center", va="center",
                fontsize=7.5, fontweight="bold", zorder=3)
        nome_curto = nome_municipio(no.vertice).split()[0][:8]
        ax.text(x, y - 0.65, nome_curto, ha="center", va="center",
                fontsize=6, zorder=3, color="#333333")

    # Destaque da raiz
    xr, yr = posicoes[id(bst.raiz)]
    ax.text(xr, yr + 0.65, "RAIZ", ha="center", fontsize=8,
            color="#E74C3C", fontweight="bold")

    ax.set_xlim(min(x for x, y in posicoes.values()) - 1,
                max(x for x, y in posicoes.values()) + 1)
    ax.set_ylim(min(y for x, y in posicoes.values()) - 1.5,
                max(y for x, y in posicoes.values()) + 1.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Legenda de cores
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(0, 1))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Índice de Risco", shrink=0.5,
                 fraction=0.02, pad=0.02)

    ax.set_title(
        f"Figura 2 — BST de Municípios por Índice de Risco ({tamanho} nós)\n"
        f"Cada nó exibe o índice de risco | Propriedade BST: r_esq < r_pai ≤ r_dir | "
        f"Altura={bst.altura()} | {bst.balanceamento()}",
        fontsize=9, pad=12,
    )
    ax.text(0.01, 0.01,
            "Fonte: BST construída sobre municípios do RS afetados pelas enchentes de 2024. "
            f"A chave de ordenação é o índice de risco ambiental (float [0,1]). "
            f"A altura da árvore é {bst.altura()}, indicando o custo de busca O(h). "
            "A cor dos nós segue a escala de risco: amarelo (baixo) → vermelho (alto).",
            transform=ax.transAxes, fontsize=7, style="italic",
            verticalalignment="bottom",
        )
    return salvar(fig, "fig2_bst.png")


# ---------------------------------------------------------------------------
# Figura 3 — Desempenho: tempo × N
# ---------------------------------------------------------------------------

def figura_desempenho() -> str:
    """
    Gráfico comparativo de tempo de execução × N para FB e Dijkstra.
    """
    print("\n  Rodando benchmarks para figura de desempenho...")
    resultados = rodar_benchmark_completo(
        tamanhos=[5, 8, 10, 20, 50, 100],
        limite_fb=10,
    )

    fb  = resultados["forca_bruta"]
    dij = resultados["dijkstra"]

    ns_fb  = [r["n"] for r in fb]
    ts_fb  = [r["tempo_ms"] for r in fb]
    ns_dij = [r["n"] for r in dij]
    ts_dij = [r["tempo_ms"] for r in dij]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ns_fb,  ts_fb,  "o-r", linewidth=2, markersize=7,
            label="Força Bruta O(n!)")
    ax.plot(ns_dij, ts_dij, "s--b", linewidth=2, markersize=7,
            label="Dijkstra O((V+E) log V)")

    # Anotação do cruzamento
    ax.axvline(x=12, color="gray", linestyle=":", alpha=0.6)
    ax.text(12.3, max(ts_fb) * 0.8, "N≈12\nFB inviável →",
            fontsize=8, color="gray")

    ax.set_xlabel("Número de vértices (N)", fontsize=11)
    ax.set_ylabel("Tempo de execução (ms)", fontsize=11)
    ax.set_title(
        "Figura 3 — Desempenho: Tempo de Execução × N\n"
        "Força Bruta vs Dijkstra (Guloso) — escala linear",
        fontsize=11,
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.text(0.01, -0.12,
            "Fonte: Benchmarks com grafos sintéticos completos (FB) e esparsos (Dijkstra). "
            "A Força Bruta apresenta crescimento fatorial (explosão combinatória) e se torna "
            "inviável a partir de N≈10–12 vértices. O Dijkstra permanece sub-milissegundo "
            "até N=100, demonstrando a superioridade do algoritmo guloso em instâncias reais.",
            transform=ax.transAxes, fontsize=7, style="italic",
            verticalalignment="top",
        )
    return salvar(fig, "fig3_desempenho.png")


def figura_desempenho_log() -> str:
    """Versão em escala log-log para melhor visualização."""
    resultados = rodar_benchmark_completo(
        tamanhos=[5, 8, 10, 20, 50, 100],
        limite_fb=10,
    )
    fb  = resultados["forca_bruta"]
    dij = resultados["dijkstra"]

    ns_fb  = [r["n"] for r in fb]
    ts_fb  = [r["tempo_ms"] for r in fb]
    ns_dij = [r["n"] for r in dij]
    ts_dij = [r["tempo_ms"] for r in dij]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(ns_fb,  ts_fb,  "o-r", linewidth=2, markersize=7,
                label="Força Bruta O(n!)")
    ax.semilogy(ns_dij, ts_dij, "s--b", linewidth=2, markersize=7,
                label="Dijkstra O((V+E) log V)")

    ax.set_xlabel("Número de vértices (N)", fontsize=11)
    ax.set_ylabel("Tempo de execução (ms) — escala log", fontsize=11)
    ax.set_title(
        "Figura 3b — Desempenho (escala log): Força Bruta vs Dijkstra",
        fontsize=11,
    )
    ax.legend(fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    ax.text(0.01, -0.12,
            "Escala logarítmica no eixo Y. A inclinação acentuada da curva da Força Bruta "
            "confirma o crescimento super-exponencial do número de caminhos avaliados. "
            "O Dijkstra mantém crescimento quase plano, evidenciando sua eficiência prática.",
            transform=ax.transAxes, fontsize=7, style="italic",
            verticalalignment="top",
        )
    return salvar(fig, "fig3b_desempenho_log.png")


# ---------------------------------------------------------------------------
# Figura 4 — Tabela de estruturas de dados
# ---------------------------------------------------------------------------

def figura_tabela_estruturas() -> str:
    """
    Tabela visual das estruturas de dados utilizadas no projeto.
    """
    dados = [
        ("Lista (list)",     "Adjacência do grafo;\nresultados de caminho",      "O(V+E) espaço;\nO(deg) iteração"),
        ("Tupla (tuple)",    "Vértice imutável\n(id, nome, risco, custo, pop)",  "O(1) acesso;\nSegurança de dados"),
        ("Dicionário (dict)","Adjacência ponderada;\ncustos e predecessores",    "O(1) médio lookup;\nO(V) espaço"),
        ("Conjunto (set)",   "Visitados em BFS/DFS;\nfronteira do Guloso",       "O(1) pertencimento;\nO(V) espaço"),
        ("Heap (heapq)",     "Fila de prioridade\nno Dijkstra",                  "O(log V) push/pop;\nO(V) espaço"),
        ("BST (classes)",    "Municípios por risco;\nbusca em intervalo",        "O(log n) busca;\nO(n) espaço"),
        ("Grafo (dict+list)","Rede de municípios\ne rotas ponderadas",           "O(V+E) espaço;\nO(deg) vizinhos"),
        ("Deque (deque)",    "Fila para BFS;\nprocessamento FIFO",               "O(1) append/pop;\nO(V) espaço"),
    ]

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.axis("off")

    colunas = ["Estrutura", "Uso no Sistema", "Complexidade"]
    table = ax.table(
        cellText=dados,
        colLabels=colunas,
        cellLoc="center",
        loc="center",
        colWidths=[0.22, 0.42, 0.30],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 2.2)

    # Estilo do cabeçalho
    for j in range(len(colunas)):
        table[(0, j)].set_facecolor("#2C3E50")
        table[(0, j)].set_text_props(color="white", fontweight="bold")

    # Linhas alternadas
    cores = ["#EAF2FF", "#FFFFFF"]
    for i in range(1, len(dados) + 1):
        for j in range(len(colunas)):
            table[(i, j)].set_facecolor(cores[i % 2])

    ax.set_title(
        "Figura 4 — Tabela de Estruturas de Dados Utilizadas\n"
        "Justificativa de uso e complexidade em cada módulo do sistema",
        fontsize=11, pad=20,
    )
    ax.text(0.01, 0.01,
            "Fonte: Elaboração própria. Cada estrutura foi selecionada considerando "
            "o trade-off entre complexidade de tempo e espaço para a operação dominante "
            "em cada módulo. A lista de adjacência é preferível à matriz para grafos esparsos "
            "(O(V+E) vs O(V²)). A BST permite consultas por intervalo de risco em O(k+log n).",
            transform=ax.transAxes, fontsize=7, style="italic",
            verticalalignment="bottom",
        )
    return salvar(fig, "fig4_tabela_estruturas.png")


# ---------------------------------------------------------------------------
# Figura 5 — Gap de otimalidade
# ---------------------------------------------------------------------------

def figura_gap_otimalidade() -> str:
    """
    Gráfico do gap percentual entre FB (ótimo) e Dijkstra em função de N.
    """
    print("\n  Calculando comparações para figura de gap...")
    comparacoes = comparar_mesmo_grafo([4, 5, 6, 7, 8, 9, 10])

    ns   = [c["n"] for c in comparacoes]
    gaps = [c["gap_pct"] for c in comparacoes]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Gap %
    axes[0].bar(ns, gaps, color=["#2ECC71" if g < 1 else "#E74C3C" for g in gaps],
                edgecolor="black", linewidth=0.8)
    axes[0].axhline(y=0, color="black", linewidth=0.8)
    axes[0].set_xlabel("N (número de vértices)", fontsize=11)
    axes[0].set_ylabel("Gap de otimalidade (%)", fontsize=11)
    axes[0].set_title("Gap: Dijkstra vs Força Bruta", fontsize=11)
    axes[0].set_xticks(ns)
    axes[0].grid(True, axis="y", alpha=0.3)
    for x, g in zip(ns, gaps):
        axes[0].text(x, g + 0.05, f"{g:.1f}%", ha="center", fontsize=8)

    # Tempo
    ts_fb  = [c["tempo_fb_ms"] for c in comparacoes]
    ts_dij = [c["tempo_dij_ms"] for c in comparacoes]

    axes[1].plot(ns, ts_fb,  "o-r", linewidth=2, markersize=7,
                 label="Força Bruta")
    axes[1].plot(ns, ts_dij, "s--b", linewidth=2, markersize=7,
                 label="Dijkstra")
    axes[1].set_xlabel("N (número de vértices)", fontsize=11)
    axes[1].set_ylabel("Tempo (ms)", fontsize=11)
    axes[1].set_title("Tempo de execução (mesmo grafo)", fontsize=11)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(
        "Figura 5 — Gap de Otimalidade e Tempo de Execução: Força Bruta × Dijkstra\n"
        "Instâncias idênticas — grafos completos com mesma semente aleatória",
        fontsize=11,
    )
    fig.text(0.01, -0.04,
             "Fonte: Comparações realizadas no mesmo grafo sintético completo (denso) "
             "para garantir equivalência. Um gap de 0% confirma que Dijkstra é ótimo "
             "para grafos com pesos não-negativos. Gaps positivos podem ocorrer quando "
             "há múltiplos caminhos de custo idêntico (empates na escolha do predecessor). "
             "O painel direito demonstra a inviabilidade da FB a partir de N≈10.",
             fontsize=7, style="italic",
         )
    plt.tight_layout()
    return salvar(fig, "fig5_gap_otimalidade.png")


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("VISUALIZAÇÕES — Global Solution 2026")
    print("=" * 65)

    os.makedirs("report/figures", exist_ok=True)

    print("\n[1] Gerando Figura 1 — Grafo RS...")
    figura_grafo_rs()

    print("\n[2] Gerando Figura 1b — Grafo MATOPIBA...")
    figura_grafo_matopiba()

    print("\n[3] Gerando Figura 2 — BST...")
    figura_bst(tamanho=12)

    print("\n[4] Gerando Figura 3 — Desempenho...")
    figura_desempenho()
    figura_desempenho_log()

    print("\n[5] Gerando Figura 4 — Tabela de Estruturas...")
    figura_tabela_estruturas()

    print("\n[6] Gerando Figura 5 — Gap de Otimalidade...")
    figura_gap_otimalidade()

    print("\n✓ Todas as figuras salvas em report/figures/")
