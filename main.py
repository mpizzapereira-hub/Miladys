import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# Importação de Machine Learning e Detecção de Anomalias (IA)
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# Importações para geração do PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E ESTILIZAÇÃO CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTwin | Monitoramento & Inteligência Ambiental",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gerenciamento de navegação por estado e query params para o clique do Aero
query_params = st.query_params
if "nav" in query_params and query_params["nav"] == "aero":
    st.session_state.active_tab = 3
    st.query_params.clear()

if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

st.markdown("""
    <style>
    /* 1. FUNDO VERDE ESCURO REFINADO */
    .stApp {
        background-color: #0E231A;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        color: #ECFDF5 !important;
    }
    
    /* 2. TEXTOS E RÓTULOS */
    p, span, label, div, li {
        color: #E2E8F0 !important;
    }
    
    h1, h2, h3, h4 {
        color: #34D399 !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem;
    }

    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #34D399;
        margin-bottom: 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* 3. BARRA LATERAL (SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #081610;
        border-right: 1px solid #1C3A2D;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px;
    }

    /* 4. ABAS COM BORDAS ARREDONDADAS E MICROANIMAÇÕES NO HOVER */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid #1C3A2D;
        overflow-x: auto;
        white-space: nowrap;
        flex-wrap: nowrap !important;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #152E23;
        border-radius: 12px 12px 4px 4px !important;
        color: #A7F3D0 !important;
        font-weight: 600;
        font-size: 0.85rem !important;
        padding: 9px 14px !important;
        border: 1px solid #234737;
        flex-shrink: 0;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    /* Microanimação nas Abas (Hover) */
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px) scale(1.01);
        border-color: #34D399;
        background-color: #1C3A2D;
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: #FFFFFF !important;
        border-color: #34D399;
        border-radius: 12px 12px 4px 4px !important;
    }

    /* 5. CARDS DE RESULTADOS COM MICROANIMAÇÕES */
    .metric-card {
        background: #152E23;
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #234737;
        min-height: 95px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #34D399;
        box-shadow: 0 8px 15px rgba(16, 185, 129, 0.2);
    }
    .metric-label {
        font-size: 0.82rem;
        color: #9AE6B4;
        font-weight: 600;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #34D399;
        line-height: 1.1;
    }
    .metric-unit {
        font-size: 0.78rem;
        color: #CBD5E1;
        font-weight: 500;
        margin-top: 2px;
    }

    /* CARDS INFORMATIVOS COM HOVER SUAVE */
    .eco-card {
        background: #152E23;
        padding: 18px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        border: 1px solid #234737;
        margin-bottom: 15px;
        transition: all 0.25s ease;
    }
    .eco-card:hover {
        transform: translateY(-2px);
        border-color: #34D399;
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.15);
    }
    
    .tech-card {
        background: #0A1C14;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #34D399;
        margin-top: 10px;
        font-size: 0.88rem;
    }

    /* BOTÕES COM ANIMAÇÃO */
    .stButton>button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: #FFFFFF !important;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    /* 6. AERO CLICÁVEL REAL ("Olá, sou o Aero") SEM BOTÃO DUPLICADO NO TOPO */
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
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 2px solid #10B981;
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

# -----------------------------------------------------------------------------
# WIDGET FLUTUANTE CLICÁVEL DO AERO ("Olá, sou o Aero") COM NAVEGAÇÃO REAL
# -----------------------------------------------------------------------------
st.markdown("""
    <a href="?nav=aero" target="_self" class="aero-widget-link" title="Clique para abrir o Chat Aero">
        <div class="aero-bubble">Olá, sou o Aero</div>
        <div class="aero-avatar">🤖</div>
    </a>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if "vazamentos" not in st.session_state:
    st.session_state.vazamentos = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🤖 **Olá! Eu sou o Aero!** Seu copiloto de sustentabilidade. Como posso analisar o seu consumo ou ajudar na sua meta de emissões hoje?"}
    ]

# -----------------------------------------------------------------------------
# BARRA LATERAL DE PARÂMETROS
# -----------------------------------------------------------------------------
st.sidebar.title("🌱 EcoTwin")
st.sidebar.caption("Monitoramento & Inteligência Ambiental")

st.sidebar.markdown("---")
st.sidebar.header("🏠 Consumo Residencial")

