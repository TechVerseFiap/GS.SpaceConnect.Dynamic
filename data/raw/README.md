# data/raw — Dados Brutos Sintéticos

Arquivos gerados por `gerar_dados_sinteticos.py` com dados sintéticos
baseados nos cenários do enunciado. Em produção, substituir pelos dados
reais das fontes abaixo.

## Arquivos

### Cenário A — Enchentes RS
| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| municipios_rs.csv | ~80 | Municípios RS com risco de inundação, população, custo |
| arestas_rs.csv | ~240 | Rodovias entre municípios (distância km, tempo horas) |
| pluviometria_rs.csv | ~960 | Precipitação mensal por município (mai/2024–abr/2025) |

### Cenário B — Seca MATOPIBA
| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| municipios_matopiba.csv | 50 | Municípios MA/TO/PI/BA com NDVI, precipitação, risco seca |
| arestas_matopiba.csv | ~150 | Rodovias federais/estaduais entre municípios |
| ndvi_matopiba.csv | 600 | NDVI mensal e precipitação por município |

## Fontes reais (para substituição)

- **municipios_rs / municipios_matopiba**: IBGE malha municipal
  https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html
- **arestas_rs / arestas_matopiba**: DNIT malha viária federal
  https://www.gov.br/dnit/pt-br/assuntos/atlas-e-mapas/shapefiles
- **pluviometria_rs**: INMET BDMEP
  https://bdmep.inmet.gov.br/
- **ndvi_matopiba**: NASA Earthdata MODIS MOD13A3
  https://earthdata.nasa.gov
- **Índice de risco de inundação**: Defesa Civil RS
- **Categoria de seca**: ANA Hidroweb https://hidroweb.ana.gov.br

## Notas sobre os dados sintéticos

- Coordenadas geográficas: reais (lat/lon dos municípios)
- Populações: baseadas no Censo IBGE 2022 (aproximadas)
- Índices de risco: calculados por fórmula determinística (semente 42)
  com base em distância ao Guaíba (RS) e NDVI simulado (MATOPIBA)
- Distâncias: calculadas pela fórmula de Haversine com fator de
  tortuosidade rodoviária 1.35
- Precipitação: valores plausíveis para o clima de cada região,
  com pico em mai/2024 para simular as enchentes do RS
