# ============================================
# VITAFORCE DASHBOARD — Missão 2
# ============================================

import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title = "VitaForce Dashboard",
    page_icon  = "💊",
    layout     = "wide"
)

# ============================================
# CARREGAR OS DADOS
# ============================================
# @st.cache_data diz ao Streamlit para guardar
# os dados na memória — não relê o CSV a cada
# vez que o utilizador clica em algo
# ============================================

@st.cache_data
def carregar_dados():
    df = pd.read_csv("vitaforce_limpo.csv")
    df['data'] = pd.to_datetime(df['data'])
    return df

df = carregar_dados()

# ============================================
# CABEÇALHO
# ============================================

st.title("💊 VitaForce Portugal")
st.subheader("Dashboard de Performance de Campanhas — Outubro 2024")
st.divider()

# ============================================
# FASE 2C — FILTRO LATERAL
# ============================================
# st.sidebar é o painel do lado esquerdo
# Tudo o que colocar aqui aparece na barra lateral
# ============================================

st.sidebar.title("🔧 Filtros")
st.sidebar.markdown("Seleccione os dados que quer ver:")

# Filtro de Canal
canais_disponiveis = ["Todos"] + list(df['canal'].unique())
canal_escolhido = st.sidebar.selectbox(
    label   = "Canal de Publicidade",
    options = canais_disponiveis
)

# Filtro de Campanha
campanhas_disponiveis = ["Todas"] + list(df['campanha'].unique())
campanha_escolhida = st.sidebar.selectbox(
    label   = "Campanha",
    options = campanhas_disponiveis
)

# --- APLICAR FILTROS ---
df_filtrado = df.copy()

if canal_escolhido != "Todos":
    df_filtrado = df_filtrado[df_filtrado['canal'] == canal_escolhido]

if campanha_escolhida != "Todas":
    df_filtrado = df_filtrado[df_filtrado['campanha'] == campanha_escolhida]

# ============================================
# CALCULAR MÉTRICAS COM DADOS FILTRADOS
# ============================================

investimento_total = df_filtrado['investimento'].sum()
receita_total      = df_filtrado['receita_gerada'].sum()
roas_geral         = round(receita_total / investimento_total, 2) if investimento_total > 0 else 0
total_cliques      = df_filtrado['cliques'].sum()
cac                = round(investimento_total / total_cliques, 2) if total_cliques > 0 else 0

# ============================================
# CARTÕES DE MÉTRICAS
# ============================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label = "💰 Investimento Total",
        value = f"€{investimento_total:,.0f}"
    )

with col2:
    st.metric(
        label = "📈 Receita Gerada",
        value = f"€{receita_total:,.0f}"
    )

with col3:
    st.metric(
        label = "🎯 ROAS",
        value = f"{roas_geral}x"
    )

with col4:
    st.metric(
        label = "👤 CAC (por clique)",
        value = f"€{cac}"
    )

# ============================================
# TABELA DE DADOS
# ============================================

st.divider()
st.subheader("📋 Dados Filtrados")
st.caption(f"A mostrar {len(df_filtrado)} registos de {len(df)} totais")

st.dataframe(
    df_filtrado[['data','canal','campanha',
                 'investimento','receita_gerada','cliques']],
    use_container_width = True
)
# ============================================
# GRÁFICOS INTERACTIVOS — PLOTLY
# ============================================

import plotly.express as px

st.divider()
st.subheader("📊 Análise Visual")

# --- GRÁFICO 1: ROAS POR CAMPANHA ---
roas_campanha = df_filtrado.groupby(['canal','campanha']).agg(
    investimento = ('investimento',   'sum'),
    receita      = ('receita_gerada', 'sum')
).reset_index()

roas_campanha['ROAS'] = (
    roas_campanha['receita'] / roas_campanha['investimento']
).round(2)

roas_campanha = roas_campanha.sort_values('ROAS', ascending=True)

fig1 = px.bar(
    roas_campanha,
    x           = 'ROAS',
    y           = 'campanha',
    color       = 'canal',
    orientation = 'h',
    title       = '🎯 ROAS por Campanha',
    color_discrete_map = {
        'Google': '#4285F4',
        'Meta':   '#E05A2B'
    },
    text = 'ROAS',
    labels = {'ROAS': 'ROAS (€ gerado por €1 investido)', 'campanha': ''}
)

fig1.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
fig1.add_vline(x=3, line_dash="dash", line_color="green",
               annotation_text="Meta saudável (3x)")
fig1.update_layout(height=400, showlegend=True)

st.plotly_chart(fig1, use_container_width=True)

# --- GRÁFICO 2: INVESTIMENTO DIÁRIO ---
invest_diario = df_filtrado.groupby(['data','canal']).agg(
    investimento = ('investimento', 'sum')
).reset_index()

fig2 = px.line(
    invest_diario,
    x     = 'data',
    y     = 'investimento',
    color = 'canal',
    title = '📅 Investimento Diário por Canal',
    color_discrete_map = {
        'Google': '#4285F4',
        'Meta':   '#E05A2B'
    },
    labels = {
        'data':         'Data',
        'investimento': 'Investimento (€)',
        'canal':        'Canal'
    }
)

fig2.update_traces(mode='lines+markers')
fig2.update_layout(height=350)

st.plotly_chart(fig2, use_container_width=True)