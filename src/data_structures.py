"""
data_structures.py
==================
Implementação das estruturas de dados do sistema de monitoramento
de riscos ambientais.

Estruturas implementadas:
    - Tupla: vértice (id, nome, risco, custo, população)
    - Dicionário de listas de adjacência: grafo de municípios
    - Node + BinarySearchTree: BST por índice de risco
    - heapq: fila de prioridade (usado pelo Greedy)
    - set: controle de visitados (BFS/DFS)
    - deque: fila para BFS
"""

from __future__ import annotations
from collections import deque
import heapq
import json
import pickle
from typing import Optional


# ---------------------------------------------------------------------------
# 1. VÉRTICE — tupla imutável
# ---------------------------------------------------------------------------
# vertice = (id_municipio, nome, indice_risco, custo_atendimento, populacao)
#
# Exemplo real (RS):
#   v = (4314902, 'Porto Alegre', 0.72, 1850.0, 1400000)
# ---------------------------------------------------------------------------

def criar_vertice(id_municipio: int, nome: str, indice_risco: float,
                  custo_atendimento: float, populacao: int) -> tuple:
    """Retorna um vértice como tupla imutável."""
    return (id_municipio, nome, indice_risco, custo_atendimento, populacao)


def id_municipio(v: tuple) -> int:       return v[0]
def nome_municipio(v: tuple) -> str:     return v[1]
def risco(v: tuple) -> float:            return v[2]
def custo(v: tuple) -> float:            return v[3]
def populacao(v: tuple) -> int:          return v[4]


# ---------------------------------------------------------------------------
# 2. GRAFO — dicionário de listas de adjacência
# ---------------------------------------------------------------------------
# grafo = { id_vertice: [(vizinho_id, peso), ...] }
#
# Justificativa de representação:
#   - Lista de adjacência: O(V + E) espaço vs O(V²) da matriz.
#   - Para grafos esparsos (municípios têm poucos vizinhos), a lista é
#     mais eficiente em memória e mais rápida para iterar os vizinhos.
#   - A matriz seria preferível apenas se V fosse pequeno e se precisássemos
#     verificar a existência de aresta em O(1) com frequência.
# ---------------------------------------------------------------------------

