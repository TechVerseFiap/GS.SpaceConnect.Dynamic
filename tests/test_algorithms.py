"""
tests/test_algorithms.py
========================
Testes unitários com pytest para todos os módulos do projeto.

Execução:
    pytest tests/ -v
    pytest tests/ -v --tb=short
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_structures import (
    Grafo, BinarySearchTree, Node,
    criar_vertice, id_municipio, nome_municipio, risco, custo, populacao,
    construir_grafo_rs, construir_grafo_matopiba, construir_bst,
)
from brute_force import forca_bruta_caminhos, resetar_contadores
from greedy import dijkstra, reconstruir_caminho, planejar_atendimento


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def grafo_simples():
    """Grafo pequeno (5 nós) para testes básicos."""
    g = Grafo()
    for i in range(5):
        g.adicionar_vertice(criar_vertice(i, f"Mun{i}", 0.1 * (i + 1), 100.0 + i, 10000 + i))
    g.adicionar_aresta(0, 1, 1.0)
    g.adicionar_aresta(1, 2, 2.0)
    g.adicionar_aresta(2, 3, 1.5)
    g.adicionar_aresta(3, 4, 0.5)
    g.adicionar_aresta(0, 4, 10.0)  # Caminho longo direto
    g.adicionar_aresta(1, 3, 3.0)
    return g


@pytest.fixture
def grafo_rs():
    return construir_grafo_rs()


@pytest.fixture
def grafo_matopiba():
    return construir_grafo_matopiba()


@pytest.fixture
def bst_rs(grafo_rs):
    return construir_bst(grafo_rs)


# ===========================================================================
# Testes: Tupla / Vértice
# ===========================================================================

class TestVertice:
    def test_criar_vertice_retorna_tupla(self):
        v = criar_vertice(1, "Teste", 0.5, 200.0, 50000)
        assert isinstance(v, tuple)

    def test_campos_corretos(self):
        v = criar_vertice(42, "Porto Alegre", 0.72, 1850.0, 1400000)
        assert id_municipio(v) == 42
        assert nome_municipio(v) == "Porto Alegre"
        assert risco(v) == pytest.approx(0.72)
        assert custo(v) == pytest.approx(1850.0)
        assert populacao(v) == 1400000

    def test_imutabilidade(self):
        v = criar_vertice(1, "Mun", 0.5, 100.0, 5000)
        with pytest.raises(TypeError):
            v[0] = 99  # type: ignore


# ===========================================================================
# Testes: Grafo
# ===========================================================================

class TestGrafo:
    def test_adicionar_vertices(self, grafo_simples):
        assert grafo_simples.num_vertices() == 5

    def test_adicionar_arestas_bidirecionais(self, grafo_simples):
        viz_0 = [v for v, _ in grafo_simples.vizinhos(0)]
        assert 1 in viz_0
        assert 4 in viz_0
        viz_1 = [v for v, _ in grafo_simples.vizinhos(1)]
        assert 0 in viz_1

    def test_vizinhos_inexistente_retorna_lista_vazia(self):
        g = Grafo()
        assert g.vizinhos(999) == []

    def test_num_arestas(self, grafo_simples):
        assert grafo_simples.num_arestas() == 6

    def test_bfs_visita_todos(self, grafo_simples):
        resultado = grafo_simples.bfs(0)
        assert set(resultado) == {0, 1, 2, 3, 4}

    def test_dfs_visita_todos(self, grafo_simples):
        resultado = grafo_simples.dfs(0)
        assert set(resultado) == {0, 1, 2, 3, 4}

    def test_bfs_origem_primeiro(self, grafo_simples):
        assert grafo_simples.bfs(0)[0] == 0

    def test_dfs_origem_primeiro(self, grafo_simples):
        assert grafo_simples.dfs(0)[0] == 0

    def test_grafo_rs_12_vertices(self, grafo_rs):
        assert grafo_rs.num_vertices() == 12

    def test_grafo_matopiba_10_vertices(self, grafo_matopiba):
        assert grafo_matopiba.num_vertices() == 10

    def test_grafo_rs_conectado(self, grafo_rs):
        ids = grafo_rs.ids()
        visitados = grafo_rs.bfs(ids[0])
        assert set(visitados) == set(ids)

    def test_serializar_json(self, grafo_simples, tmp_path):
        caminho = str(tmp_path / "grafo.json")
        grafo_simples.salvar_json(caminho)
        g2 = Grafo.carregar_json(caminho)
        assert g2.num_vertices() == grafo_simples.num_vertices()
        assert g2.num_arestas() == grafo_simples.num_arestas()


# ===========================================================================
# Testes: BST
# ===========================================================================

class TestBST:
    def test_inserir_e_tamanho(self):
        bst = BinarySearchTree()
        for i in range(5):
            bst.inserir(criar_vertice(i, f"M{i}", 0.1 * (i + 1), 100.0, 1000))
        assert len(bst) == 5

    def test_in_order_crescente(self):
        bst = BinarySearchTree()
        riscos_inseridos = [0.7, 0.3, 0.9, 0.1, 0.5]
        for i, r in enumerate(riscos_inseridos):
            bst.inserir(criar_vertice(i, f"M{i}", r, 100.0, 1000))
        in_order = [risco(v) for v in bst.percurso_in_order()]
        assert in_order == sorted(in_order)

    def test_busca_intervalo(self):
        bst = BinarySearchTree()
        for i in range(10):
            bst.inserir(criar_vertice(i, f"M{i}", 0.1 * (i + 1), 100.0, 1000))
        resultado = bst.buscar(0.4, 0.7)
        for v in resultado:
            assert 0.4 <= risco(v) <= 0.7

    def test_busca_intervalo_vazio(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "M0", 0.5, 100.0, 1000))
        assert bst.buscar(0.8, 1.0) == []

    def test_altura_folha(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "M0", 0.5, 100.0, 1000))
        assert bst.altura() == 1

    def test_altura_dois_niveis(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "M0", 0.5, 100.0, 1000))
        bst.inserir(criar_vertice(1, "M1", 0.3, 100.0, 1000))
        bst.inserir(criar_vertice(2, "M2", 0.7, 100.0, 1000))
        assert bst.altura() == 2

    def test_remover_folha(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "M0", 0.5, 100.0, 1000))
        bst.inserir(criar_vertice(1, "M1", 0.3, 100.0, 1000))
        bst.remover(1)
        assert len(bst) == 1
        assert bst.buscar(0.3, 0.3) == []

    def test_remover_no_com_dois_filhos(self):
        bst = BinarySearchTree()
        # Insere em ordem para criar árvore balanceada
        bst.inserir(criar_vertice(0, "Raiz", 0.5, 100.0, 1000))
        bst.inserir(criar_vertice(1, "Esq", 0.3, 100.0, 1000))
        bst.inserir(criar_vertice(2, "Dir", 0.7, 100.0, 1000))
        bst.inserir(criar_vertice(3, "EsqDir", 0.4, 100.0, 1000))
        bst.remover(0)  # Remove raiz
        assert len(bst) == 3
        # In-order ainda deve estar crescente
        in_order = [risco(v) for v in bst.percurso_in_order()]
        assert in_order == sorted(in_order)

    def test_remover_no_com_um_filho(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "Raiz", 0.5, 100.0, 1000))
        bst.inserir(criar_vertice(1, "Filho", 0.3, 100.0, 1000))
        bst.remover(0)
        assert len(bst) == 1
        in_order = [risco(v) for v in bst.percurso_in_order()]
        assert in_order == [0.3]

    def test_remover_id_inexistente_nao_altera_tamanho(self):
        bst = BinarySearchTree()
        bst.inserir(criar_vertice(0, "M0", 0.5, 100.0, 1000))
        bst.remover(99)
        assert len(bst) == 1

    def test_bst_rs_ordenado(self, bst_rs):
        in_order = [risco(v) for v in bst_rs.percurso_in_order()]
        assert in_order == sorted(in_order)


# ===========================================================================
# Testes: Força Bruta
# ===========================================================================

class TestForcaBruta:
    def test_encontra_caminho_simples(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, 0, 4)
        assert res["melhor_caminho"][0] == 0
        assert res["melhor_caminho"][-1] == 4

    def test_caminho_otimo_custo(self, grafo_simples):
        # Caminho 0→1→2→3→4 = 1+2+1.5+0.5 = 5.0
        # Caminho 0→4 = 10.0
        # Melhor deve ser via intermediários
        res = forca_bruta_caminhos(grafo_simples, 0, 4)
        assert res["melhor_custo"] < 10.0  # Melhor que o direto

    def test_sem_caminho_retorna_infinito(self):
        g = Grafo()
        for i in range(3):
            g.adicionar_vertice(criar_vertice(i, f"M{i}", 0.1 * i, 100.0, 1000))
        g.adicionar_aresta(0, 1, 1.0)
        # Vértice 2 isolado
        res = forca_bruta_caminhos(g, 0, 2)
        assert res["melhor_custo"] == float("inf")
        assert res["melhor_caminho"] == []

    def test_contador_chamadas_positivo(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, 0, 4)
        assert res["chamadas"] > 0
        assert res["avaliados"] > 0

    def test_todos_caminhos_lista(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, 0, 4)
        assert isinstance(res["todos_caminhos"], list)
        assert all(c[0][0] == 0 and c[0][-1] == 4
                   for c in res["todos_caminhos"])


# ===========================================================================
# Testes: Dijkstra (Greedy)
# ===========================================================================

class TestDijkstra:
    def test_distancia_origem_zero(self, grafo_simples):
        dist, _, _ = dijkstra(grafo_simples, 0)
        assert dist[0] == pytest.approx(0.0)

    def test_distancia_correta(self, grafo_simples):
        dist, _, _ = dijkstra(grafo_simples, 0)
        # 0→1 = 1.0
        assert dist[1] == pytest.approx(1.0)
        # 0→1→2 = 3.0
        assert dist[2] == pytest.approx(3.0)

    def test_caminho_otimo_menor_que_direto(self, grafo_simples):
        dist, _, _ = dijkstra(grafo_simples, 0)
        # Direto 0→4 = 10.0; via 1,2,3 = 5.0
        assert dist[4] < 10.0

    def test_reconstrucao_caminho(self, grafo_simples):
        dist, pred, _ = dijkstra(grafo_simples, 0)
        cam = reconstruir_caminho(pred, 0, 4)
        assert cam[0] == 0
        assert cam[-1] == 4
        # Custo deve bater com dist
        custo_recalc = sum(
            next(p for v, p in grafo_simples.vizinhos(cam[i]) if v == cam[i+1])
            for i in range(len(cam) - 1)
        )
        assert custo_recalc == pytest.approx(dist[4])

    def test_reconstrucao_sem_caminho_retorna_lista_vazia(self):
        g = Grafo()
        g.adicionar_vertice(criar_vertice(0, "M0", 0.1, 100.0, 1000))
        g.adicionar_vertice(criar_vertice(1, "M1", 0.2, 100.0, 1000))
        dist, pred, _ = dijkstra(g, 0)
        assert dist[1] == float("inf")
        assert reconstruir_caminho(pred, 0, 1) == []

    def test_reconstrucao_origem_igual_destino(self):
        g = Grafo()
        g.adicionar_vertice(criar_vertice(0, "M0", 0.1, 100.0, 1000))
        _, pred, _ = dijkstra(g, 0)
        assert reconstruir_caminho(pred, 0, 0) == [0]

    def test_sem_caminho_retorna_infinito(self):
        g = Grafo()
        g.adicionar_vertice(criar_vertice(0, "M0", 0.1, 100.0, 1000))
        g.adicionar_vertice(criar_vertice(1, "M1", 0.2, 100.0, 1000))
        dist, _, _ = dijkstra(g, 0)
        assert dist[1] == float("inf")

    def test_dijkstra_igual_fb(self, grafo_simples):
        """Dijkstra deve ser ótimo como a Força Bruta em grafos pequenos."""
        dist_dij, _, _ = dijkstra(grafo_simples, 0)
        res_fb = forca_bruta_caminhos(grafo_simples, 0, 4)

        assert dist_dij[4] == pytest.approx(res_fb["melhor_custo"], rel=1e-6)

    def test_dijkstra_rs_alcanca_todos(self, grafo_rs):
        """Dijkstra deve alcançar todos os vértices do grafo RS."""
        hub = 4314902  # Porto Alegre
        dist, _, _ = dijkstra(grafo_rs, hub)
        infinitos = [k for k, v in dist.items() if v == float("inf")]
        assert len(infinitos) == 0, f"Vértices inalcançáveis: {infinitos}"

    def test_operacoes_registradas(self, grafo_simples):
        _, _, ops = dijkstra(grafo_simples, 0)
        assert ops["relaxamentos"] > 0
        assert ops["insercoes_heap"] > 0
        assert ops["extraccoes_heap"] > 0


# ===========================================================================
# Testes: Integração
# ===========================================================================

class TestIntegracao:
    def test_bst_consulta_alto_risco(self, bst_rs):
        """Municípios de alto risco devem ser retornados pela BST."""
        alto = bst_rs.buscar(0.80, 1.0)
        assert len(alto) > 0
        for v in alto:
            assert risco(v) >= 0.80

    def test_dijkstra_respeita_pesos(self, grafo_rs):
        """O custo calculado pelo Dijkstra deve ser positivo e finito."""
        hub = 4314902
        dist, _, _ = dijkstra(grafo_rs, hub)
        for vid, d in dist.items():
            if vid != hub:
                assert d > 0
                assert d != float("inf"), f"Vértice {vid} inalcançável"

    def test_fb_valida_dijkstra_grafo_rs(self, grafo_rs):
        """
        Para o subgrafo RS de 12 vértices, FB e Dijkstra devem
        encontrar o mesmo custo ótimo (gap = 0).
        """
        hub = 4314902
        destino = 4316808  # São Leopoldo — vizinho direto

        res_fb = forca_bruta_caminhos(grafo_rs, hub, destino)
        dist_dij, _, _ = dijkstra(grafo_rs, hub)

        assert dist_dij[destino] == pytest.approx(res_fb["melhor_custo"], rel=1e-6)

    def test_planejamento_ordem_por_risco_e_distancia(self):
        g = Grafo()
        v_hub = criar_vertice(0, "Hub", 0.20, 100.0, 1000)
        v_a = criar_vertice(1, "A", 0.95, 100.0, 1000)
        v_b = criar_vertice(2, "B", 0.95, 100.0, 1000)
        v_c = criar_vertice(3, "C", 0.85, 100.0, 1000)
        v_low = criar_vertice(4, "D", 0.50, 100.0, 1000)
        for v in [v_hub, v_a, v_b, v_c, v_low]:
            g.adicionar_vertice(v)
        g.adicionar_aresta(0, 1, 5.0)
        g.adicionar_aresta(0, 2, 2.0)
        g.adicionar_aresta(0, 3, 4.0)
        g.adicionar_aresta(0, 4, 1.0)

        bst = BinarySearchTree()
        for v in [v_hub, v_a, v_b, v_c, v_low]:
            bst.inserir(v)

        planos = planejar_atendimento(g, bst, hub=0, limiar_risco=0.80, orcamento_km=10)
        ids_ordenados = [p["id"] for p in planos]
        assert ids_ordenados == [2, 1, 3]

    def test_planejamento_respeita_orcamento(self):
        g = Grafo()
        v_hub = criar_vertice(0, "Hub", 0.20, 100.0, 1000)
        v_a = criar_vertice(1, "A", 0.95, 100.0, 1000)
        v_b = criar_vertice(2, "B", 0.95, 100.0, 1000)
        for v in [v_hub, v_a, v_b]:
            g.adicionar_vertice(v)
        g.adicionar_aresta(0, 1, 5.0)
        g.adicionar_aresta(0, 2, 2.0)

        bst = BinarySearchTree()
        for v in [v_hub, v_a, v_b]:
            bst.inserir(v)

        planos = planejar_atendimento(g, bst, hub=0, limiar_risco=0.80, orcamento_km=3)
        ids_ordenados = [p["id"] for p in planos]
        assert ids_ordenados == [2]
