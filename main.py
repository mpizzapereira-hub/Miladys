import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# Inteligência Artificial
from sklearn.linear_model import LinearRegression

# Relatórios PDF Profissionais
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E ESTILIZAÇÃO CSS REFINADA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTwin | Monitoramento & Inteligência Ambiental",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Roteamento do Clique no Aero Widget
query_params = st.query_params
if "nav" in query_params and query_params["nav"] == "aero":
    st.session_state.active_tab = 4  # Índice 4 = Aba 5 (Chat Aero)
    st.query_params.clear()

if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

if "vazamentos" not in st.session_state:
    st.session_state.vazamentos = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🤖 **Olá! Eu sou o Aero!** Seu copiloto de sustentabilidade na FECART. Como posso analisar o seu consumo ou apoiar sua meta ecológica hoje?"}
    ]

# Inicializações de estado para cálculos transversais e PDF consolidado
if "calc_banho" not in st.session_state:
    st.session_state.calc_banho = 15
if "calc_transp" not in st.session_state:
    st.session_state.calc_transp = 10
if "calc_carne" not in st.session_state:
    st.session_state.calc_carne = 4
if "calc_lixo" not in st.session_state:
    st.session_state.calc_lixo = 5
if "area_plantio" not in st.session_state:
    st.session_state.area_plantio = 120
if "quiz_acertos" not in st.session_state:
    st.session_state.quiz_acertos = 0
if "quiz_respondido" not in st.session_state:
    st.session_state.quiz_respondido = False

