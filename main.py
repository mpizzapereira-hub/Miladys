import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# Importação de Machine Learning (Requisito Técnico de IA)
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# Importações para geração do PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO E ESTILIZAÇÃO COM ALTO CONTRASTE (SEM TEXTOS APAGADOS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTwin | Gêmeo Digital & IA Sustentável",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Fundo Principal da Aplicação */
    .stApp {
        background-color: #0f231c;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        color: #f0fdf4 !important;
    }
    
    /* Garante visibilidade global de textos, parágrafos e legendas */
    p, span, label, div, li {
        color: #e2f1e7 !important;
    }
    
    /* Títulos e Subtítulos em Destaque */
    h1, h2, h3, h4 {
        color: #34d399 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar (Barra Lateral) */
    [data-testid="stSidebar"] {
        background-color: #081711;
        border-right: 1px solid #1c3d30;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #c2e5d1 !important;
    }

    /* Campos de Entrada na Sidebar */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        color: #0f231c !important;
        background-color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px;
    }
    
    /* Botões Interativos */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff !important;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
    }
    
    /* Cards de Métricas */
    [data-testid="stMetric"] {
        background: #143226;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #23523f;
    }
    [data-testid="stMetricValue"] {
        color: #34d399 !important;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        color: #a7f3d0 !important;
    }
    
    /* Abas de Navegação (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #23523f;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #143226;
        border-radius: 8px 8px 0px 0px;
        color: #a7f3d0 !important;
        font-weight: 600;
        padding: 12px 20px;
        border: 1px solid #23523f;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
    }

    /* Cards Informativos */
    .eco-card {
        background: #143226;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #10b981;
        border: 1px solid #23523f;
        margin-bottom: 15px;
    }

    /* Widget Flutuante da IA Aero */
    .aero-widget {
        position: fixed;
        bottom: 20px;
        right: 25px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .aero-bubble {
        background: #ffffff;
        color: #0f231c !important;
        padding: 8px 14px;
        border-radius: 14px 14px 2px 14px;
        font-weight: bold;
        font-size: 13px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid #10b981;
    }
    .aero-avatar {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: 2px solid #a7f3d0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
    }
    </style>

    <div class="aero-widget">
        <div class="aero-bubble">👋 Olá, Terra! Sou o Aero</div>
        <div class="aero-avatar">🤖</div>
    </div>
""", unsafe_allow_html=True)

# Session State
if "vazamentos" not in st.session_state:
    st.session_state.vazamentos = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🤖 **Olá, Terra! Eu sou o Aero!** Seus assistente ecológico com IA. Como posso ajudar a reduzir sua pegada de carbono hoje?"}
    ]

# -----------------------------------------------------------------------------
# BARRA LATERAL (PARÂMETROS DE ENTRADA)
# -----------------------------------------------------------------------------
st.sidebar.title("🌱 EcoTwin IA")
st.sidebar.caption("Plataforma de Monitoramento Sustentável")

st.sidebar.markdown("---")
st.sidebar.header("🏠 Parâmetros do Imóvel")

moradores = st.sidebar.number_input("Número de Pessoas/Moradores", min_value=1, max_value=100, value=4, step=1)
tempo_banho = st.sidebar.number_input("Tempo de Banho (min/pessoa)", min_value=1, max_value=60, value=10, step=1)
energia_kwh = st.sidebar.number_input("Consumo de Energia (kWh/mês)", min_value=10, max_value=10000, value=220, step=10)

st.sidebar.markdown("---")
st.sidebar.header("💻 Equipamentos de TI")
num_pcs = st.sidebar.number_input("Número de Computadores", min_value=0, max_value=200, value=5, step=1)
horas_pcs = st.sidebar.slider("Horas de Uso Diário dos PCs", min_value=1, max_value=24, value=8, step=1)

meta_reducao_pct = st.sidebar.slider("Meta de Redução Ecológica (%)", min_value=5, max_value=50, value=15, step=5)

# -----------------------------------------------------------------------------
# CÁLCULOS TÉCNICOS
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
arvores_salvas = int(round(co2_evitado_ano_kg / 15.0))
arvores_necessarias = int(round((co2_total_ano_kg - co2_evitado_ano_kg) / 15.0))

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
        fontSize=18, textColor=colors.HexColor('#064e3b'), spaceAfter=12
    )
    
    elements = [
        Paragraph("🌱 Relatório de Impacto Ambiental - EcoTwin", title_style),
        Spacer(1, 10)
    ]
    
    dados = [
        ["Indicador Ambiental", "Valor Medido"],
        ["Ocupantes da Instalação", str(moradores)],
        ["Consumo Total de Energia", f"{kwh_total_mes:,.0f} kWh/mês"],
        ["Pegada de Carbono Anual", f"{co2_total_ano_kg:.1f} kg CO₂/ano"],
        ["Meta de Redução Definida", f"{meta_reducao_pct}%"],
        ["Carbono Evitado com Meta", f"{co2_evitado_ano_kg:.1f} kg CO₂/ano"],
        ["Compensação em Árvores Salvas", f"{arvores_salvas} Árvores/ano"],
        ["Economia Financeira Estimada", f"R$ {economia_fin_mes*12:,.2f}/ano"]
    ]
    
    tabela = Table(dados, colWidths=[220, 200])
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
# PAINEL DE ABAS
# -----------------------------------------------------------------------------
st.title("EcoTwin | Gêmeo Digital e Inteligência Artificial Sustentável 🌱")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Diagnóstico",
    "🌱 Créditos de Carbono",
    "🧠 Modelo de IA (ML)",
    "🤖 Chat IA Aero",
    "📝 Quiz de Hábitos",
    "🔍 Vazamentos",
    "📄 Relatórios PDF"
])

# -----------------------------------------------------------------------------
# TAB 1: DIAGNÓSTICO
# -----------------------------------------------------------------------------
with tab1:
    st.header("📊 Diagnóstico Ecológico da Instalação")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Consumo Energético", f"{kwh_total_mes:,.0f} kWh/mês")
    c2.metric("Pegada de Carbono", f"{co2_total_ano_kg:.0f} kg CO₂/ano")
    c3.metric("Árvores Salvas", f"{arvores_salvas} Árvores")
    c4.metric("Economia Est.", f"R$ {economia_fin_mes:.2f}/mês")

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        df_pie = pd.DataFrame({
            "Categoria": ["Eletricidade Prédio", "Computadores/TI", "Uso Hídrico"],
            "Consumo": [energia_kwh, kwh_ti_mes, consumo_agua_total * 0.01]
        })
        fig_pie = px.pie(df_pie, values="Consumo", names="Categoria", title="Distribuição do Impacto Energético/Ambiental", color_discrete_sequence=['#10b981', '#3b82f6', '#06b6d4'])
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2f1e7'))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        df_bar = pd.DataFrame({
            "Cenário": ["Atual", "Com Meta Ecológica"],
            "kg CO₂/ano": [co2_total_ano_kg, co2_total_ano_kg - co2_evitado_ano_kg]
        })
        fig_bar = px.bar(df_bar, x="Cenário", y="kg CO₂/ano", color="Cenário", title="Projeção de Redução de Emissões", color_discrete_sequence=['#ef4444', '#10b981'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2f1e7'))
        st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: CRÉDITOS DE CARBONO
# -----------------------------------------------------------------------------
with tab2:
    st.header("🌱 Créditos de Carbono & Sumidouro Florestal")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("""
        <div class="eco-card">
            <h4>🔴 O que é Débito de Carbono?</h4>
            <p>Ocorre quando as atividades da instalação geram mais emissões de CO₂ do que a capacidade do ecossistema de absorvê-las.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown("""
        <div class="eco-card">
            <h4>🟢 O que é Crédito de Carbono?</h4>
            <p>Representa a não emissão ou remoção de CO₂ da atmosfera obtida através de metas de eficiência e otimização.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌳 Balanço de Neutralização Florestal")
    
    st.write(f"- Para anular 100% da pegada atual ({co2_total_ano_kg:.0f} kg CO₂/ano), é necessário o plantio ou financiamento de **{arvores_necessarias} árvores nativas**.")
    st.write(f"- A meta de **{meta_reducao_pct}% de otimização** equivale ao trabalho ambiental de **{arvores_salvas} árvores** em crescimento por ano!")
    
    if meta_reducao_pct >= 20:
        st.balloons()
        st.success(f"🎉 **Excelente Desempenho!** Sua meta gera o abatimento de {co2_evitado_ano_kg:.1f} kg de CO₂/ano.")
    else:
        st.warning("⚠️ Aumente sua meta na barra lateral para elevar seu nível de créditos de carbono.")

# -----------------------------------------------------------------------------
# TAB 3: MACHINE LEARNING
# -----------------------------------------------------------------------------
with tab3:
    st.header("🧠 Módulo de Inteligência Computacional (Machine Learning)")
    st.write("Uso do pacote `scikit-learn` para análise preditiva e classificação não-supervisionada de perfil:")

    st.markdown("---")
    st.subheader("1. Previsão de Consumo Energético (Regressão Linear)")
    
    # Dados de treino simulados
    meses_treino = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    consumo_treino = np.array([kwh_total_mes * 0.9, kwh_total_mes * 0.95, kwh_total_mes * 1.05, 
                               kwh_total_mes * 1.02, kwh_total_mes * 1.1, kwh_total_mes])
    
    # Modelo de Regressão Linear
    model = LinearRegression()
    model.fit(meses_treino, consumo_treino)
    
    # Previsão
    meses_futuros = np.array([7, 8, 9]).reshape(-1, 1)
    previsoes = model.predict(meses_futuros)
    
    df_ml = pd.DataFrame({
        "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"],
        "Consumo (kWh)": list(consumo_treino) + list(previsoes),
        "Origem": ["Histórico Real"]*6 + ["Projeção Machine Learning"]*3
    })
    
    fig_ml = px.line(df_ml, x="Mês", y="Consumo (kWh)", color="Origem", markers=True, title="Modelo Preditivo de Consumo Futuro")
    fig_ml.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2f1e7'))
    st.plotly_chart(fig_ml, use_container_width=True)

    st.markdown("---")
    st.subheader("2. Classificação de Perfil Ecológico (K-Means Clustering)")
    
    # Algoritmo K-Means
    np.random.seed(42)
    dados_clusters = np.random.randint(100, 2000, size=(20, 2))
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(dados_clusters)
    
    df_cluster = pd.DataFrame(dados_clusters, columns=["Demanda Energia (kWh)", "Demanda Água (L)"])
    df_cluster["Grupo Ecológico"] = [f"Cluster {c+1}" for c in kmeans.labels_]
    
    fig_cluster = px.scatter(df_cluster, x="Demanda Energia (kWh)", y="Demanda Água (L)", color="Grupo Ecológico", title="Mapeamento de Perfis por Agrupamento K-Means")
    fig_cluster.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2f1e7'))
    st.plotly_chart(fig_cluster, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: IA AERO
# -----------------------------------------------------------------------------
with tab4:
    st.header("🤖 Consultoria com o Assistente Aero")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Digite sua dúvida para o Aero...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if "banho" in prompt.lower():
                resp = f"🚿 **Dica do Aero:** Diminuir o tempo de banho das {moradores} pessoas da casa em 2 minutos poupa até **{moradores * 2 * 9 * 30} Litros de água por mês**!"
            elif "luz" in prompt.lower() or "energia" in prompt.lower():
                resp = f"⚡ **Dica do Aero:** Seus {num_pcs} computadores respondem por **{kwh_ti_mes:.0f} kWh/mês**. Ativar a suspensão automática de tela economiza até 15%!"
            else:
                resp = f"🌱 **Dica do Aero:** Para alcançar a meta de {meta_reducao_pct}%, recomendo priorizar a troca de lâmpadas antigas por LED e controlar os aparelhos mantidos em modo de espera."
            
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# -----------------------------------------------------------------------------
# TAB 5: QUIZ DE HÁBITOS
# -----------------------------------------------------------------------------
with tab5:
    st.header("📝 Diagnosticador de Hábitos Sustentáveis")
    
    q1 = st.radio("1. O computador e os monitores são desligados ao fim da rotina?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)"])
    q2 = st.radio("2. A iluminação de cômodos ou salas vazias é mantida apagada?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)"])
    q3 = st.radio("3. A torneira é fechada durante a escovação ou higienização?", ["Sempre (10 Pts)", "Às vezes (5 Pts)", "Nunca (0 Pts)"])
    
    if st.button("Consolidar Pontuação"):
        pontos = sum([10 if "Sempre" in r else (5 if "Às vezes" in r else 0) for r in [q1, q2, q3]])
        st.subheader(f"Pontuação de Conformidade: **{pontos} / 30 Pontos**")
        if pontos >= 25:
            st.success("🌟 **Excelência Operacional!** Seus hábitos estão alinhados com boas práticas ambientais.")
        else:
            st.warning("⚠️ **Atenção:** Há margem para melhorias no controle do consumo diário.")

# -----------------------------------------------------------------------------
# TAB 6: VAZAMENTOS
# -----------------------------------------------------------------------------
with tab6:
    st.header("🔍 Auditoria de Perdas e Vazamentos Hídricos")
    
    local = st.selectbox("Ponto de Anomalia", ["Torneira", "Caixa Acoplada / Vaso Sanitário", "Chuveiro"])
    gotas = st.slider("Intensidade do Gotejamento", 1, 10, 2)
    
    perda_litros = gotas * 30 * 30
    st.write(f"Perda Estimada: **{perda_litros} Litros/mês** (Impacto orçamentário: R$ {perda_litros * 0.012:.2f}/mês)")
    
    if st.button("Registrar Ocorrência"):
        st.session_state.vazamentos.append({"Local": local, "Perda L/mês": perda_litros})
        st.success("Anomalia registrada com sucesso!")

# -----------------------------------------------------------------------------
# TAB 7: RELATÓRIOS PDF
# -----------------------------------------------------------------------------
with tab7:
    st.header("📄 Emissão do Laudo Técnico (PDF)")
    st.write("Clique no botão abaixo para gerar o relatório oficial formatado contendo o resumo dos dados:")
    
    pdf_bytes = gerar_pdf()
    st.download_button(
        label="📥 Emitir Relatório Técnico em PDF",
        data=pdf_bytes,
        file_name="Relatorio_Tecnico_EcoTwin.pdf",
        mime="application/pdf",
        use_container_width=True
    )