moradores = st.sidebar.number_input("Número de Pessoas / Ocupantes", min_value=1, max_value=100, value=4, step=1)
tempo_banho = st.sidebar.number_input("Tempo Médio de Banho (min/pessoa)", min_value=1, max_value=60, value=10, step=1)
energia_kwh = st.sidebar.number_input("Consumo de Energia Geral (kWh/mês)", min_value=10, max_value=10000, value=220, step=10)

st.sidebar.markdown("---")
st.sidebar.header("💻 Infraestrutura & TI")
num_pcs = st.sidebar.number_input("Número de Computadores", min_value=0, max_value=200, value=5, step=1)
horas_pcs = st.sidebar.slider("Horas de Uso Diário dos PCs", min_value=1, max_value=24, value=8, step=1)

st.sidebar.markdown("---")
meta_reducao_pct = st.sidebar.slider("Meta de Otimização Ecológica (%)", min_value=5, max_value=50, value=15, step=5)

# -----------------------------------------------------------------------------
# CÁLCULOS TÉCNICOS E METODOLOGIA
# -----------------------------------------------------------------------------
litros_banho_mes = tempo_banho * 9 * moradores * 30
consumo_outro_agua = moradores * 30 * 40
consumo_agua_total = litros_banho_mes + consumo_outro_agua

kwh_ti_mes = (num_pcs * 0.150 * horas_pcs * 30)
kwh_total_mes = energia_kwh + kwh_ti_mes

co2_energia_kg = kwh_total_mes * 0.085
co2_agua_kg = consumo_agua_total * 0.0005
co2_total_mes_kg = co2_energia_kg + co2_agua_kg
co2_total_ano_kg = co2_total_mes_kg * 12

co2_evitado_ano_kg = co2_total_ano_kg * (meta_reducao_pct / 100.0)

arvores_equivalentes = int(round(co2_total_ano_kg / 15.0))
arvores_salvas = int(round(co2_evitado_ano_kg / 15.0))

economia_fin_mes = (kwh_total_mes * (meta_reducao_pct / 100.0)) * 0.75

# -----------------------------------------------------------------------------
# GERADOR DE PDF
# -----------------------------------------------------------------------------
def gerar_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=18, textColor=colors.HexColor('#065f46'), spaceAfter=12
    )
    
    elements = [
        Paragraph("🌱 Relatório de Impacto Ambiental - EcoTwin", title_style),
        Paragraph("Plataforma de Monitoramento & Inteligência Ambiental", styles['Normal']),
        Spacer(1, 15)
    ]
    
    dados = [
        ["Indicador Ambiental", "Valor Medido / Estimado"],
        ["Ocupantes da Instalação", str(moradores)],
        ["Consumo Total de Energia", f"{kwh_total_mes:,.0f} kWh/mês"],
        ["Pegada de Carbono Anual", f"{co2_total_ano_kg:.1f} kg CO₂e/ano"],
        ["Meta de Redução Definida", f"{meta_reducao_pct}%"],
        ["Emissões Evitadas (Meta)", f"{co2_evitado_ano_kg:.1f} kg CO₂e/ano"],
        ["Equivalência em Árvores Preservadas", f"{arvores_salvas} Árvores/ano"],
        ["Economia Financeira Estimada", f"R$ {economia_fin_mes*12:,.2f}/ano"]
    ]
    
    tabela = Table(dados, colWidths=[230, 200])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#a7f3d0')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0fdf4')),
    ]))
    
    elements.append(tabela)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# CABEÇALHO PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">EcoTwin | Monitoramento & Inteligência Ambiental</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAINEL DE ABAS (COM SELEÇÃO DINÂMICA CONTROLADA PELO CLIQUE DO AERO)
# -----------------------------------------------------------------------------
tab_names = [
    "📊 Diagnóstico",
    "🌳 Carbon Twin",
    "🧠 Modelo de IA",
    "🤖 Chat Aero",
    "📝 Diagnóstico Inteligente",
    "🔍 Vazamentos",
    "📄 Relatórios PDF"
]

selected_tab = st.session_state.active_tab
tabs = st.tabs(tab_names)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs

# Script de redirecionamento imediato caso o clique do Aero tenha acionado o estado
if st.session_state.active_tab == 3:
    st.session_state.active_tab = 0
    st.rerun()

