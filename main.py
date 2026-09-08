import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Importações para geração do PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO E ESTILIZAÇÃO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTwin - Plataforma Dinâmica Sustentável",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #f4f9f5;
    }
    [data-testid="stSidebar"] {
        background-color: #1b4332;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #2d6a4f;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #40916c;
        color: white !important;
    }
    h1, h2, h3 {
        color: #1b4332 !important;
    }
    [data-testid="stMetricValue"] {
        color: #2d6a4f !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;
        border-radius: 6px 6px 0px 0px;
        color: #1b4332;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2d6a4f !important;
        color: white !important;
    }
    .info-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2d6a4f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "vazamentos_detectados" not in st.session_state:
    st.session_state.vazamentos_detectados = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Eu sou o Aero, sua IA de inteligência sustentável! 🌿 Como posso te ajudar hoje?"}
    ]

# -----------------------------------------------------------------------------
# BARRA LATERAL
# -----------------------------------------------------------------------------
st.sidebar.title("🌿 EcoTwin")
st.sidebar.caption("EcoMonitoramento Urbano Inteligente")

st.sidebar.markdown("---")
st.sidebar.header("🏠 Dados da Simulação")

moradores = st.sidebar.number_input("Número de moradores", min_value=1, max_value=20, value=4, step=1)
tempo_banho = st.sidebar.number_input("Tempo de banho (min/pessoa)", min_value=1, max_value=60, value=10, step=1)
frequencia_maquina = st.sidebar.number_input("Uso da máquina (vezes/semana)", min_value=0, max_value=20, value=3, step=1)
energia_kwh = st.sidebar.number_input("Consumo mensal de energia (kWh)", min_value=10, max_value=5000, value=220, step=10)
meta_reducao_pct = st.sidebar.slider("Meta de redução (%)", min_value=5, max_value=50, value=15, step=5)

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido para **EcoTwin**")

# -----------------------------------------------------------------------------
# CÁLCULOS PRINCIPAIS
# -----------------------------------------------------------------------------
litros_banho_mes = tempo_banho * 9 * moradores * 30
litros_maquina_mes = frequencia_maquina * 4 * 100
consumo_outro_mes = moradores * 30 * 40
consumo_atual_litros = litros_banho_mes + litros_maquina_mes + consumo_outro_mes

reducao_fator = meta_reducao_pct / 100.0
economia_agua_litros = consumo_atual_litros * reducao_fator

co2_energia_kg = energia_kwh * 0.085
co2_agua_kg = consumo_atual_litros * 0.0005
co2_total_atual_kg = co2_energia_kg + co2_agua_kg

co2_evitado_mes_kg = co2_total_atual_kg * reducao_fator
co2_evitado_ano_kg = co2_evitado_mes_kg * 12
creditos_carbono_ano = co2_evitado_ano_kg / 1000.0

economia_financeira_mes = economia_agua_litros * 0.008

# Gerador de PDF
def gerar_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1b4332'),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#2d6a4f'),
        spaceAfter=8
    )

    elements = []
    elements.append(Paragraph("🌿 EcoTwin - Relatório Técnico de Sustentabilidade", title_style))
    elements.append(Spacer(1, 10))
    
    dados = [
        ["Métrica / Indicador", "Valor Registrado"],
        ["Número de Moradores", str(moradores)],
        ["Meta de Redução Definida", f"{meta_reducao_pct}%"],
        ["Economia Mensal de Água", f"{economia_agua_litros:,.0f} Litros"],
        ["Economia Financeira Estimada", f"R$ {economia_financeira_mes:.2f}/mês"],
        ["Poluição de Carbono Evitada", f"{co2_evitado_ano_kg:.2f} kg/ano"],
        ["Créditos de Carbono Potenciais", f"{creditos_carbono_ano:.4f} tCO₂/ano"]
    ]
    
    tabela = Table(dados, colWidths=[250, 200])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1b4332')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f4f9f5')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#b7e4c7')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    
    elements.append(tabela)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Este documento consolida os indicadores de impacto ambiental gerados pela plataforma EcoTwin.", body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
