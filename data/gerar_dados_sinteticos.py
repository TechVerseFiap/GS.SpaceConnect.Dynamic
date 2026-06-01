"""
gerar_dados_sinteticos.py
=========================
Gera todos os arquivos de dados sintéticos para data/raw/.
Execute uma vez para popular a pasta antes de rodar o sistema.

    python data/gerar_dados_sinteticos.py
"""

import csv
import random
import math
import os

random.seed(42)
OUTPUT = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT, exist_ok=True)


# ============================================================
# UTILITÁRIOS
# ============================================================

def distancia_km(lat1, lon1, lat2, lon2):
    """Fórmula de Haversine — distância em km entre dois pontos."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 1)


def horas_de_viagem(km, velocidade_media=60):
    """Converte km em horas com fator de tortuosidade rodoviária."""
    return round(km * 1.35 / velocidade_media, 2)


# ============================================================
# CENÁRIO A — RS: Municípios afetados pelas enchentes 2024
# Fonte simulada: malha DNIT + Defesa Civil RS
# ============================================================

MUNICIPIOS_RS = [
    # (geocodigo, nome, uf, lat, lon, pop_estimada)
    (4314902, "Porto Alegre",         "RS", -30.0368, -51.2090, 1400000),
    (4316808, "São Leopoldo",         "RS", -29.7603, -51.1489,  230000),
    (4306403, "Canoas",               "RS", -29.9175, -51.1839,  350000),
    (4312401, "Lajeado",              "RS", -29.4667, -51.9620,   82000),
    (4310108, "Guaíba",               "RS", -30.1117, -51.3250,  100000),
    (4318705, "Venâncio Aires",       "RS", -29.6131, -52.1908,   73000),
    (4320404, "Encantado",            "RS", -29.2358, -51.8728,   21000),
    (4322509, "Santa Cruz do Sul",    "RS", -29.7175, -52.4253,  130000),
    (4307005, "Caxias do Sul",        "RS", -29.1681, -51.1794,  530000),
    (4303004, "Bento Gonçalves",      "RS", -29.1706, -51.5183,  120000),
    (4315602, "Rio Grande",           "RS", -32.0350, -52.0986,  210000),
    (4300406, "Alegrete",             "RS", -29.7833, -55.7953,   78000),
    (4304606, "Cachoeira do Sul",     "RS", -29.9867, -52.8964,   83000),
    (4304903, "Cachoeirinha",         "RS", -29.9500, -51.0939,  130000),
    (4305108, "Camaquã",              "RS", -30.8508, -51.8108,   62000),
    (4305355, "Campo Bom",            "RS", -29.6739, -51.0528,   65000),
    (4306205, "Candelária",           "RS", -29.6667, -52.7833,   31000),
    (4307807, "Cruz Alta",            "RS", -28.6378, -53.6069,   62000),
    (4308904, "Estrela",              "RS", -29.5000, -51.9667,   34000),
    (4309100, "Farroupilha",          "RS", -29.2256, -51.3519,   70000),
    (4310207, "Gravataí",             "RS", -29.9406, -50.9878,  280000),
    (4313300, "Montenegro",           "RS", -29.6878, -51.4608,   63000),
    (4314100, "Nova Hamburgo",        "RS", -29.6789, -51.1317,  250000),
    (4315107, "Pelotas",              "RS", -31.7714, -52.3425,  340000),
    (4316307, "Santa Maria",          "RS", -29.6839, -53.8069,  285000),
    (4317202, "Santo Ângelo",         "RS", -28.2997, -54.2639,   75000),
    (4321204, "Sapucaia do Sul",      "RS", -29.8325, -51.1517,  140000),
    (4322806, "Triunfo",              "RS", -29.9386, -51.7219,   25000),
    (4323804, "Viamão",               "RS", -30.0808, -51.0228,  260000),
    (4323002, "Uruguaiana",           "RS", -29.7550, -57.0856,  125000),
    (4308508, "Erechim",              "RS", -27.6344, -52.2733,  105000),
    (4311403, "Ijuí",                 "RS", -28.3878, -53.9150,   83000),
    (4322004, "Taquara",              "RS", -29.6522, -50.7825,   55000),
    (4322400, "Três Coroas",          "RS", -29.5125, -50.7783,   22000),
    (4321600, "Soledade",             "RS", -28.8139, -52.5103,   30000),
    (4319901, "São Lourenço do Sul",  "RS", -31.3622, -51.9775,   43000),
    (4318606, "São Gabriel",          "RS", -30.3367, -54.3206,   61000),
    (4318408, "São Borja",            "RS", -28.6611, -55.9753,   61000),
    (4304200, "Carazinho",            "RS", -28.2836, -52.7911,   61000),
    (4308003, "Dois Irmãos",          "RS", -29.5881, -51.0886,   32000),
    (4309308, "Feliz",                "RS", -29.4533, -51.3075,   14000),
    (4309407, "Flores da Cunha",      "RS", -29.0261, -51.1839,   32000),
    (4314407, "Nova Prata",           "RS", -28.7842, -51.6117,   22000),
    (4320107, "São Paulo das Missões","RS", -28.0167, -55.0167,   14000),
    (4305454, "Campo Novo",           "RS", -27.6736, -53.8064,   13000),
    (4311700, "Ibirubá",              "RS", -28.6228, -53.0864,   21000),
    (4312054, "Jóia",                 "RS", -28.6569, -54.1236,    9000),
    (4312658, "Liberato Salzano",     "RS", -27.5256, -53.0761,   13000),
    (4314332, "Nova Palma",           "RS", -29.4764, -53.4681,   11000),
    (4315701, "Roca Sales",           "RS", -29.3867, -51.8656,   11000),
    (4316402, "Santa Rosa",           "RS", -27.8697, -54.4822,   73000),
    (4316956, "Santiago",             "RS", -29.1878, -54.8664,   50000),
    (4317400, "Santo Augusto",        "RS", -27.8500, -53.7758,   14000),
    (4318309, "São Borja",            "RS", -28.6611, -55.9753,   61000),
    (4319208, "São João do Polêsine", "RS", -29.4833, -53.4014,    3000),
    (4320305, "São Martinho",         "RS", -27.7156, -53.9628,    7000),
    (4320438, "São Miguel das Missões","RS",-28.5522, -54.5578,   10000),
    (4320602, "São Sepé",             "RS", -30.1636, -53.5681,   24000),
    (4320909, "São Valentim",         "RS", -27.3667, -52.6833,    9000),
    (4321501, "Seberi",               "RS", -27.4775, -53.3978,   17000),
    (4321808, "Tapejara",             "RS", -27.9717, -52.0094,   21000),
    (4322251, "Três de Maio",         "RS", -27.7711, -54.2447,   24000),
    (4322707, "Tucunduva",            "RS", -27.6511, -54.4497,   11000),
    (4323200, "Vale do Sol",          "RS", -29.6056, -52.6725,   12000),
    (4323606, "Veranópolis",          "RS", -28.9375, -51.5556,   24000),
    (4323903, "Vicente Dutra",        "RS", -27.1792, -53.3886,   10000),
    (4300802, "Arroio Grande",        "RS", -32.2336, -53.0853,   19000),
    (4301305, "Bagé",                 "RS", -31.3286, -54.1053,  122000),
    (4301537, "Barão do Triunfo",     "RS", -30.4208, -51.7322,   12000),
    (4302105, "Bom Jesus",            "RS", -28.6708, -50.4303,   12000),
    (4303103, "Caçapava do Sul",      "RS", -30.5133, -53.4878,   35000),
    (4305207, "Camargo",              "RS", -28.5028, -52.0211,    5000),
    (4305769, "Canguçu",              "RS", -31.4003, -52.6753,   55000),
    (4306007, "Capão do Leão",        "RS", -31.7600, -52.4717,   25000),
    (4306106, "Capivari do Sul",      "RS", -30.1444, -50.5133,    9000),
    (4309902, "Garibaldi",            "RS", -29.2564, -51.5333,   36000),
    (4310207, "Gravataí",             "RS", -29.9406, -50.9878,  280000),
    (4311403, "Ijuí",                 "RS", -28.3878, -53.9150,   83000),
    (4311502, "Independência",        "RS", -27.8222, -54.5981,   10000),
    (4312203, "Lagoa Vermelha",       "RS", -28.2092, -51.5325,   29000),
]

# ── índice de risco de inundação (simulado com base em altitude e bacia)
# Municípios mais próximos de rios e com menor altitude têm maior risco
def calcular_risco_rs(lat, lon, pop):
    """Risco simulado: altitude inversa + proximidade com Rio Jacuí/Guaíba."""
    # Centróide aproximado do delta do Guaíba
    dist_guaiba = distancia_km(lat, lon, -30.20, -51.30)
    risco_geo = max(0, 1 - dist_guaiba / 350)
    risco_pop = min(0.3, math.log10(max(pop, 1000)) / 7)
    ruido = random.uniform(-0.05, 0.05)
    return round(min(0.99, max(0.10, risco_geo * 0.6 + risco_pop * 0.3 + 0.1 + ruido)), 2)


print("Gerando municipios_rs.csv ...")
with open(f"{OUTPUT}/municipios_rs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo", "nome", "uf", "latitude", "longitude",
                "populacao", "indice_risco_inundacao", "custo_atendimento_mil_reais",
                "altitude_m", "bacia_hidrografica"])
    for geo, nome, uf, lat, lon, pop in MUNICIPIOS_RS:
        risco = calcular_risco_rs(lat, lon, pop)
        custo = round(pop * 0.0013 + random.uniform(50, 300), 1)
        alt   = round(random.uniform(2, 900) * (1 - risco * 0.5))
        bacia = "Jacuí" if lon > -53 else ("Pelotas" if lat < -30.5 else "Guaíba")
        w.writerow([geo, nome, uf, lat, lon, pop, risco, custo, alt, bacia])

print(f"  {len(MUNICIPIOS_RS)} municípios RS salvos.")


# ── arestas (rodovias RS)
print("Gerando arestas_rs.csv ...")
with open(f"{OUTPUT}/arestas_rs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo_origem", "geocodigo_destino",
                "distancia_km", "tempo_horas", "rodovia", "condicao"])
    ids = [m[0] for m in MUNICIPIOS_RS]
    coords = {m[0]: (m[3], m[4]) for m in MUNICIPIOS_RS}
    rodovias = ["BR-116","BR-386","BR-287","BR-290","BR-392",
                "RS-020","RS-122","RS-130","RS-240","RS-324"]
    arestas_feitas = set()
    # Conecta cada município aos 3 vizinhos mais próximos
    for i, geo_u in enumerate(ids):
        dists = sorted(
            [(distancia_km(*coords[geo_u], *coords[geo_v]), geo_v)
             for geo_v in ids if geo_v != geo_u]
        )
        for dist, geo_v in dists[:3]:
            chave = (min(geo_u, geo_v), max(geo_u, geo_v))
            if chave in arestas_feitas:
                continue
            arestas_feitas.add(chave)
            horas = horas_de_viagem(dist)
            rod = random.choice(rodovias)
            cond = random.choice(["boa","regular","regular","ruim"])
            w.writerow([geo_u, geo_v, dist, horas, rod, cond])

print(f"  {len(arestas_feitas)} arestas RS salvas.")


# ── pluviometria RS (últimos 12 meses simulados — INMET)
print("Gerando pluviometria_rs.csv ...")
meses = ["2024-05","2024-06","2024-07","2024-08","2024-09","2024-10",
         "2024-11","2024-12","2025-01","2025-02","2025-03","2025-04"]
with open(f"{OUTPUT}/pluviometria_rs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo","municipio","mes","precipitacao_mm",
                "desvio_historico_pct","alerta_enchente"])
    for geo, nome, uf, lat, lon, pop in MUNICIPIOS_RS:
        for mes in meses:
            # Maio/2024 = pico das enchentes
            fator = 3.5 if mes == "2024-05" else (1.8 if mes in ["2024-04","2024-06"] else 1.0)
            precip = round(random.uniform(60, 180) * fator, 1)
            desvio = round((precip / 120 - 1) * 100, 1)
            alerta = "SIM" if precip > 300 else "NÃO"
            w.writerow([geo, nome, mes, precip, desvio, alerta])

print(f"  {len(MUNICIPIOS_RS) * len(meses)} registros pluviométricos RS salvos.")


# ============================================================
# CENÁRIO B — MATOPIBA: 50 municípios com risco de seca
# Fonte simulada: NDVI MODIS/NASA + INMET precipitação
# ============================================================

MUNICIPIOS_MATOPIBA = [
    # (geocodigo, nome, uf, lat, lon, pop)
    (2111300, "Imperatriz",              "MA", -5.5267,  -47.4792,  260000),
    (2105302, "Chapadinha",              "MA", -3.7417,  -43.3556,   65000),
    (2102440, "Balsas",                  "MA", -7.5322,  -46.0353,   95000),
    (2109007, "São Raimundo das Mangabeiras","MA",-6.9903,-45.4028,  55000),
    (2100055, "Açailândia",              "MA", -4.9453,  -47.4992,  110000),
    (2100501, "Alto Parnaíba",           "MA", -9.1053,  -45.9325,   19000),
    (2101400, "Araioses",                "MA", -2.8942,  -41.9028,   28000),
    (2102200, "Bacabal",                 "MA", -4.2258,  -44.7906,   99000),
    (2103000, "Brejo",                   "MA", -3.6850,  -42.7444,   39000),
    (2103703, "Caxias",                  "MA", -4.8617,  -43.3564,  160000),
    (2104800, "Colinas",                 "MA", -6.0228,  -44.2469,   37000),
    (2106201, "Grajaú",                  "MA", -5.8217,  -46.1392,   66000),
    (2107803, "Mirador",                 "MA", -6.3728,  -44.3628,   23000),
    (2108405, "Pedreiras",               "MA", -4.5717,  -44.5964,   41000),
    (2109239, "Sambaíba",                "MA", -7.1292,  -45.3500,   12000),
    (2110203, "Timon",                   "MA", -5.0933,  -42.8344,  170000),
    (1721000, "Palmas",                  "TO", -10.2491, -48.3243,  310000),
    (1716604, "Paraíso do Tocantins",    "TO", -10.1733, -48.8842,   50000),
    (1702109, "Araguaína",               "TO", -7.1919,  -48.2042,  180000),
    (1703602, "Augustinópolis",          "TO", -5.4658,  -47.8894,   24000),
    (1705508, "Colinas do Tocantins",    "TO", -8.0592,  -48.4758,   38000),
    (1708205, "Guaraí",                  "TO", -8.8339,  -48.5142,   25000),
    (1709500, "Miracema do Tocantins",   "TO", -9.5631,  -48.3919,   21000),
    (1712504, "Pedro Afonso",            "TO", -8.9694,  -48.1769,   14000),
    (1715507, "Nova Olinda",             "TO", -7.8378,  -48.4264,   13000),
    (2207702, "Parnaíba",                "PI", -2.9044,  -41.7764,  155000),
    (2209377, "Uruçuí",                  "PI", -7.2317,  -44.5558,   40000),
    (2200053, "Água Branca",             "PI", -5.8889,  -42.6408,   17000),
    (2200202, "Altos",                   "PI", -4.9700,  -42.4594,   47000),
    (2201507, "Barras",                  "PI", -4.2458,  -42.2967,   45000),
    (2202307, "Campo Maior",             "PI", -4.8311,  -42.1647,   47000),
    (2203750, "Corrente",                "PI", -10.4411, -45.1700,   26000),
    (2204006, "Demerval Lobão",          "PI", -5.3583,  -42.6722,   17000),
    (2205003, "Floriano",                "PI", -6.7681,  -43.0219,   60000),
    (2207603, "Oeiras",                  "PI", -7.0211,  -42.1289,   35000),
    (2208650, "São João do Piauí",       "PI", -8.3581,  -42.2486,   20000),
    (2910727, "Barreiras",               "BA", -12.1522, -44.9939,  160000),
    (2933307, "Luís Eduardo Magalhães",  "BA", -12.0964, -45.7944,   75000),
    (2900702, "Angical",                 "BA", -12.0064, -44.7117,   17000),
    (2902708, "Baianópolis",             "BA", -12.0694, -44.5369,   15000),
    (2903276, "Barra",                   "BA", -11.0875, -43.1361,   61000),
    (2903300, "Barra do Mendes",         "BA", -11.8081, -42.0578,   16000),
    (2904605, "Bom Jesus da Lapa",       "BA", -13.2553, -43.4150,   67000),
    (2906501, "Caetité",                 "BA", -14.0689, -42.4733,   47000),
    (2912202, "Correntina",              "BA", -13.3550, -44.6428,   32000),
    (2915601, "Ibotirama",               "BA", -12.1800, -43.2128,   26000),
    (2918209, "Iuiú",                    "BA", -14.2231, -43.6492,   12000),
    (2919207, "Juazeiro",                "BA", -9.4281,  -40.5028,  218000),
    (2921709, "Mansidão",                "BA", -10.7228, -44.0394,   11000),
    (2927408, "Santa Maria da Vitória",  "BA", -13.3953, -44.2083,   38000),
]


def calcular_ndvi(lat, lon):
    """NDVI simulado: regiões mais secas (cerrado/sertão) têm NDVI menor."""
    # NDVI decresce com latitude sul e longitude oeste no cerrado
    base = 0.55 - abs(lat) * 0.01 - abs(lon + 45) * 0.005
    return round(max(0.10, min(0.80, base + random.uniform(-0.08, 0.08))), 3)


def calcular_risco_seca(ndvi, precip_anual):
    """Risco de seca: inversamente proporcional a NDVI e precipitação."""
    risco_ndvi  = max(0, 1 - ndvi / 0.6)
    risco_prec  = max(0, 1 - precip_anual / 1200)
    return round(min(0.99, max(0.10, risco_ndvi * 0.5 + risco_prec * 0.4 + random.uniform(0, 0.1))), 2)


print("\nGerando municipios_matopiba.csv ...")
with open(f"{OUTPUT}/municipios_matopiba.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo","nome","uf","latitude","longitude","populacao",
                "ndvi_medio","precipitacao_anual_mm","indice_risco_seca",
                "custo_atendimento_mil_reais","bioma","categoria_risco"])
    for geo, nome, uf, lat, lon, pop in MUNICIPIOS_MATOPIBA:
        ndvi   = calcular_ndvi(lat, lon)
        precip = round(random.uniform(700, 1400), 0)
        risco  = calcular_risco_seca(ndvi, precip)
        custo  = round(pop * 0.0012 + random.uniform(50, 250), 1)
        bioma  = "Cerrado" if ndvi > 0.35 else ("Caatinga" if lat < -8 else "Cerrado/Caatinga")
        cat    = "CRÍTICO" if risco >= 0.80 else ("ALTO" if risco >= 0.65 else ("MÉDIO" if risco >= 0.45 else "BAIXO"))
        w.writerow([geo, nome, uf, lat, lon, pop, ndvi, int(precip), risco, custo, bioma, cat])

print(f"  {len(MUNICIPIOS_MATOPIBA)} municípios MATOPIBA salvos.")


print("Gerando arestas_matopiba.csv ...")
with open(f"{OUTPUT}/arestas_matopiba.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo_origem","geocodigo_destino",
                "distancia_km","tempo_horas","rodovia","tipo_via"])
    ids_mat = [m[0] for m in MUNICIPIOS_MATOPIBA]
    coords_mat = {m[0]: (m[3], m[4]) for m in MUNICIPIOS_MATOPIBA}
    rods_mat = ["BR-010","BR-020","BR-135","BR-230","BR-242",
                "BR-324","BR-349","BR-407","BR-430","TO-010","PI-112","MA-006"]
    feitas = set()
    for geo_u in ids_mat:
        dists = sorted(
            [(distancia_km(*coords_mat[geo_u], *coords_mat[geo_v]), geo_v)
             for geo_v in ids_mat if geo_v != geo_u]
        )
        for dist, geo_v in dists[:3]:
            chave = (min(geo_u, geo_v), max(geo_u, geo_v))
            if chave in feitas:
                continue
            feitas.add(chave)
            horas = horas_de_viagem(dist, velocidade_media=70)
            tipo = random.choice(["federal","estadual","estadual","municipal"])
            rod  = random.choice(rods_mat)
            w.writerow([geo_u, geo_v, dist, horas, rod, tipo])

print(f"  {len(feitas)} arestas MATOPIBA salvas.")


# ── NDVI mensal (12 meses) para MATOPIBA
print("Gerando ndvi_matopiba.csv ...")
with open(f"{OUTPUT}/ndvi_matopiba.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geocodigo","municipio","uf","mes","ndvi","precipitacao_mm","alerta_seca"])
    for geo, nome, uf, lat, lon, pop in MUNICIPIOS_MATOPIBA:
        ndvi_base = calcular_ndvi(lat, lon)
        for mes in meses:
            # Seca mais intensa em jul-set (estação seca do cerrado)
            fator_ndvi = 0.75 if mes[5:] in ["07","08","09"] else (0.90 if mes[5:] in ["06","10"] else 1.0)
            ndvi_m = round(max(0.05, min(0.85, ndvi_base * fator_ndvi + random.uniform(-0.03, 0.03))), 3)
            precip_m = round(random.uniform(0, 30) if mes[5:] in ["07","08","09"]
                            else random.uniform(60, 200), 1)
            alerta = "SIM" if ndvi_m < 0.25 and precip_m < 30 else "NÃO"
            w.writerow([geo, nome, uf, mes, ndvi_m, precip_m, alerta])

print(f"  {len(MUNICIPIOS_MATOPIBA) * len(meses)} registros NDVI MATOPIBA salvos.")


# ============================================================
# README dos dados brutos
# ============================================================
readme = """# data/raw — Dados Brutos Sintéticos

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
"""
with open(f"{OUTPUT}/README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("\n✓ Todos os arquivos gerados em data/raw/")
print("\nArquivos criados:")
for arq in sorted(os.listdir(OUTPUT)):
    tamanho = os.path.getsize(f"{OUTPUT}/{arq}")
    print(f"  {arq:45s} {tamanho:>8,} bytes")
