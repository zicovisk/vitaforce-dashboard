# ============================================
# GERAR DATASET VITAFORCE — versão local
# Execute este ficheiro UMA vez para criar
# o CSV que o dashboard vai usar
# ============================================

import pandas as pd
import numpy as np
import random
from dateutil import parser

random.seed(42)
np.random.seed(42)

dias       = pd.date_range(start="2024-10-01", end="2024-10-30")
campanhas  = [
    "Suplementos - Pesquisa",
    "Retargeting Carrinho",
    "Awareness Novos Produtos",
    "Promoção Black Friday"
]
canais_sujos = ["Google Ads","GOOGLE","google","Meta Ads","meta","META"]

def formatar_data(data, i):
    if i % 3 == 0: return data.strftime("%Y-%m-%d")
    elif i % 3 == 1: return data.strftime("%d/%m/%Y")
    else: return data.strftime("%b %d %Y")

linhas = []
for i, dia in enumerate(dias):
    for campanha in campanhas:
        canal             = random.choice(canais_sujos)
        inv_val           = round(random.uniform(150, 500), 2)
        fmt               = random.choice(["euro","dolar","puro"])
        if fmt == "euro":   investimento = f"€ {inv_val}"
        elif fmt == "dolar": investimento = f"$ {round(inv_val*0.95,2)}"
        else:               investimento = str(inv_val)
        receita = round(random.uniform(300, 2000), 2)
        if random.random() < 0.10: receita = 0
        if random.random() < 0.03: receita = 999999
        cliques    = random.randint(200, 800)
        if random.random() < 0.03: cliques = -cliques
        impressoes = f"{random.randint(8000,25000):,}".replace(",",".")
        campanha_f = campanha if random.random() > 0.15 else ""
        cpc        = round(random.uniform(0.60,1.20),2)
        if random.random() < 0.20: cpc = None
        linhas.append({
            "data": formatar_data(dia, i),
            "canal": canal, "campanha": campanha_f,
            "investimento": investimento, "receita_gerada": receita,
            "cliques": cliques, "impressoes": impressoes,
            "custo_por_clique": cpc
        })

df = pd.DataFrame(linhas)

# --- LIMPEZA COMPLETA ---
df['canal'] = df['canal'].str.lower().str.strip()
df['canal'] = df['canal'].map({
    'google ads':'Google','google':'Google',
    'meta ads':'Meta','meta':'Meta'
})
df['campanha'] = df['campanha'].replace('', np.nan)
df['campanha'] = df['campanha'].fillna('Campanha Desconhecida')

def limpar_investimento(v):
    v = str(v).strip()
    eh_dolar = '$' in v
    f = float(v.replace('€','').replace('$','').replace(' ',''))
    return round(f * 0.95, 2) if eh_dolar else f

df['investimento']    = df['investimento'].apply(limpar_investimento)
df['receita_gerada']  = df['receita_gerada'].replace({999999:np.nan, 0:np.nan})
df['receita_gerada']  = df.groupby('canal')['receita_gerada']\
                          .transform(lambda x: x.fillna(x.median()))
df['cliques']         = df['cliques'].abs()

if df['impressoes'].dtype == object:
    df['impressoes'] = df['impressoes'].str.replace('.','',regex=False).astype(int)

def converter_data(v):
    for fmt in ["%Y-%m-%d","%d/%m/%Y","%b %d %Y"]:
        try: return pd.to_datetime(v, format=fmt)
        except: continue
    return pd.NaT

df['data'] = df['data'].apply(converter_data)

df.to_csv("vitaforce_limpo.csv", index=False)
print("✅ Dataset criado e limpo!")
print(f"   {len(df)} linhas | Canais: {df['canal'].unique()}")