# CSS Customizado (Verde Escuro Refinado + Efeito 3D Fazendinha + Aero)
st.markdown("""
    <style>
    /* Fundo e Tipografia Global */
    .stApp {
        background-color: #0E231A;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        color: #ECFDF5 !important;
    }
    p, span, label, div, li { color: #E2E8F0 !important; }
    h1, h2, h3, h4 { color: #34D399 !important; font-weight: 700 !important; margin-bottom: 0.5rem; }
    
    /* Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #081610;
        border-right: 1px solid #1C3A2D;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #CBD5E1 !important;
        font-weight: 600;
    }
    
    /* Abas Customizadas com Transição Suave */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #1C3A2D;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #152E23;
        border-radius: 12px 12px 4px 4px !important;
        color: #A7F3D0 !important;
        font-weight: 600;
        font-size: 0.9rem !important;
        padding: 10px 16px !important;
        border: 1px solid #234737;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1C3A2D;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        border-color: #34D399;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: #FFFFFF !important;
        border-color: #34D399;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* Cards Informativos e Métricos */
    .eco-card {
        background: #152E23;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #10B981;
        border: 1px solid #234737;
        margin-bottom: 18px;
        transition: all 0.25s ease;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
    }
    .eco-card:hover {
        transform: translateY(-2px);
        border-color: #34D399;
        box-shadow: 0 8px 18px rgba(16, 185, 129, 0.2);
    }

    /* ------------------------------------------------------------- */
    /* EFEITO VISUAL 3D / PROFUNDIDADE DA FAZENDINHA ECOTWIN         */
    /* ------------------------------------------------------------- */
    .farm-viewport {
        perspective: 1000px;
        background: radial-gradient(circle at 50% 25%, #183d2c 0%, #0a1b13 100%);
        border: 2px solid #234737;
        border-radius: 18px;
        padding: 30px 25px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7), inset 0 2px 8px rgba(52, 211, 153, 0.3);
        margin: 20px 0;
        position: relative;
        overflow: hidden;
    }
    .farm-header-badge {
        display: inline-block;
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: #ffffff;
        font-weight: 800;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4);
    }
    .farm-grid-3d {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 16px;
        transform: rotateX(16deg);
        transform-style: preserve-3d;
        padding: 15px 5px;
    }
    .farm-block {
        background: linear-gradient(145deg, #1d4633 0%, #112d21 100%);
        border-radius: 14px;
        padding: 16px 10px;
        text-align: center;
        border: 1px solid rgba(52, 211, 153, 0.25);
        border-bottom: 5px solid #091710;
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .farm-block:hover {
        transform: translateY(-8px) translateZ(10px) scale(1.04);
        box-shadow: 0 18px 25px rgba(16, 185, 129, 0.35);
        border-color: #34D399;
    }
    .farm-emoji {
        font-size: 2.5rem;
        display: block;
        margin-bottom: 6px;
        filter: drop-shadow(0 6px 8px rgba(0, 0, 0, 0.45));
    }
    .farm-name {
        font-size: 0.82rem;
        font-weight: 800;
        color: #ECFDF5;
        margin-bottom: 2px;
    }
    .farm-desc {
        font-size: 0.7rem;
        color: #9AE6B4;
        line-height: 1.1;
    }

    /* Widget Flutuante do Aero */
    .aero-widget-link {
        position: fixed;
        bottom: 20px;
        right: 25px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        text-decoration: none !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .aero-widget-link:hover {
        transform: scale(1.05) translateY(-3px);
    }
    .aero-bubble {
        background: #FFFFFF;
        color: #0F172A !important;
        padding: 8px 14px;
        border-radius: 12px 12px 2px 12px;
        font-weight: 700;
        font-size: 13px;
        border: 2px solid #10B981;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .aero-avatar {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        border: 2px solid #A7F3D0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Widget Flutuante Aero Clicável
st.markdown("""
    <a href="?nav=aero" target="_self" class="aero-widget-link" title="Abrir Consultoria com o Aero">
        <div class="aero-bubble">Olá, sou o Aero</div>
        <div class="aero-avatar">🤖</div>
    </a>
""", unsafe_allow_html=True)

st.title("🌱 EcoTwin | Monitoramento & Inteligência Ambiental")
st.caption("Plataforma Interativa para Simulação de Sustentabilidade, Gêmeo Digital e Auditoria Ecológica")

# -----------------------------------------------------------------------------
# DADOS GLOBAIS E SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.header("🏠 Consumo Residencial Geral")
moradores = st.sidebar.number_input("Número de Moradores", min_value=1, max_value=50, value=4, step=1)
energia_kwh = st.sidebar.number_input("Energia Elétrica Mensal (kWh)", min_value=10, max_value=10000, value=220, step=10)
meta_reducao = st.sidebar.slider("Meta de Redução de Emissões (%)", min_value=5, max_value=50, value=15, step=5)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica do Projeto:** Pequenas mudanças de 10% a 15% na rotina de uma comunidade geram economia de milhões de litros de água e toneladas de CO₂.")

# -----------------------------------------------------------------------------
# CÁLCULOS BASE DE ENERGIA E PEGADA
# -----------------------------------------------------------------------------
co2_energia_ano = energia_kwh * 0.085 * 12
# Estimativa de emissão indireta da moradia (gás, água encanada e consumo comum)
co2_base_moradia = moradores * 160.0
co2_total_ano = co2_energia_ano + co2_base_moradia
arvores_necessarias_base = int(np.ceil(co2_total_ano / 15.0))
co2_evitado_meta = co2_total_ano * (meta_reducao / 100.0)
arvores_salvas_meta = int(np.ceil(co2_evitado_meta / 15.0))

# -----------------------------------------------------------------------------
# DEFINIÇÃO DAS 8 ABAS INTEGRADAS
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "📊 Diagnóstico", 
    "🧮 Calculadora Pessoal", 
    "🌳 Carbon Twin", 
    "🧠 Modelo de IA", 
    "🤖 Chat Aero", 
    "📝 Quiz & Gamificação", 
    "🔍 Vazamentos", 
    "📄 Relatórios PDF"
])

# Roteador de aba ativa via Aero
if st.session_state.active_tab == 4:
    st.session_state.active_tab = 0
    st.rerun()

# =============================================================================
# 1. ABA: DIAGNÓSTICO
# =============================================================================
with tabs[0]:
    st.header("📊 Diagnóstico de Impacto Ambiental Integrado")
    st.write("Visão holística das emissões de gases de efeito estufa e potencial de mitigação da instalação.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pegada Estimada", f"{co2_total_ano:,.0f} kg CO₂e/ano", f"-{meta_reducao}% na meta", delta_color="inverse")
    c2.metric("Consumo Mensal", f"{energia_kwh:,.0f} kWh/mês", "Rede Elétrica")
    c3.metric("Árvores p/ Compensar", f"{arvores_necessarias_base} árvores", "Dívida ecológica", delta_color="inverse")
    c4.metric("Mitigação com Meta", f"{co2_evitado_meta:,.0f} kg CO₂e", f"{arvores_salvas_meta} árvores poupadas")

    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Distribuição do Impacto de Emissões")
        df_donut = pd.DataFrame({
            "Categoria": ["Eletricidade Geral", "Impacto Hídrico & Gás", "Transporte da Rotina", "Resíduos Sólidos"],
            "Emissão (kg CO₂e/ano)": [co2_energia_ano, co2_base_moradia * 0.45, co2_base_moradia * 0.35, co2_base_moradia * 0.20]
        })
        fig_donut = px.pie(
            df_donut, 
            values="Emissão (kg CO₂e/ano)", 
            names="Categoria", 
            hole=0.52,
            color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6']
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#E2E8F0'),
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_g2:
        st.subheader("Cenário Atual vs Cenário Otimizado (Meta)")
        df_bar = pd.DataFrame({
            "Cenário": ["Cenário Atual", f"Com Meta de {meta_reducao}%"],
            "Emissão (kg CO₂e/ano)": [co2_total_ano, co2_total_ano - co2_evitado_meta]
        })
        fig_bar = px.bar(
            df_bar, 
            x="Cenário", 
            y="Emissão (kg CO₂e/ano)", 
            color="Cenário", 
            text="Emissão (kg CO₂e/ano)",
            color_discrete_sequence=['#EF4444', '#10B981']
        )
        fig_bar.update_traces(texttemplate='%{text:,.0f} kg', textposition='outside')
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#E2E8F0'),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f"""
        <div class="eco-card">
            <h4>💡 Conclusão do Diagnóstico Operacional</h4>
            <p>Seus <b>{moradores} ocupantes</b> geram anualmente <b>{co2_total_ano:,.1f} kg de CO₂e</b>. Ao cumprir sua meta de redução de <b>{meta_reducao}%</b>, você deixará de lançar na atmosfera o equivalente a <b>{co2_evitado_meta:,.1f} kg de carbono</b>, salvando o trabalho de <b>{arvores_salvas_meta} árvores adultas</b> todo ano!</p>
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 2. ABA: CALCULADORA PESSOAL
# =============================================================================
with tabs[1]:
    st.header("🧮 Calculadora de Impacto Pessoal & Hábitos")
    st.write("Ajuste seus hábitos cotidianos e veja a comparação imediata com as médias populacionais brasileiras.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.calc_banho = st.slider("Tempo médio de banho diário (minutos)", min_value=3, max_value=60, value=st.session_state.calc_banho, step=1)
        st.session_state.calc_transp = st.slider("Deslocamento diário em veículo próprio fóssil (km)", min_value=0, max_value=120, value=st.session_state.calc_transp, step=2)
    with col_c2:
        st.session_state.calc_carne = st.slider("Consumo semanal de carne vermelha (dias/semana)", min_value=0, max_value=7, value=st.session_state.calc_carne, step=1)
        st.session_state.calc_lixo = st.slider("Geração de sacos de lixo de 50L (sacos/semana)", min_value=1, max_value=25, value=st.session_state.calc_lixo, step=1)

    st.markdown("### 📈 Comparativo Direto com a Média Nacional Brasileira")
    mc1, mc2, mc3, mc4 = st.columns(4)
    
    # Parâmetros de referência brasileira (Fontes: IBGE / Sabesp / EPE)
    delta_banho = st.session_state.calc_banho - 12
    delta_transp = st.session_state.calc_transp - 15
    delta_carne = st.session_state.calc_carne - 3
    delta_lixo = st.session_state.calc_lixo - 4

    mc1.metric("Banho Diário", f"{st.session_state.calc_banho} min", f"{delta_banho:+d} min vs Média BR (12m)", delta_color="inverse")
    mc2.metric("Transporte Diário", f"{st.session_state.calc_transp} km", f"{delta_transp:+d} km vs Média BR (15km)", delta_color="inverse")
    mc3.metric("Carne Vermelha", f"{st.session_state.calc_carne} dias/sem", f"{delta_carne:+d} dias vs Média BR (3d)", delta_color="inverse")
    mc4.metric("Descarte de Lixo", f"{st.session_state.calc_lixo} sacos/sem", f"{delta_lixo:+d} sacos vs Média BR (4s)", delta_color="inverse")

    st.info("📌 **Critério Técnico:** Em indicadores de pegada de carbono e hídrica, valores **abaixo da média nacional** (verdes) são excelentes para o meio ambiente, enquanto valores superiores (vermelhos) demandam atenção.")

# =============================================================================
# 3. ABA: CARBON TWIN (SIMULAÇÃO DE ÁRVORES & FAZENDINHA 3D)
# =============================================================================
with tabs[2]:
    st.header("🌳 Carbon Twin | Gêmeo Digital & Fazendinha 3D")
    st.write("Explore seu débito de carbono através de simulação de área reflorestada e uma fazenda virtual imersiva.")

    st.markdown("""
        <div class="eco-card">
            <h4>🌿 Entendendo o Conceito do Carbon Twin</h4>
            <p>O <b>Gêmeo Digital Florestal</b> espelha as atividades poluidoras humanas em equivalentes de biomassa viva. Uma árvore nativa brasileira em crescimento absorve em média <b>15 kg de CO₂ por ano</b>. Aqui você calcula seu equilíbrio bioecológico em tempo real.</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("1. Simulador Interativo de Reflorestamento & Área de Plantio")
    st.session_state.area_plantio = st.slider(
        "Área física disponível para plantio / quintal / reflorestamento (m²)",
        min_value=10,
        max_value=3000,
        value=st.session_state.area_plantio,
        step=10,
        help="Espaçamento técnico recomendado: cerca de 10 a 12 m² por árvore de copa nativa para desenvolvimento pleno."
    )

    # Cálculos florestais em tempo real
    capacidade_mudas = int(st.session_state.area_plantio / 12)
    absorcao_anual_mudas = capacidade_mudas * 15.0
    saldo_carbono = co2_total_ano - absorcao_anual_mudas
    cobertura_pct = min(100.0, (absorcao_anual_mudas / co2_total_ano) * 100.0) if co2_total_ano > 0 else 100.0

    col_sim1, col_sim2, col_sim3 = st.columns(3)
    col_sim1.metric("Capacidade de Árvores na Área", f"{capacidade_mudas} árvores", f"{st.session_state.area_plantio} m² de solo")
    col_sim2.metric("Absorção Anual do Plantio", f"{absorcao_anual_mudas:,.0f} kg CO₂/ano", "Biomassa Viva")
    col_sim3.metric("Cobertura da sua Pegada", f"{cobertura_pct:.1f}%", f"{'Totalmente Neutro!' if saldo_carbono <= 0 else f'Faltam {saldo_carbono:,.0f} kg'}")

    st.markdown("---")
    st.subheader("2. Fazendinha Virtual EcoTwin 3D (Ecossistema Vivo)")
    st.write("A fazendinha ganha vida e novos elementos à medida que você aumenta sua meta de redução ou amplia o plantio de mudas:")

    # Lógica de evolução dinâmica da fazendinha 3D baseada em sustentabilidade
    pontuacao_fazenda = (meta_reducao * 2) + min(60, capacidade_mudas * 3)
    if pontuacao_fazenda >= 70:
        nivel_fazenda = "Oásis Regenerativo Sustentável (Nível 4 - Ouro)"
        itens_fazenda = [
            ("☀️", "Energia Solar", "Microgeração Fotovoltaica"),
            ("🌳", "Mata Nativa", "Espécies de Dossel Alto"),
            ("🍎", "Pomar Produtivo", "Frutas sem Agrotóxicos"),
            ("🐝", "Apiário Ativo", "Polinização Natural"),
            ("💧", "Cisterna Pluvial", "Reúso de Água da Chuva"),
            ("🌽", "Agrofloresta", "Consórcio Milho & Legumes"),
            ("🐑", "Pasto Rotativo", "Manejo com Baixa Emissão"),
            ("🏡", "Eco-Residência", "Construção Bioclimática")
        ]
    elif pontuacao_fazenda >= 45:
        nivel_fazenda = "Fazenda Agroecológica em Transição (Nível 3 - Prata)"
        itens_fazenda = [
            ("🌳", "Árvores Frutíferas", "Reflorestamento Ativo"),
            ("🍊", "Citros Orgânicos", "Absorção de Carbono"),
            ("🥕", "Horta Familiar", "Consumo Local"),
            ("🐔", "Aves Livres", "Produção de Subsistência"),
            ("💧", "Poço Ecológico", "Manejo Hídrico"),
            ("🌾", "Cereal Sustentável", "Cobertura de Solo")
        ]
    elif pontuacao_fazenda >= 25:
        nivel_fazenda = "Sítio em Desenvolvimento Ecológico (Nível 2 - Bronze)"
        itens_fazenda = [
            ("🌱", "Mudas Nativas", "Plantio em Crescimento"),
            ("🌾", "Solo Preparado", "Recuperação Orgânica"),
            ("🍎", "Árvores Jovens", "Começo da Absorção"),
            ("💧", "Ponto de Irrigação", "Gotejamento Eficiente")
        ]
    else:
        nivel_fazenda = "Área Inicial em Recuperação (Nível 1 - Básico)"
        itens_fazenda = [
            ("🌱", "Primeiros Brotos", "Solo Descompactado"),
            ("🌾", "Capim Protetor", "Evitando Erosão"),
            ("🚜", "Preparo Agroecológico", "Transição Verde")
        ]

    # Renderização visual rica em HTML/CSS com grid 3D
    blocos_html = "".join([f"""
        <div class="farm-block">
            <span class="farm-emoji">{emoji}</span>
            <div class="farm-name">{nome}</div>
            <div class="farm-desc">{desc}</div>
        </div>
    """ for emoji, nome, desc in itens_fazenda])

    st.markdown(f"""
        <div class="farm-viewport">
            <div class="farm-header-badge">{nivel_fazenda}</div>
            <div class="farm-grid-3d">
                {blocos_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.caption(f"🌲 **Floresta de Compensação Bruta:** Para neutralizar totalmente seus {co2_total_ano:,.0f} kg CO₂ anuais sem área de plantio, seriam necessárias **{arvores_necessarias_base} árvores adultas**.")
    grid_arvores = "🌳 " * min(arvores_necessarias_base, 120)
    st.markdown(f"<div style='font-size: 20px; line-height: 1.6; background: #0A1C14; padding: 14px; border-radius: 10px; border: 1px solid #1C3A2D;'>{grid_arvores}</div>", unsafe_allow_html=True)

# =============================================================================
# 4. ABA: MODELO DE IA (PROJEÇÃO REGRESSIVA)
# =============================================================================
with tabs[3]:
    st.header("🧠 Modelo de IA | Projeção e Regressão Linear")
    st.write("Aplicação real de Machine Learning utilizando Scikit-Learn para prever tendências energéticas e identificar padrões.")

    meses_hist = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    # Simulação realista baseada no patamar informado pelo usuário
    consumo_hist = np.array([
        energia_kwh * 0.90, 
        energia_kwh * 0.94, 
        energia_kwh * 1.04, 
        energia_kwh * 0.97, 
        energia_kwh * 1.03, 
        energia_kwh * 1.00
    ])

    # Treinamento do Modelo OLS
    modelo_reg = LinearRegression()
    modelo_reg.fit(meses_hist, consumo_hist)

    meses_futuros = np.array([7, 8, 9]).reshape(-1, 1)
    previsoes_ia = modelo_reg.predict(meses_futuros)

    fig_ml = go.Figure()
    fig_ml.add_trace(go.Scatter(
        x=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        y=consumo_hist,
        mode='lines+markers',
        name='Consumo Histórico Real',
        line=dict(color='#10B981', width=3),
        marker=dict(size=8)
    ))
    fig_ml.add_trace(go.Scatter(
        x=["Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"],
        y=[consumo_hist[-1]] + list(previsoes_ia),
        mode='lines+markers',
        name='Projeção Linear (IA)',
        line=dict(color='#3B82F6', width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))
    fig_ml.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        margin=dict(t=25, b=20, l=20, r=20),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_ml, use_container_width=True)

    st.info(f"💡 **Diagnóstico Preditivo:** O modelo estima um consumo médio projetado de **{previsoes_ia.mean():,.1f} kWh** para os próximos três meses. Para inverter a inclinação da reta, foque na redução de equipamentos em modo standby e controle térmico.")

# =============================================================================
# 5. ABA: CHAT AERO (CONSULTORIA INTERATIVA)
# =============================================================================
with tabs[4]:
    st.header("🤖 Consultoria Inteligente com o Assistente Aero")
    st.write("Converse com o copiloto que analisa em tempo real os dados preenchidos no seu painel.")

    st.markdown("**💡 Perguntas Rápidas Sugeridas:**")
    qb1, qb2, qb3 = st.columns(3)
    perg_clicada = None
    if qb1.button("⚡ Como economizar energia rápida?"):
        perg_clicada = "Como posso reduzir minha conta de energia rapidamente?"
    if qb2.button("🌳 Qual é o benefício da minha fazendinha?"):
        perg_clicada = "Como a fazendinha 3D me ajuda a compensar meu consumo?"
    if qb3.button("💧 Qual o impacto do meu tempo de banho?"):
        perg_clicada = "Como o tempo de banho afeta minha pegada hídrica?"

    st.markdown("---")

    # Renderiza mensagens anteriores
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    input_prompt = st.chat_input("Pergunte ao Aero sobre sustentabilidade, energia ou seus cálculos...")
    prompt_final = perg_clicada or input_prompt

    if prompt_final:
        st.session_state.messages.append({"role": "user", "content": prompt_final})
        with st.chat_message("user"):
            st.markdown(prompt_final)

        with st.chat_message("assistant"):
            texto_baixo = prompt_final.lower()
            if "energia" in texto_baixo or "kwh" in texto_baixo or "conta" in texto_baixo:
                resp = f"⚡ **Análise do Aero:** Você consome **{energia_kwh} kWh/mês**. Ao bater sua meta de **{meta_reducao}%**, você economizará cerca de **{energia_kwh * (meta_reducao/100):,.0f} kWh/mês** (aproximadamente R$ {energia_kwh * (meta_reducao/100) * 0.75:,.2f} todo mês)."
            elif "fazendinha" in texto_baixo or "árvore" in texto_baixo or "plantio" in texto_baixo:
                resp = f"🌳 **Análise do Aero:** Com seus **{st.session_state.area_plantio} m²** simulados, você consegue abrigar até **{capacidade_mudas} árvores nativas**, absorvendo **{absorcao_anual_mudas:,.0f} kg de CO₂/ano**!"
            elif "banho" in texto_baixo or "água" in texto_baixo:
                resp = f"🚿 **Análise do Aero:** Seu banho diário é de **{st.session_state.calc_banho} minutos**. Se você reduzir apenas 2 minutos, poupará mais de **540 litros de água tratada por mês** por pessoa!"
            else:
                resp = f"🌱 **Dica do Aero:** Monitorar seus hábitos residenciais é o primeiro passo para cidades inteligentes. Dê uma olhada no Quiz e na Calculadora Pessoal para turbinar seus resultados!"

            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# =============================================================================
# 6. ABA: QUIZ & GAMIFICAÇÃO (10 PERGUNTAS DESAFIADORAS)
# =============================================================================
with tabs[5]:
    st.header("📝 Quiz & Gamificação: 10 Desafios Mito ou Verdade")
    st.write("Teste seu conhecimento ecológico. Cada acerto fortalece sua pontuação e dispara recompensas visuais!")

    # Banco com 10 Perguntas Desafiadoras e Educativas
    perguntas_quiz = [
        {
            "id": "q1",
            "enunciado": "1. Deixar aparelhos eletrônicos em stand-by (luzinha vermelha acesa) não consome energia elétrica relevante.",
            "correta": "Mito",
            "explicacao": "Mito! O consumo passivo ou 'fantasma' de aparelhos em stand-by pode responder por até 10% a 12% da conta de luz residencial."
        },
        {
            "id": "q2",
            "enunciado": "2. A pecuária extensiva é uma das principais fontes antropogênicas mundiais de emissão de gás metano (CH₄).",
            "correta": "Verdade",
            "explicacao": "Verdade! O processo de fermentação entérica de ruminantes responde por parcela expressiva das emissões mundiais de metano."
        },
        {
            "id": "q3",
            "enunciado": "3. Um banho de 15 minutos em chuveiro elétrico pode gastar mais de 100 litros de água tratada.",
            "correta": "Verdade",
            "explicacao": "Verdade! Chuveiros comuns têm vazão média de 9 a 14 litros por minuto, ultrapassando facilmente 130 litros em 15 minutos."
        },
        {
            "id": "q4",
            "enunciado": "4. Uma sacola plástica descartada na natureza leva em média menos de 10 anos para se degradar totalmente.",
            "correta": "Mito",
            "explicacao": "Mito! Sacolas plásticas comuns levam entre 100 e 400 anos para se decompor, fragmentando-se em microplásticos nocivos."
        },
        {
            "id": "q5",
            "enunciado": "5. Painéis solares fotovoltaicos param totalmente de produzir energia elétrica em dias nublados ou com chuva.",
            "correta": "Mito",
            "explicacao": "Mito! Os módulos fotovoltaicos continuam captando e convertendo radiação solar difusa mesmo sob céu nublado."
        },
        {
            "id": "q6",
            "enunciado": "6. Lâmpadas LED consomem até 80% menos eletricidade do que as antigas lâmpadas incandescentes.",
            "correta": "Verdade",
            "explicacao": "Verdade! O LED converte a maior parte da energia diretamente em luz, enquanto incandescentes perdiam 90% em calor."
        },
        {
            "id": "q7",
            "enunciado": "7. O vidro é um material 100% reciclável que pode ser reaproveitado infinitas vezes sem perder qualidade.",
            "correta": "Verdade",
            "explicacao": "Verdade! 1 kg de cacos de vidro limpos rende exatamente 1 kg de vidro novo em ciclos contínuos."
        },
        {
            "id": "q8",
            "enunciado": "8. A fabricação de uma única calça jeans nova pode consumir até 10.000 litros de água ao longo da sua cadeia produtiva.",
            "correta": "Verdade",
            "explicacao": "Verdade! Segundo a UNESCO, a irrigação do algodão e os processos de tingimento consomem cerca de 8.000 a 10.000 L por peça."
        },
        {
            "id": "q9",
            "enunciado": "9. Manter o carregador de celular na tomada sem aparelho conectado não consome eletricidade alguma.",
            "correta": "Mito",
            "explicacao": "Mito! O transformador interno consome uma carga residual constante por indução (cerca de 0,1W a 0,5W contínuos)."
        },
        {
            "id": "q10",
            "enunciado": "10. Cerca de 80% do plástico que polui os oceanos tem origem em cidades e atividades em terra firme.",
            "correta": "Verdade",
            "explicacao": "Verdade! A maior parte do lixo marinho é carreada por rios, esgotos e chuvas a partir de áreas urbanas continentais."
        }
    ]

    respostas_usuario = {}
    col_q1, col_q2 = st.columns(2)

    for i, p in enumerate(perguntas_quiz):
        col = col_q1 if i < 5 else col_q2
        with col:
            respostas_usuario[p["id"]] = st.radio(
                p["enunciado"],
                ["Não respondido", "Mito", "Verdade"],
                key=f"quiz_radio_{p['id']}"
            )

    st.markdown("---")
    if st.button("🎯 Submeter Respostas & Conferir Desempenho", use_container_width=True):
        acertos = 0
        detalhes_feedback = []

        for p in perguntas_quiz:
            resp = respostas_usuario[p["id"]]
            if resp == p["correta"]:
                acertos += 1
                detalhes_feedback.append((True, p["enunciado"], p["explicacao"]))
            else:
                detalhes_feedback.append((False, p["enunciado"], p["explicacao"]))

        st.session_state.quiz_acertos = acertos
        st.session_state.quiz_respondido = True

        # Gamificação e Recompensa Visual
        if acertos >= 7:
            st.balloons()
            st.success(f"🎉 **EXCELENTE RESULTADO!** Você acertou **{acertos}/10** perguntas!")
        elif acertos >= 5:
            st.info(f"🌱 **BOM DESEMPENHO!** Você acertou **{acertos}/10** perguntas!")
        else:
            st.warning(f"💡 **APRENDIZADO EM ANDAMENTO:** Você acertou **{acertos}/10** perguntas.")

        st.progress(acertos / 10.0)

        # Resumo Interativo de Desempenho
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Placar Final", f"{acertos} / 10", f"{(acertos/10)*100:.0f}% de Precisão")
        
        if acertos == 10:
            rank_quiz = "🏆 Mestre Supremo da Sustentabilidade"
        elif acertos >= 8:
            rank_quiz = "🌟 Guardião Ecológico de Elite"
        elif acertos >= 5:
            rank_quiz = "🌿 Cidadão Consciente em Ação"
        else:
            rank_quiz = "🌱 Aprendiz do Meio Ambiente"
            
        rc2.metric("Título Conquistado", rank_quiz)
        rc3.metric("Status no Laudo", "Salvo para o PDF")

        with st.expander("🔍 Ver Gabarito Técnico e Justificativas Educativas"):
            for correta, texto, exp in detalhes_feedback:
                if correta:
                    st.write(f"✅ **{texto}**")
                else:
                    st.write(f"❌ **{texto}**")
                st.caption(f"↳ *Explicação:* {exp}")

# =============================================================================
# 7. ABA: VAZAMENTOS (AUDITORIA E SIMULADOR HÍDRICO)
# =============================================================================
with tabs[6]:
    st.header("🔍 Auditoria de Perdas e Vazamentos Hídricos")
    st.write("Identifique pontos de desperdício na tubulação e registre ocorrências técnicas.")

    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        local_vaz = st.selectbox("Ponto de Anomalia Detectado", [
            "Torneira Pingando Lenta", 
            "Torneira Pingando Rápida", 
            "Caixa Acoplada / Vaso Sanitário com Filete", 
            "Chuveiro com Gotejamento Contínuo",
            "Cano Subterrâneo com Infiltração"
        ])
        intensidade_vaz = st.slider("Severidade / Frequência do Gotejamento (Escala 1 a 10)", min_value=1, max_value=10, value=4)
        
        # Fórmula paramétrica de perda hídrica mensal em litros
        perda_litros_mes = intensidade_vaz * 30 * 25
        custo_estimado_rs = perda_litros_mes * 0.018 # Tarifa média de água e esgoto

        st.warning(f"💧 **Desperdício Calculado:** {perda_litros_mes:,.0f} Litros/mês (Prejuízo orçamentário: ~R$ {custo_estimado_rs:,.2f}/mês)")

        if st.button("➕ Registrar Ocorrência na Auditoria", use_container_width=True):
            st.session_state.vazamentos.append({
                "Local": local_vaz,
                "Severidade": f"Nível {intensidade_vaz}/10",
                "Perda Estimada (L/mês)": perda_litros_mes,
                "Impacto Financeiro (R$/mês)": f"R$ {custo_estimado_rs:,.2f}"
            })
            st.success("Ocorrência adicionada com sucesso ao histórico!")

    with col_v2:
        st.subheader("📋 Histórico de Ocorrências Registradas")
        if st.session_state.vazamentos:
            df_vazamentos = pd.DataFrame(st.session_state.vazamentos)
            st.dataframe(df_vazamentos, use_container_width=True)
            total_perdido_mes = sum([item["Perda Estimada (L/mês)"] for item in st.session_state.vazamentos])
            st.error(f"🚨 **Perda Hídrica Acumulada:** {total_perdido_mes:,.0f} Litros de água potável por mês!")
            if st.button("🗑️ Limpar Registro de Vazamentos"):
                st.session_state.vazamentos = []
                st.rerun()
        else:
            st.info("Nenhum vazamento registrado no momento. Todas as torneiras e conexões estão operando perfeitamente!")

# =============================================================================
# 8. ABA: RELATÓRIOS PDF CONSOLIDADO (REPORTLAB COMPLETO)
# =============================================================================
with tabs[7]:
    st.header("📄 Emissão do Laudo Técnico Consolidado (PDF)")
    st.write("Gere um documento profissional em PDF contendo **todas as métricas**, cálculos e registros integrados de todas as abas do sistema.")

    def gerar_pdf_consolidado():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        # Estilos Customizados
        style_title = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#065F46'))
        style_sub = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#374151'))
        style_h2 = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#059669'), spaceBefore=10, spaceAfter=4)
        style_cell = ParagraphStyle('CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
        style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12)

        elements = []

        # Cabeçalho Principal
        elements.append(Paragraph("🌱 Laudo Técnico de Inteligência Ambiental - EcoTwin", style_title))
        elements.append(Paragraph("Documento Técnico de Avaliação, Pegada de Carbono, Hábitos e Auditoria de Recursos", style_sub))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=2, spaceAfter=10))

        # 1. Dados da Instalação e Energia
        elements.append(Paragraph("1. Diagnóstico Geral da Instalação Residencial", style_h2))
        dados_diag = [
            [Paragraph("<b>Indicador Técnico</b>", style_cell_bold), Paragraph("<b>Valor Registrado</b>", style_cell_bold)],
            [Paragraph("Ocupantes / Moradores", style_cell), Paragraph(f"{moradores} pessoas", style_cell)],
            [Paragraph("Consumo Mensal de Eletricidade", style_cell), Paragraph(f"{energia_kwh:,.0f} kWh/mês", style_cell)],
            [Paragraph("Pegada Anual Total Estimada", style_cell), Paragraph(f"{co2_total_ano:,.1f} kg CO₂e/ano", style_cell)],
            [Paragraph("Meta de Otimização Voluntária", style_cell), Paragraph(f"{meta_reducao}% de redução", style_cell)],
            [Paragraph("Emissões Mitigadas com a Meta", style_cell), Paragraph(f"{co2_evitado_meta:,.1f} kg CO₂e/ano", style_cell)],
            [Paragraph("Equivalência em Árvores Poupadas", style_cell), Paragraph(f"{arvores_salvas_meta} árvores adultas/ano", style_cell)]
        ]
        t1 = Table(dados_diag, colWidths=[270, 260])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FAFB'), colors.HexColor('#F0FDF4')]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t1)
        elements.append(Spacer(1, 10))

        # 2. Calculadora de Impacto Pessoal
        elements.append(Paragraph("2. Hábitos e Consumo Individual (Comparativo Nacional)", style_h2))
        dados_habitos = [
            [Paragraph("<b>Hábito Pessoal Auditado</b>", style_cell_bold), Paragraph("<b>Parâmetro Informado</b>", style_cell_bold), Paragraph("<b>Diferencial vs Média BR</b>", style_cell_bold)],
            [Paragraph("Duração Média de Banho", style_cell), Paragraph(f"{st.session_state.calc_banho} min/dia", style_cell), Paragraph(f"{delta_banho:+d} min (Ref: 12 min)", style_cell)],
            [Paragraph("Deslocamento com Veículo Fóssil", style_cell), Paragraph(f"{st.session_state.calc_transp} km/dia", style_cell), Paragraph(f"{delta_transp:+d} km (Ref: 15 km)", style_cell)],
            [Paragraph("Consumo de Carne Vermelha", style_cell), Paragraph(f"{st.session_state.calc_carne} dias/semana", style_cell), Paragraph(f"{delta_carne:+d} dias (Ref: 3 dias)", style_cell)],
            [Paragraph("Geração de Resíduos Sólidos", style_cell), Paragraph(f"{st.session_state.calc_lixo} sacos 50L/sem", style_cell), Paragraph(f"{delta_lixo:+d} sacos (Ref: 4 sacos)", style_cell)]
        ]
        t2 = Table(dados_habitos, colWidths=[200, 160, 170])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FAFB'), colors.HexColor('#F0FDF4')]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 10))

        # 3. Carbon Twin e Fazendinha 3D
        elements.append(Paragraph("3. Status do Carbon Twin & Fazendinha EcoTwin", style_h2))
        dados_twin = [
            [Paragraph("<b>Indicador do Gêmeo Digital</b>", style_cell_bold), Paragraph("<b>Valores do Modelo</b>", style_cell_bold)],
            [Paragraph("Dívida Ecológica Bruta (Árvores Necessárias)", style_cell), Paragraph(f"{arvores_necessarias_base} árvores nativas adultas", style_cell)],
            [Paragraph("Área Simulada para Plantio / Reflorestamento", style_cell), Paragraph(f"{st.session_state.area_plantio} m²", style_cell)],
            [Paragraph("Capacidade de Acomodação de Mudas", style_cell), Paragraph(f"{capacidade_mudas} mudas de árvores", style_cell)],
            [Paragraph("Absorção Anual Esperada do Plantio", style_cell), Paragraph(f"{absorcao_anual_mudas:,.1f} kg CO₂e/ano", style_cell)],
            [Paragraph("Nível da Fazendinha EcoTwin 3D Atingido", style_cell), Paragraph(f"{nivel_fazenda}", style_cell)]
        ]
        t3 = Table(dados_twin, colWidths=[270, 260])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#047857')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FAFB'), colors.HexColor('#F0FDF4')]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t3)
        elements.append(Spacer(1, 10))

        # 4. Desempenho no Quiz de Gamificação
        elements.append(Paragraph("4. Avaliação de Conhecimento Ecológico (Quiz de 10 Perguntas)", style_h2))
        status_quiz_texto = f"{st.session_state.quiz_acertos} acertos de 10 perguntas ({(st.session_state.quiz_acertos/10)*100:.0f}%)" if st.session_state.quiz_respondido else "Quiz não finalizado nesta sessão"
        dados_quiz = [
            [Paragraph("<b>Avaliação Gamificada</b>", style_cell_bold), Paragraph("<b>Resultado da Sessão</b>", style_cell_bold)],
            [Paragraph("Pontuação no Desafio Mito ou Verdade", style_cell), Paragraph(status_quiz_texto, style_cell)],
            [Paragraph("Classificação de Perfil", style_cell), Paragraph(f"{'Mestre Supremo' if st.session_state.quiz_acertos==10 else 'Guardião Ecológico' if st.session_state.quiz_acertos>=7 else 'Cidadão Consciente' if st.session_state.quiz_acertos>=5 else 'Iniciante Verde'}", style_cell)]
        ]
        t4 = Table(dados_quiz, colWidths=[270, 260])
        t4.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065F46')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FAFB'), colors.HexColor('#F0FDF4')]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t4)
        elements.append(Spacer(1, 10))

        # 5. Auditoria de Vazamentos
        elements.append(Paragraph("5. Registro de Auditoria de Perdas e Vazamentos Hídricos", style_h2))
        if st.session_state.vazamentos:
            dados_vaz = [[
                Paragraph("<b>Local da Anomalia</b>", style_cell_bold), 
                Paragraph("<b>Severidade</b>", style_cell_bold), 
                Paragraph("<b>Desperdício Estimado</b>", style_cell_bold),
                Paragraph("<b>Impacto Orçamentário</b>", style_cell_bold)
            ]]
            for item in st.session_state.vazamentos:
                dados_vaz.append([
                    Paragraph(item["Local"], style_cell),
                    Paragraph(item["Severidade"], style_cell),
                    Paragraph(f"{item['Perda Estimada (L/mês)']:,.0f} L/mês", style_cell),
                    Paragraph(item["Impacto Financeiro (R$/mês)"], style_cell)
                ])
            t5 = Table(dados_vaz, colWidths=[170, 110, 130, 120])
        else:
            dados_vaz = [
                [Paragraph("<b>Status da Instalação Hídrica</b>", style_cell_bold), Paragraph("<b>Resultado</b>", style_cell_bold)],
                [Paragraph("Inspeção de Torneiras e Tubulações", style_cell), Paragraph("Nenhum vazamento registrado. Sistema operando sem perdas detectadas.", style_cell)]
            ]
            t5 = Table(dados_vaz, colWidths=[270, 260])

        t5.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F2937')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FAFB'), colors.HexColor('#FEF2F2') if st.session_state.vazamentos else colors.HexColor('#F0FDF4')]),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t5)
        elements.append(Spacer(1, 14))

        elements.append(Paragraph("<i>Relatório emitido automaticamente pelo EcoTwin - Inteligência Artificial & Sustentabilidade Urbana. FECART 2026.</i>", style_sub))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_consolidado = gerar_pdf_consolidado()

    st.download_button(
        label="📥 Fazer Download do Laudo Técnico Consolidado (PDF)",
        data=pdf_consolidado,
        file_name="Laudo_Tecnico_Consolidado_EcoTwin.pdf",
        mime="application/pdf",
        use_container_width=True
    )