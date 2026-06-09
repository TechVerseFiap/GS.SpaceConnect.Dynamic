# 🌍 Global Solution 2026 — Monitoramento de Riscos Ambientais

**FIAP — 1º Semestre de 2026**  
**Disciplina:** Estruturas de Dados e Algoritmos  
**Tema:** Economia Espacial / Dynamic Programming

---

## 👥 Integrantes do Grupo

| RM | Nome |
|----|------|
| 566223 | Davi Marques de Andrade Munhoz |
| 562559 | Diogo Oliveira Lima |
| 566539 | Leandro Simoneli da Silva |
| 562414 | Lucas dos Reis Aquino |
| 565356 | Lucas Perez Bonato |

---

## 📌 Descrição

Sistema de monitoramento e triagem de riscos ambientais em municípios brasileiros utilizando estruturas de dados e algoritmos para apoiar a tomada de decisão em cenários de desastres naturais.

### Tecnologias e Conceitos Aplicados

- 🗺️ **Grafo ponderado** para representar municípios e conexões (estradas e rotas)
- 🌳 **Árvore Binária de Busca (BST)** para consultas eficientes por índice de risco
- 🔍 **Força Bruta** para validação de resultados em instâncias pequenas (*N ≤ 12*)
- ⚡ **Algoritmo Guloso (Dijkstra)** para execução eficiente em cenários reais

### Cenários Implementados

#### Cenário A — Rede de Resposta a Enchentes no Rio Grande do Sul
Simulação da melhor rota de atendimento para municípios afetados por enchentes.

#### Cenário B — Triagem de Risco de Seca no MATOPIBA
Classificação e priorização de municípios com maior vulnerabilidade à seca.

---

## 🗂️ Estrutura do Repositório

```text
GS.SpaceConnect.Dynamic/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # Dados brutos: NDVI, pluviometria e malha viária
│   └── processed/            # Grafos e árvores serializados (JSON/Pickle)
├── src/
│   ├── data_structures.py     # Lista, tupla, dict, heap, BST e grafo
│   ├── brute_force.py         # Enumeração completa (baseline de validação)
│   ├── greedy.py              # Implementação do algoritmo de Dijkstra
│   ├── performance_monitor.py # Métricas de desempenho
│   └── visualizations.py      # Geração de gráficos e visualizações
├── notebooks/
│   └── analise_resultados.ipynb
├── tests/
│   └── test_algorithms.py
└── report/
    └── relatorio_final.pdf
```

---

## ⚙️ Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Instalação das Dependências

```bash
pip install -r requirements.txt
```

### Criação de Ambiente Virtual (Opcional, Recomendado)

Para evitar conflitos entre dependências do sistema e do projeto, recomenda-se utilizar um ambiente virtual Python.

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Para sair do ambiente virtual:

```bash
deactivate
```

### Execução dos Módulos

```bash
python src/data_structures.py
python src/brute_force.py
python src/greedy.py
python src/performance_monitor.py
python src/visualizations.py
```

### Execução dos Testes

```bash
pytest tests/ -v
```

### Análise Interativa com Jupyter Notebook

```bash
jupyter notebook notebooks/analise_resultados.ipynb
```

---

## 📊 Módulos do Projeto

| Módulo | Descrição |
|---------|------------|
| `data_structures.py` | Implementação das estruturas de dados utilizadas no projeto |
| `brute_force.py` | Busca exaustiva por todos os caminhos possíveis |
| `greedy.py` | Implementação do algoritmo de Dijkstra utilizando heap |
| `performance_monitor.py` | Monitoramento de tempo, memória e quantidade de operações |
| `visualizations.py` | Visualização de grafos, BSTs e gráficos de desempenho |

---

## 📈 Métricas Avaliadas

O projeto realiza comparações entre as abordagens de **Força Bruta** e **Algoritmo Guloso**, considerando:

- Tempo de execução
- Consumo de memória
- Quantidade de operações realizadas
- Escalabilidade para diferentes tamanhos de entrada

---

## 🔗 Fontes de Dados

- IBGE — Malha Municipal: https://www.ibge.gov.br/geociencias
- INMET — Dados Climáticos: https://bdmep.inmet.gov.br
- DNIT — Malha Viária: https://www.gov.br/dnit
- NASA Earthdata — NDVI MODIS: https://www.earthdata.nasa.gov

---

## 🌱 Objetivos de Desenvolvimento Sustentável (ODS)

Este projeto está alinhado com os seguintes ODS da ONU:

- **ODS 2** — Fome Zero e Agricultura Sustentável
- **ODS 9** — Indústria, Inovação e Infraestrutura
- **ODS 11** — Cidades e Comunidades Sustentáveis
- **ODS 13** — Ação Contra a Mudança Global do Clima

---

## 📄 Licença

Projeto acadêmico desenvolvido para a disciplina de **Estruturas de Dados e Algoritmos** da FIAP.