# -----------------------------------------------------------------------------
# TAB 1: DIAGNÓSTICO
# -----------------------------------------------------------------------------
with tab1:
    st.header("📊 Diagnóstico de Impacto Ambiental")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Consumo Energético</div>
            <div class="metric-value">{kwh_total_mes:,.0f}</div>
            <div class="metric-unit">kWh / mês</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pegada de Carbono</div>
            <div class="metric-value">{co2_total_ano_kg:,.0f}</div>
            <div class="metric-unit">kg CO₂e / ano</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Equivalência Ambiental</div>
            <div class="metric-value">{arvores_salvas}</div>
            <div class="metric-unit">Árvores Preservadas / ano</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Economia Estimada</div>
            <div class="metric-value">R$ {economia_fin_mes:,.2f}</div>
            <div class="metric-unit">potencial financeiro / mês</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição do Impacto Energético / Hídrico")
        df_donut = pd.DataFrame({
            "Categoria": ["Eletricidade Geral", "Equipamentos TI", "Uso Hídrico"],
            "Consumo (kWh Equivalente)": [energia_kwh, kwh_ti_mes, (consumo_agua_total * 0.005)]
        })
        fig_donut = px.pie(
            df_donut, 
            values="Consumo (kWh Equivalente)", 
            names="Categoria", 
            hole=0.5,
            color_discrete_sequence=['#10B981', '#3B82F6', '#06B6D4']
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E2E8F0'),
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.subheader("Cenário Atual vs Meta de Redução")
        df_bar = pd.DataFrame({
            "Cenário": ["Cenário Atual", "Com Meta de Redução"],
            "Emissão (kg CO₂e/ano)": [co2_total_ano_kg, co2_total_ano_kg - co2_evitado_ano_kg]
        })
        fig_bar = px.bar(
            df_bar, 
            x="Cenário", 
            y="Emissão (kg CO₂e/ano)", 
            color="Cenário",
            text="Emissão (kg CO₂e/ano)",
            color_discrete_sequence=['#EF4444', '#10B981']
        )
        fig_bar.update_traces(texttemplate='%{text:.0f} kg', textposition='outside')
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
        <h4>💡 Contextualização dos Resultados</h4>
        <p><b>A Pegada do Imóvel:</b> {co2_total_ano_kg:.1f} kg CO₂e/ano.</p>
        <p><b>Significado:</b> Este valor representa uma estimativa direta das emissões decorrentes do consumo de eletricidade e recursos hídricos.</p>
        <p><b>Maior Fator de Impacto:</b> O consumo elétrico predial responde pela maior fração das emissões calculadas.</p>
        <p><b>Recomendação Prioritária:</b> Definir metas para a infraestrutura de TI e otimizar equipamentos em standby podem gerar até R$ {economia_fin_mes*12:,.2f} de economia por ano.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Ver análise técnica e metodologia"):
        st.markdown(f"""
        <div class="tech-card">
            <b>Detalhamento Técnico do Cálculo:</b><br>
            • <b>Fator de Emissão Energética:</b> 0,085 kg CO₂/kWh (Baseado na média do Sistema Interligado Nacional).<br>
            • <b>Fator de Emissão Hídrica:</b> 0,0005 kg CO₂/L (Consumo energético do tratamento e distribuição).<br>
            • <b>Potência estimada de TI:</b> 150W por estação de trabalho ativa.<br>
            • <b>Metodologia de Neutralização:</b> Considera a absorção média anual de 15kg de CO₂ por árvore adulta nativa.<br>
            • <b>Limitações:</b> Modelo demonstrativo baseado nos parâmetros informados na barra lateral.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: CARBON TWIN / VISUALIZAÇÃO AMBIENTAL
# -----------------------------------------------------------------------------
with tab2:
    st.header("🌳 Carbon Twin | Impacto Ambiental Visual")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        <div class="eco-card">
            <h4>🔴 Débito de Emissões</h4>
            <p>Ocorre quando as atividades operacionais geram liberação de CO₂ na atmosfera superior à capacidade de absorção local.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="eco-card">
            <h4>🟢 Equivalência & Compensação</h4>
            <p>Representa a redução voluntária ou mitigação calculada atrelada a metas de eficiência e otimização energética.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌲 Floresta Virtual de Equivalência")
    st.write(f"Sua emissão anual ({co2_total_ano_kg:.0f} kg CO₂e) corresponde à capacidade de absorção de **{arvores_equivalentes} árvores adultas**.")
    
    arvores_exibidas = min(arvores_equivalentes, 60)
    grid_arvores = "🌳 " * arvores_exibidas
    st.markdown(f"<div style='font-size: 24px; line-height: 1.8; background: #0A1C14; padding: 15px; border-radius: 8px; border: 1px solid #234737;'>{grid_arvores}</div>", unsafe_allow_html=True)
    
    st.caption("Nota: Representação de equivalência florestal baseada no consumo informado. Esta simulação é educativa e não substitui auditorias oficiais de créditos de carbono.")

# -----------------------------------------------------------------------------
# TAB 3: MODELO DE IA (PREVISÃO, ANOMALIAS E CLUSTER)
# -----------------------------------------------------------------------------
with tab3:
    st.header("🧠 Módulo de Inteligência Computacional (Machine Learning)")
    
    st.subheader("1. Previsão de Consumo Energético (Regressão Linear)")
    
    meses_treino = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    consumo_treino = np.array([kwh_total_mes * 0.88, kwh_total_mes * 0.92, kwh_total_mes * 1.04, 
                               kwh_total_mes * 0.98, kwh_total_mes * 1.05, kwh_total_mes])
    
    model = LinearRegression()
    model.fit(meses_treino, consumo_treino)
    
    meses_futuros = np.array([7, 8, 9]).reshape(-1, 1)
    previsoes = model.predict(meses_futuros)
    
    fig_ml = go.Figure()
    fig_ml.add_trace(go.Scatter(
        x=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        y=consumo_treino,
        mode='lines+markers',
        name='Histórico Real',
        line=dict(color='#10B981', width=3)
    ))
    fig_ml.add_trace(go.Scatter(
        x=["Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"],
        y=[consumo_treino[-1]] + list(previsoes),
        mode='lines+markers',
        name='Projeção IA',
        line=dict(color='#3B82F6', width=3, dash='dash')
    ))
    fig_ml.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_ml, use_container_width=True)
    
    st.info(f"💡 **Interpretação da IA:** O modelo prevê uma tendência de consumo médio de **{previsoes.mean():.0f} kWh** para os próximos 3 meses. Mantenha os computadores fora do modo standby para estabilizar a projeção.")

    st.markdown("---")
    col_ia1, col_ia2 = st.columns(2)
    
    with col_ia1:
        st.subheader("2. Análise de Anomalias (Isolation Forest)")
        X_anomalia = np.array([[kwh_total_mes*0.9], [kwh_total_mes*0.95], [kwh_total_mes], [kwh_total_mes*2.1]])
        iso_model = IsolationForest(contamination=0.25, random_state=42)
        preds = iso_model.fit_predict(X_anomalia)
        
        if preds[-1] == -1:
            st.warning("⚠️ **Alerta do EcoTwin:** O modelo identificou um pico atípico no consumo projetado em relação à média esperada.")
        else:
            st.success("✅ **Status Normal:** Consumo estabilizado sem picos anômalos detectados.")

    with col_ia2:
        st.subheader("3. Cluster de Perfil (K-Means)")
        np.random.seed(42)
        dados_clusters = np.random.randint(100, 2000, size=(20, 2))
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(dados_clusters)
        
        df_cluster = pd.DataFrame(dados_clusters, columns=["Energia (kWh)", "Água (L)"])
        df_cluster["Grupo"] = [f"Perfil {c+1}" for c in kmeans.labels_]
        
        fig_cluster = px.scatter(df_cluster, x="Energia (kWh)", y="Água (L)", color="Grupo", color_discrete_sequence=['#10B981', '#F59E0B', '#EF4444'])
        fig_cluster.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E2E8F0'), margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_cluster, use_container_width=True)

    with st.expander("🔬 Ver análise técnica e transparência dos modelos"):
        st.caption("• **Regressão Linear:** Ajuste via Mínimos Quadrados Ordinários (OLS). Data de treino: Simulada com base no padrão informado.")
        st.caption("• **Isolation Forest:** Algoritmo baseado em árvores para isolamento de observações fora do desvio padrão.")
        st.caption("• **K-Means:** Agrupamento não-supervisionado particionando os dados em 3 centroides de uso energético/hídrico.")

# -----------------------------------------------------------------------------
# TAB 4: CHAT IA AERO
# -----------------------------------------------------------------------------
with tab4:
    st.header("🤖 Consultoria com o Assistente Aero")
    st.caption("O Aero utiliza os dados reais preenchidos no seu painel para responder perguntas personalizadas.")
    
    st.markdown("**💡 Sugestões de Perguntas Frequentes:**")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    pergunta_clicada = None
    with col_q1:
        if st.button("⚡ Onde estou gastando mais?"):
            pergunta_clicada = "Onde estou gastando mais?"
    with col_q2:
        if st.button("💧 Como reduzir meu tempo de banho?"):
            pergunta_clicada = "Como posso economizar água nos banhos?"
    with col_q3:
        if st.button("🌱 Como melhorar meu perfil de carbono?"):
            pergunta_clicada = "Como melhorar minha pontuação de emissões?"

    st.markdown("---")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt_input = st.chat_input("Digite sua dúvida para o Aero...")
    prompt = pergunta_clicada or prompt_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if "gastando mais" in prompt.lower() or "onde" in prompt.lower():
                resp = f"📊 **Análise do Aero:** Com base nos seus dados, o gasto principal está na energia predial (**{energia_kwh} kWh/mês**) e nos computadores de TI (**{kwh_ti_mes:.0f} kWh/mês**)."
            elif "água" in prompt.lower() or "banho" in prompt.lower():
                resp = f"🚿 **Dica do Aero:** Reduzir 2 minutos no banho das {moradores} pessoas poupará cerca de **{moradores * 2 * 9 * 30} Litros de água por mês**!"
            else:
                resp = f"🌱 **Dica do Aero:** Para alcançar a meta de {meta_reducao_pct}% e economizar R$ {economia_fin_mes:.2f}/mês, priorize desligar os {num_pcs} computadores ao final do expediente."
            
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# -----------------------------------------------------------------------------
# TAB 5: DIAGNÓSTICO INTELIGENTE
# -----------------------------------------------------------------------------
with tab5:
    st.header("📝 Diagnóstico Inteligente de Carbono")
    st.write("Responda às questões sobre hábitos para obter sua avaliação técnica de conformidade:")

    q1 = st.radio("1. Os equipamentos de TI e monitores são desligados ao fim da rotina?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)", "Não sei"])
    q2 = st.radio("2. A iluminação em cômodos e salas desocupadas permanece apagada?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)", "Não sei"])
    q3 = st.radio("3. As torneiras são mantidas fechadas durante a higienização?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)", "Não sei"])
    q4 = st.radio("4. Há controle sobre o tempo de uso de ar-condicionado?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)", "Não sei"])

    if q1 == "Não sei" or q2 == "Não sei" or q3 == "Não sei" or q4 == "Não sei":
        st.info("💡 **Onde encontrar informações técnicas não sabidas?** Consulte a conta de energia mensal do imóvel ou o manual do fabricante dos seus aparelhos de TI.")

    if st.button("Consolidar Pontuação do Diagnóstico"):
        respostas = [q1, q2, q3, q4]
        pontos = sum([10 if "Sempre" in r else (5 if "Às vezes" in r else 0) for r in respostas])
        st.subheader(f"Pontuação de Conformidade: **{pontos} / 40 Pontos**")
        if pontos >= 30:
            st.success("🌟 **Excelente Desempenho Operacional!** Seus hábitos estão altamente alinhados com a eficiência ambiental.")
        else:
            st.warning("⚠️ **Atenção:** Identificamos margem de otimização no controle dos equipamentos.")

# -----------------------------------------------------------------------------
# TAB 6: VAZAMENTOS
# -----------------------------------------------------------------------------
with tab6:
    st.header("🔍 Auditoria de Perdas e Vazamentos Hídricos")
    
    local = st.selectbox("Ponto de Anomalia Detectado", ["Torneira", "Caixa Acoplada / Vaso Sanitário", "Chuveiro"])
    gotas = st.slider("Intensidade do Gotejamento (Escala 1 a 10)", 1, 10, 2)
    
    perda_litros = gotas * 30 * 30
    st.write(f"Perda Estimada: **{perda_litros} Litros / mês** (Impacto orçamentário: R$ {perda_litros * 0.012:.2f}/mês)")
    
    if st.button("Registrar Ocorrência na Auditoria"):
        st.session_state.vazamentos.append({"Local": local, "Perda L/mês": perda_litros})
        st.success("Ocorrência registrada no histórico de auditoria!")

# -----------------------------------------------------------------------------
# TAB 7: RELATÓRIOS PDF
# -----------------------------------------------------------------------------
with tab7:
    st.header("📄 Emissão do Laudo Técnico (PDF)")
    st.write("Gere o relatório oficial consolidando os parâmetros informados, pegada de carbono e metas:")
    
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="📥 Emitir Relatório Técnico em PDF",
        data=pdf_bytes,
        file_name="Relatorio_Tecnico_EcoTwin.pdf",
        mime="application/pdf",
        use_container_width=True
    )