class Grafo:
    """
    Grafo ponderado não-direcionado representado como dicionário de
    listas de adjacência.

    Atributos
    ---------
    vertices : dict[int, tuple]
        Mapeia id_municipio → tupla de atributos do vértice.
    adj : dict[int, list[tuple[int, float]]]
        Mapeia id_municipio → lista de (vizinho_id, peso).
    """

    def __init__(self):
        self.vertices: dict[int, tuple] = {}          # id → vertice
        self.adj: dict[int, list] = {}                # id → [(viz, peso)]

    # ---- construção --------------------------------------------------------

    def adicionar_vertice(self, vertice: tuple) -> None:
        """Adiciona vértice ao grafo (sem arestas)."""
        vid = id_municipio(vertice)
        self.vertices[vid] = vertice
        if vid not in self.adj:
            self.adj[vid] = []

    def adicionar_aresta(self, u: int, v: int, peso: float) -> None:
        """Adiciona aresta bidirecional entre u e v com o peso dado."""
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, peso))
        self.adj[v].append((u, peso))

    # ---- consultas básicas -------------------------------------------------

    def vizinhos(self, u: int) -> list:
        """Retorna lista de (vizinho_id, peso) para o vértice u."""
        return self.adj.get(u, [])

    def num_vertices(self) -> int:
        return len(self.vertices)

    def num_arestas(self) -> int:
        return sum(len(viz) for viz in self.adj.values()) // 2

    def ids(self) -> list:
        """Retorna lista de todos os ids de vértices."""
        return list(self.vertices.keys())

    # ---- travessias --------------------------------------------------------

    def bfs(self, origem: int) -> list[int]:
        """
        Busca em largura (BFS) a partir da origem.
        Usa deque como fila e set para controle de visitados.

        Retorna a lista de ids na ordem de visita.
        """
        visitados: set[int] = set()
        fila: deque[int] = deque([origem])
        visitados.add(origem)
        ordem: list[int] = []

        while fila:
            u = fila.popleft()
            ordem.append(u)
            for (v, _) in self.adj.get(u, []):
                if v not in visitados:
                    visitados.add(v)
                    fila.append(v)
        return ordem

    def dfs(self, origem: int) -> list[int]:
        """
        Busca em profundidade (DFS) a partir da origem.
        Usa conjunto para controle de visitados e evitar ciclos.

        Retorna a lista de ids na ordem de visita.
        """
        visitados: set[int] = set()
        ordem: list[int] = []

        def _dfs(u: int):
            visitados.add(u)
            ordem.append(u)
            for (v, _) in self.adj.get(u, []):
                if v not in visitados:
                    _dfs(v)

        _dfs(origem)
        return ordem

    # ---- serialização ------------------------------------------------------

    def salvar_json(self, caminho: str) -> None:
        dados = {
            "vertices": {str(k): list(v) for k, v in self.vertices.items()},
            "adj": {str(k): v for k, v in self.adj.items()},
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def salvar_pickle(self, caminho: str) -> None:
        with open(caminho, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def carregar_json(caminho: str) -> "Grafo":
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        g = Grafo()
        for k, v in dados["vertices"].items():
            g.vertices[int(k)] = tuple(v)
        for k, viz in dados["adj"].items():
            g.adj[int(k)] = [(int(v), p) for v, p in viz]
        return g

    def __repr__(self) -> str:
        return (f"Grafo(vertices={self.num_vertices()}, "
                f"arestas={self.num_arestas()})")


# ---------------------------------------------------------------------------
# 3. BST — Árvore Binária de Busca por índice de risco
# ---------------------------------------------------------------------------
# Chave de ordenação: indice_risco (float)
# Regra BST: risco_esquerda < risco_pai ≤ risco_direita
# ---------------------------------------------------------------------------

class Node:
    """Nó da BST. Armazena o vértice completo (tupla)."""

    def __init__(self, vertice: tuple):
        self.vertice: tuple = vertice            # (id, nome, risco, custo, pop)
        self.esquerda: Optional[Node] = None
        self.direita: Optional[Node] = None

    @property
    def chave(self) -> float:
        return risco(self.vertice)

    def __repr__(self) -> str:
        return (f"Node(id={id_municipio(self.vertice)}, "
                f"nome={nome_municipio(self.vertice)}, "
                f"risco={self.chave:.2f})")


class BinarySearchTree:
    """
    BST de municípios ordenada por índice de risco.

    Operações:
        inserir, buscar (intervalo), percurso_in_order, altura, remover
    """

    def __init__(self):
        self.raiz: Optional[Node] = None
        self._tamanho: int = 0

    # ---- inserção ----------------------------------------------------------

    def inserir(self, vertice: tuple) -> None:
        """Insere um município mantendo a propriedade BST."""
        self.raiz = self._inserir(self.raiz, vertice)
        self._tamanho += 1

    def _inserir(self, no: Optional[Node], vertice: tuple) -> Node:
        if no is None:
            return Node(vertice)
        r = risco(vertice)
        if r < no.chave:
            no.esquerda = self._inserir(no.esquerda, vertice)
        else:
            no.direita = self._inserir(no.direita, vertice)
        return no

    # ---- busca por intervalo -----------------------------------------------

    def buscar(self, r_min: float, r_max: float) -> list[tuple]:
        """
        Retorna todos os municípios com índice de risco em [r_min, r_max].
        Complexidade: O(k + log n) onde k é o número de resultados.
        """
        resultado: list[tuple] = []
        self._buscar(self.raiz, r_min, r_max, resultado)
        return resultado

    def _buscar(self, no: Optional[Node], r_min: float, r_max: float,
                resultado: list) -> None:
        if no is None:
            return
        if r_min < no.chave:
            self._buscar(no.esquerda, r_min, r_max, resultado)
        if r_min <= no.chave <= r_max:
            resultado.append(no.vertice)
        if r_max >= no.chave:
            self._buscar(no.direita, r_min, r_max, resultado)

    # ---- percurso in-order -------------------------------------------------

    def percurso_in_order(self) -> list[tuple]:
        """
        Retorna municípios em ordem crescente de risco.
        Útil para priorização: o último elemento é o município
        de maior risco e deve ser atendido primeiro.
        """
        resultado: list[tuple] = []
        self._in_order(self.raiz, resultado)
        return resultado

    def _in_order(self, no: Optional[Node], resultado: list) -> None:
        if no is None:
            return
        self._in_order(no.esquerda, resultado)
        resultado.append(no.vertice)
        self._in_order(no.direita, resultado)

    # ---- altura ------------------------------------------------------------

    def altura(self) -> int:
        """
        Calcula a altura da árvore.
        Árvore balanceada: O(log n). Pior caso (degenerada): O(n).
        """
        return self._altura(self.raiz)

    def _altura(self, no: Optional[Node]) -> int:
        if no is None:
            return 0
        return 1 + max(self._altura(no.esquerda), self._altura(no.direita))

    def balanceamento(self) -> str:
        """Avalia o balanceamento da árvore."""
        h = self.altura()
        n = self._tamanho
        import math
        ideal = math.ceil(math.log2(n + 1)) if n > 0 else 0
        fator = h / ideal if ideal > 0 else float('inf')
        if fator <= 1.5:
            return f"BEM BALANCEADA (h={h}, ideal≈{ideal}, fator={fator:.2f})"
        elif fator <= 2.5:
            return f"MODERADAMENTE DESBALANCEADA (h={h}, ideal≈{ideal}, fator={fator:.2f})"
        else:
            return f"DESBALANCEADA (h={h}, ideal≈{ideal}, fator={fator:.2f})"

    # ---- remoção -----------------------------------------------------------

    def remover(self, id_mun: int) -> None:
        """Remove o nó com o município de id dado."""
        self.raiz, removido = self._remover_por_id(self.raiz, id_mun)
        if removido:
            self._tamanho -= 1

    def _remover_por_id(self, no: Optional[Node], id_mun: int):
        """Percorre a árvore em busca do id e remove; retorna (novo_no, removido)."""
        if no is None:
            return None, False

        if id_municipio(no.vertice) == id_mun:
            # Caso 1: folha
            if no.esquerda is None and no.direita is None:
                return None, True
            # Caso 2: só filho direito
            if no.esquerda is None:
                return no.direita, True
            # Caso 3: só filho esquerdo
            if no.direita is None:
                return no.esquerda, True
            # Caso 4: dois filhos — substitui pelo menor da subárvore direita
            sucessor = self._minimo(no.direita)
            no.vertice = sucessor.vertice
            no.direita, _ = self._remover_por_id(no.direita,
                                                  id_municipio(sucessor.vertice))
            return no, True

        # Busca em ambos os ramos (a remoção por id não segue a chave de risco)
        no.esquerda, rem_esq = self._remover_por_id(no.esquerda, id_mun)
        if not rem_esq:
            no.direita, rem_dir = self._remover_por_id(no.direita, id_mun)
            return no, rem_dir
        return no, True

    def _minimo(self, no: Node) -> Node:
        while no.esquerda is not None:
            no = no.esquerda
        return no

    # ---- utilitários -------------------------------------------------------

    def __len__(self) -> int:
        return self._tamanho

    def __repr__(self) -> str:
        return f"BinarySearchTree(tamanho={self._tamanho}, altura={self.altura()})"

    def imprimir_arvore(self, no: Optional[Node] = None, nivel: int = 0,
                        prefixo: str = "Raiz: ") -> None:
        """Imprime a árvore de forma visual no terminal."""
        if no is None and nivel == 0:
            no = self.raiz
        if no is None:
            return
        print(" " * (nivel * 4) + prefixo +
              f"{nome_municipio(no.vertice)} (risco={no.chave:.2f})")
        if no.esquerda or no.direita:
            if no.esquerda:
                self.imprimir_arvore(no.esquerda, nivel + 1, "E── ")
            else:
                print(" " * ((nivel + 1) * 4) + "E── [vazio]")
            if no.direita:
                self.imprimir_arvore(no.direita, nivel + 1, "D── ")
            else:
                print(" " * ((nivel + 1) * 4) + "D── [vazio]")


# ---------------------------------------------------------------------------
# 4. DADOS DE EXEMPLO — Cenário A (RS) e Cenário B (MATOPIBA)
# ---------------------------------------------------------------------------

def construir_grafo_rs() -> Grafo:
    """
    Cenário A: subgrafo simplificado de municípios do RS afetados
    pelas enchentes de 2024. Dados sintéticos baseados na malha DNIT.

    Peso das arestas = tempo de deslocamento estimado (horas).
    """
    g = Grafo()

    vertices_rs = [
        criar_vertice(4314902, "Porto Alegre",    0.72, 1850.0, 1400000),
        criar_vertice(4300406, "Alegrete",        0.55, 620.0,  78000),
        criar_vertice(4307005, "Caxias do Sul",   0.48, 780.0,  530000),
        criar_vertice(4316808, "São Leopoldo",    0.81, 540.0,  230000),
        criar_vertice(4312401, "Lajeado",         0.91, 310.0,  82000),
        criar_vertice(4310108, "Guaíba",          0.68, 295.0,  100000),
        criar_vertice(4306403, "Canoas",          0.77, 720.0,  350000),
        criar_vertice(4318705, "Venâncio Aires",  0.85, 270.0,  73000),
        criar_vertice(4320404, "Encantado",       0.93, 180.0,  21000),
        criar_vertice(4322509, "Santa Cruz do S.",0.60, 340.0,  130000),
        criar_vertice(4303004, "Bento Gonçalves", 0.42, 410.0,  120000),
        criar_vertice(4315602, "Rio Grande",      0.38, 580.0,  210000),
    ]

    for v in vertices_rs:
        g.adicionar_vertice(v)

    arestas_rs = [
        # (u, v, horas)
        (4314902, 4316808, 0.5),
        (4314902, 4306403, 0.4),
        (4314902, 4310108, 0.3),
        (4316808, 4312401, 0.8),
        (4312401, 4318705, 0.5),
        (4312401, 4320404, 0.3),
        (4318705, 4320404, 0.4),
        (4320404, 4322509, 1.1),
        (4322509, 4307005, 0.9),
        (4307005, 4303004, 0.7),
        (4303004, 4316808, 1.5),
        (4310108, 4315602, 2.8),
        (4306403, 4316808, 0.3),
        (4300406, 4314902, 4.2),
        (4315602, 4322509, 3.1),
    ]

    for u, v, peso in arestas_rs:
        g.adicionar_aresta(u, v, peso)

    return g


def construir_grafo_matopiba() -> Grafo:
    """
    Cenário B: subgrafo simplificado de municípios do MATOPIBA
    (MA, TO, PI, BA) com índice de risco derivado de NDVI e
    precipitação INMET. Dados sintéticos.

    Peso das arestas = distância rodoviária estimada (km).
    """
    g = Grafo()

    vertices_matopiba = [
        criar_vertice(2111300, "Imperatriz",       0.65, 920.0,  260000),  # MA
        criar_vertice(2105302, "Chapadinha",       0.78, 380.0,   65000),  # MA
        criar_vertice(1721000, "Palmas",           0.50, 1100.0, 310000),  # TO
        criar_vertice(1716604, "Paraíso do TO",    0.70, 290.0,   50000),  # TO
        criar_vertice(2207702, "Parnaíba",         0.82, 440.0,  155000),  # PI
        criar_vertice(2209377, "Uruçuí",           0.88, 250.0,   40000),  # PI
        criar_vertice(2910727, "Barreiras",        0.74, 620.0,  160000),  # BA
        criar_vertice(2933307, "Luís Eduardo M.",  0.91, 480.0,   75000),  # BA
        criar_vertice(2102440, "Balsas",           0.86, 350.0,   95000),  # MA
        criar_vertice(2109007, "São Raimundo N.",  0.79, 215.0,   55000),  # MA
    ]

    for v in vertices_matopiba:
        g.adicionar_vertice(v)

    arestas_matopiba = [
        (2111300, 1721000, 630),
        (2111300, 2105302, 480),
        (2111300, 2102440, 290),
        (1721000, 1716604, 65),
        (1721000, 2910727, 920),
        (1716604, 2910727, 860),
        (2105302, 2207702, 540),
        (2207702, 2209377, 350),
        (2209377, 2910727, 420),
        (2910727, 2933307, 120),
        (2933307, 2209377, 310),
        (2102440, 2109007, 160),
        (2109007, 2105302, 290),
        (2102440, 2209377, 400),
    ]

    for u, v, peso in arestas_matopiba:
        g.adicionar_aresta(u, v, peso)

    return g


def construir_bst(grafo: Grafo) -> BinarySearchTree:
    """
    Constrói a BST a partir dos vértices do grafo, inserindo em
    ordem aleatória para evitar árvore degenerada.
    """
    import random
    bst = BinarySearchTree()
    ids = list(grafo.vertices.keys())
    random.shuffle(ids)
    for vid in ids:
        bst.inserir(grafo.vertices[vid])
    return bst


# ---------------------------------------------------------------------------
# 5. DEMONSTRAÇÃO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ESTRUTURAS DE DADOS — Global Solution 2026")
    print("=" * 60)

    # --- Grafo RS ---
    print("\n[1] GRAFO RS (Enchentes 2024)")
    g_rs = construir_grafo_rs()
    print(g_rs)
    print(f"  Vértices: {g_rs.ids()[:4]}... ({g_rs.num_vertices()} total)")

    # BFS a partir de Porto Alegre
    bfs_rs = g_rs.bfs(4314902)
    print(f"  BFS a partir de Porto Alegre: {[g_rs.vertices[i][1] for i in bfs_rs]}")

    # DFS a partir de Porto Alegre
    dfs_rs = g_rs.dfs(4314902)
    print(f"  DFS a partir de Porto Alegre: {[g_rs.vertices[i][1] for i in dfs_rs]}")

    # --- BST RS ---
    print("\n[2] BST (índice de risco — RS)")
    bst_rs = construir_bst(g_rs)
    print(bst_rs)
    print(f"  Balanceamento: {bst_rs.balanceamento()}")

    in_order = bst_rs.percurso_in_order()
    print("  Municípios em ordem crescente de risco:")
    for v in in_order:
        print(f"    {nome_municipio(v):25s} risco={risco(v):.2f}  custo={custo(v):.0f}")

    # Busca por intervalo
    alto_risco = bst_rs.buscar(0.80, 1.0)
    print(f"\n  Alto risco [0.80, 1.00]: {[nome_municipio(v) for v in alto_risco]}")

    # --- Grafo MATOPIBA ---
    print("\n[3] GRAFO MATOPIBA (Seca)")
    g_mat = construir_grafo_matopiba()
    print(g_mat)

    # --- Serialização ---
    import os
    os.makedirs("data/processed", exist_ok=True)
    g_rs.salvar_json("data/processed/grafo_rs.json")
    g_mat.salvar_json("data/processed/grafo_matopiba.json")
    print("\n[4] Grafos serializados em data/processed/")

    print("\n✓ data_structures.py executado com sucesso.")