st.title("EcoTwin - Monitoramento & Inteligência Ambiental 🌿")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Diagnóstico & Carbono",
    "🤖 Chat IA (Aero)",
    "📝 Quiz de Hábitos",
    "🔍 Registro de Vazamentos",
    "🎮 Gamificação",
    "📄 Relatórios"
])

# -----------------------------------------------------------------------------
# TAB 1: DIAGNÓSTICO & CARBONO
# -----------------------------------------------------------------------------
with tab1:
    st.header("📊 Diagnóstico de Consumo e Impacto")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💧 Água Economizada/mês", f"{economia_agua_litros:,.0f} L", f"-{meta_reducao_pct}%")
    c2.metric("💰 Economia Financeira", f"R$ {economia_financeira_mes:.2f}/mês")
    c3.metric("🌱 Carbono Evitado por ano", f"{co2_evitado_ano_kg:.1f} kg")

    st.markdown("---")
    st.subheader("💡 Entenda Seus Indicadores de Forma Simples")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("""
        <div class="info-card">
            <h4>💧 Economia de Água</h4>
            <p>Mostra a quantidade de água que você evita desperdiçar. Isso protege os rios e reduz diretamente o valor da sua conta no final do mês.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div class="info-card">
            <h4>🌱 Créditos de Carbono</h4>
            <p>Ao economizar luz e água, você evita jogar fumaça de carbono no ar. Cada 1.000 kg de carbono economizado valem 1 Crédito de Carbono!</p>
        </div>
        """, unsafe_allow_html=True)

    st.success(f" Com a meta de **{meta_reducao_pct}%**, sua casa evita a emissão de **{co2_evitado_ano_kg:.1f} kg de carbono por ano**, gerando **{creditos_carbono_ano:.4f}** Créditos de Carbono potenciais!")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        df_agua = pd.DataFrame({
            "Categoria": ["Banhos", "Máquina de Lavar", "Outros Usos"],
            "Litros": [litros_banho_mes, litros_maquina_mes, consumo_outro_mes]
        })
        fig_agua = px.pie(df_agua, values="Litros", names="Categoria", title="Onde você mais gasta água", color_discrete_sequence=['#2d6a4f', '#52b788', '#74c69d'])
        st.plotly_chart(fig_agua, use_container_width=True)

    with col_g2:
        df_co2 = pd.DataFrame({
            "Cenário": ["Atual", "Com Redução"],
            "kg de Carbono/mês": [co2_total_atual_kg, co2_total_atual_kg - co2_evitado_mes_kg]
        })
        fig_co2 = px.bar(df_co2, x="Cenário", y="kg de Carbono/mês", color="Cenário", title="Sua Produção de Poluição de Carbono", color_discrete_sequence=['#1b4332', '#52b788'])
        st.plotly_chart(fig_co2, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: CHAT IA
# -----------------------------------------------------------------------------
with tab2:
    st.header("🤖 Conversar com o Aero (IA Sustentável)")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Pergunte ao Aero..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            resposta = f"🌿 Analisando sua dúvida sobre '{prompt}': otimizar a meta de redução na barra lateral é o primeiro passo para gerar maior impacto econômico e ambiental no EcoTwin!"
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

# -----------------------------------------------------------------------------
# TAB 3: QUIZ DE HÁBITOS
# -----------------------------------------------------------------------------
with tab3:
    st.header("📝 Quiz de Hábitos Sustentáveis")
    st.write("Responda para avaliar a eficiência ecológica do seu imóvel:")

    q1 = st.radio("1. Torneira fechada ao ensaboar mãos ou escovar dentes?", ["Sempre (+10)", "Às vezes (+5)", "Nunca (+0)"])
    q2 = st.radio("2. Máquina de lavar operando apenas na capacidade máxima?", ["Sempre (+10)", "Às vezes (+5)", "Nunca (+0)"])
    q3 = st.radio("3. Lâmpadas apagadas ao sair dos ambientes?", ["Sempre (+10)", "Às vezes (+5)", "Nunca (+0)"])
    q4 = st.radio("4. Reaproveitamento da água da máquina para limpeza externa?", ["Sempre (+10)", "Às vezes (+5)", "Nunca (+0)"])
    q5 = st.radio("5. Banhos com duração de até 5 minutos?", ["Sempre (+10)", "Às vezes (+5)", "Nunca (+0)"])

    if st.button("Calcular Pontuação e Diagnóstico"):
        respostas = [q1, q2, q3, q4, q5]
        pontos = sum([10 if "Sempre" in r else (5 if "Às vezes" in r else 0) for r in respostas])
        
        st.markdown("---")
        st.subheader(f"Pontuação Final: **{pontos} / 50 Pontos**")
        
        if pontos >= 40:
            st.success("🌟 **Excelência Ecológica!** Seus hábitos são referência. Continue mantendo o monitoramento constante.")
        elif pontos >= 25:
            st.warning("⚠️ **Bom Desempenho, com Oportunidades!** Sugestão: tente focar no reaproveitamento de água e em reduzir o tempo dos banhos.")
        else:
            st.error("🚨 **Atenção Prioritária!** Alto potencial de desperdício. Comece desligando torneiras e trocando lâmpadas por modelos LED.")

# -----------------------------------------------------------------------------
# TAB 4: REGISTRO DE VAZAMENTOS
# -----------------------------------------------------------------------------
with tab4:
    st.header("🔍 Caça e Registro de Vazamentos")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        local = st.selectbox("Local do Vazamento", ["Torneira", "Chuveiro", "Vaso Sanitário / Descarga", "Infiltração", "Tubulação Externa"])
        gravidade = st.select_slider("Gravidade do Vazamento", options=["Gotejamento Lento", "Gotejamento Rápido", "Fluxo Contínuo"])
        
    with col_v2:
        est_perda = 100 if gravidade == "Gotejamento Lento" else (300 if gravidade == "Gotejamento Rápido" else 1000)
        st.info(f"💧 **Desperdício Estimado:** ~{est_perda} Litros/mês")

    if st.button("Registrar Ocorrência"):
        st.session_state.vazamentos_detectados.append({"Local": local, "Gravidade": gravidade, "Desperdício (L/mês)": est_perda})
        st.success(f"Vazamento no(a) **{local}** registrado com sucesso!")

    if st.session_state.vazamentos_detectados:
        st.markdown("---")
        st.subheader("📋 Painel de Ocorrências e Impacto Visual")
        df_vaz = pd.DataFrame(st.session_state.vazamentos_detectados)
        
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.dataframe(df_vaz, use_container_width=True)
        with col_t2:
            fig_vaz = px.bar(df_vaz, x="Local", y="Desperdício (L/mês)", color="Gravidade", title="Desperdício por Ponto Registrado", color_discrete_sequence=['#52b788', '#2d6a4f', '#1b4332'])
            st.plotly_chart(fig_vaz, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5: GAMIFICAÇÃO
# -----------------------------------------------------------------------------
with tab5:
    st.header("🎮 Suas Conquistas EcoTwin")
    if meta_reducao_pct >= 20:
        st.balloons()
        st.success("🏆 **Nível: Mestre Sustentável** — Meta de redução superior a 20%!")
    elif meta_reducao_pct >= 10:
        st.info("🛡️ **Nível: Defensor do Planeta** — Meta de redução entre 10% e 19%.")
    else:
        st.warning("🌱 **Nível: Aprendiz Consciente** — Aumente sua meta para desbloquear novos níveis!")

# -----------------------------------------------------------------------------
# TAB 6: RELATÓRIOS
# -----------------------------------------------------------------------------
with tab6:
    st.header("📄 Relatório Técnico em PDF")
    st.write("Gere e baixe o documento oficial em formato PDF com os indicadores consolidados:")
    
    pdf_bytes = gerar_pdf()
    
    st.download_button(
        label="📥 Baixar Relatório Técnico em PDF",
        data=pdf_bytes,
        file_name="Relatorio_Tecnico_EcoTwin.pdf",
        mime="application/pdf",
        use_container_width=True
    )mime="text/plain", use_container_width=True)