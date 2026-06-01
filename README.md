# Global Solution 2026 — Monitoramento de Riscos Ambientais

**FIAP — 1º Semestre de 2026 | Estruturas de Dados e Algoritmos**
**Tema: Economia Espacial / Dynamic Programming**

---

## 👥 Integrantes do Grupo

| RA | Nome |
|----|------|
| XXXXXXX | Integrante 1 |
| XXXXXXX | Integrante 2 |
| XXXXXXX | Integrante 3 |

> ⚠️ Substitua os valores acima com RA e Nome reais dos integrantes.

---

## 📌 Descrição

Sistema de monitoramento e triagem de riscos ambientais em municípios brasileiros, construído com:

- **Grafo ponderado** de municípios e conexões (estradas/rotas)
- **Árvore Binária de Busca (BST)** para consultas por índice de risco
- **Força Bruta** para validação em instâncias pequenas (N ≤ 12)
- **Algoritmo Guloso (Dijkstra)** para instâncias reais

### Cenários implementados
- **Cenário A** — Rede de resposta a enchentes no Rio Grande do Sul
- **Cenário B** — Triagem de risco de seca no MATOPIBA

---

## 🗂️ Estrutura do Repositório

```
global-solution-2026-fund/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # Dados brutos: NDVI, pluviometria, malha viária
│   └── processed/            # Grafos e árvores serializados (JSON/pickle)
├── src/
│   ├── data_structures.py    # Lista, tupla, dict, heap, árvore binária, grafo
│   ├── brute_force.py        # Enumeração completa — baseline de validação
│   ├── greedy.py             # Dijkstra — solução eficiente
│   ├── performance_monitor.py# Tempo, memória, contadores de operações
│   └── visualizations.py     # Grafos, árvores e figuras obrigatórias
├── notebooks/
│   └── analise_resultados.ipynb
├── tests/
│   └── test_algorithms.py    # Testes unitários (pytest)
└── report/
    └── relatorio_final.pdf
```

---

## ⚙️ Instalação e Execução

### Pré-requisitos
- Python 3.10+
- pip

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Executar demonstração completa
```bash
python src/data_structures.py
python src/brute_force.py
python src/greedy.py
python src/performance_monitor.py
python src/visualizations.py
```

### Executar testes
```bash
pytest tests/ -v
```

### Jupyter Notebook (análise interativa)
```bash
jupyter notebook notebooks/analise_resultados.ipynb
```

---

## 📊 Módulos

| Módulo | Descrição |
|--------|-----------|
| `data_structures.py` | Implementação de Node, BST, Grafo com dict de listas de adjacência |
| `brute_force.py` | Backtracking para enumerar todos os caminhos; baseline ótimo |
| `greedy.py` | Dijkstra com heapq; reconstrução de caminho |
| `performance_monitor.py` | Benchmark de tempo (perf_counter) e memória (tracemalloc) |
| `visualizations.py` | Gráficos com networkx/matplotlib; visualização da BST |

---

## 🔗 Fontes de Dados
- IBGE — malha municipal: ibge.gov.br/geociencias
- INMET — dados climáticos: bdmep.inmet.gov.br
- DNIT — malha viária: dnit.gov.br
- NASA Earthdata — NDVI MODIS: earthdata.nasa.gov

---

## 🌍 ODS Relacionados
ODS 2 (Fome Zero), ODS 9 (Indústria e Infraestrutura), ODS 11 (Cidades Sustentáveis), ODS 13 (Ação Climática)
