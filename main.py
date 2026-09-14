import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# Inteligência Artificial
from sklearn.linear_model import LinearRegression

# Relatórios PDF
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
        {"role": "assistant", "content": "🤖 **Olá! Eu sou o Aero!** Seu copiloto de sustentabilidade. Como posso analisar o seu consumo hoje?"}
    ]

# CSS Customizado (Verde Escuro Refinado + Aero)
st.markdown("""
    <style>
    /* Fundo e Texto */
    .stApp {
        background-color: #0E231A;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        color: #ECFDF5 !important;
    }
    p, span, label, div, li { color: #E2E8F0 !important; }
    h1, h2, h3, h4 { color: #34D399 !important; font-weight: 700 !important; margin-bottom: 0.5rem; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #081610;
        border-right: 1px solid #1C3A2D;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid #1C3A2D;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #152E23;
        border-radius: 12px 12px 4px 4px !important;
        color: #A7F3D0 !important;
        font-weight: 600;
        border: 1px solid #234737;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1C3A2D;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: #FFFFFF !important;
        border-color: #34D399;
    }

    /* Cards */
    .eco-card {
        background: #152E23;
        padding: 18px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        border: 1px solid #234737;
        margin-bottom: 15px;
        transition: all 0.25s ease;
    }
    .eco-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(16, 185, 129, 0.15); }

    /* Widget Flutuante Aero */
    .aero-widget-link {
        position: fixed; bottom: 20px; right: 25px; z-index: 9999;
        display: flex; align-items: center; gap: 10px; cursor: pointer; text-decoration: none !important;
        transition: all 0.3s ease;
    }
    .aero-widget-link:hover { transform: scale(1.05) translateY(-3px); }
    .aero-bubble {
        background: #FFFFFF; color: #0F172A !important; padding: 8px 14px;
        border-radius: 12px 12px 2px 12px; font-weight: 700; font-size: 13px;
        border: 2px solid #10B981; box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .aero-avatar {
        width: 48px; height: 48px; background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        border: 2px solid #A7F3D0; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-size: 22px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Widget Aero Flutuante
st.markdown("""
    <a href="?nav=aero" target="_self" class="aero-widget-link" title="Falar com Aero">
        <div class="aero-bubble">Olá, sou o Aero</div>
        <div class="aero-avatar">🤖</div>
    </a>
""", unsafe_allow_html=True)

st.title("EcoTwin | Monitoramento & Inteligência Ambiental")

# -----------------------------------------------------------------------------
# DADOS GLOBAIS E SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.header("🏠 Dados Gerais (Residência)")
moradores = st.sidebar.number_input("Número de Moradores", min_value=1, value=4)
energia_kwh = st.sidebar.number_input("Energia Mensal (kWh)", min_value=10, value=220)
meta_reducao = st.sidebar.slider("Meta de Redução (%)", 5, 50, 10)

# -----------------------------------------------------------------------------
# ORGANIZAÇÃO DAS 8 ABAS
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

# Verifica roteamento
if st.session_state.active_tab == 4:
    st.session_state.active_tab = 0
    st.rerun()

# --- CÁLCULOS BASE ---
# (Eles usam dados da sidebar + sliders padrão para exibir o diagnóstico inicial)
# Serão recalculados com precisão na Aba 2, mas precisamos de valores base.
co2_energia = energia_kwh * 0.085 * 12
co2_total = co2_energia + (moradores * 150) # Estimativa base
arvores_eq = int(co2_total / 15)

# ==========================================
# 1. ABA: DIAGNÓSTICO
# ==========================================
with tabs[0]:
    st.header("📊 Diagnóstico de Impacto Ambiental")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Pegada de Carbono Atual", f"{co2_total:,.0f} kg", f"-{meta_reducao}% meta", delta_color="inverse")
    col2.metric("Consumo Energético", f"{energia_kwh} kWh/mês")
    col3.metric("Árvores Necessárias", f"{arvores_eq} árvores")
    
    st.markdown("---")
    
    c_graf1, c_graf2 = st.columns(2)
    with c_graf1:
        st.subheader("Distribuição da Pegada (Estimativa)")
        df_donut = pd.DataFrame({
            "Fonte": ["Energia", "Transporte (Est.)", "Alimentação (Est.)", "Outros"],
            "Impacto": [co2_energia, co2_total*0.3, co2_total*0.4, co2_total*0.1]
        })
        fig_donut = px.pie(df_donut, values="Impacto", names="Fonte", hole=0.5, color_discrete_sequence=['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6'])
        fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E2E8F0'))
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_graf2:
        st.subheader("Cenário: Atual vs Meta")
        df_bar = pd.DataFrame({
            "Cenário": ["Atual", f"Com Redução de {meta_reducao}%"],
            "Emissão": [co2_total, co2_total * (1 - (meta_reducao/100))]
        })
        fig_bar = px.bar(df_bar, x="Cenário", y="Emissão", color="Cenário", color_discrete_sequence=['#EF4444', '#10B981'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E2E8F0'))
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 2. ABA: CALCULADORA PESSOAL
# ==========================================
with tabs[1]:
    st.header("🧮 Calculadora Pessoal de Hábitos")
    st.write("Ajuste seus hábitos diários e compare com a média brasileira.")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        banho_min = st.slider("Tempo de banho diário (minutos)", 0, 60, 15)
        transporte_km = st.slider("Transporte particular diário (km)", 0, 100, 10)
        
    with col_calc2:
        carne_dias = st.slider("Consumo de carne vermelha (dias/semana)", 0, 7, 4)
        lixo_sacos = st.slider("Sacos de lixo gerados (por semana)", 0, 20, 5)
        
    st.markdown("### 📈 Comparativo com a Média Nacional")
    c1, c2, c3, c4 = st.columns(4)
    
    # Médias BR estimadas
    c1.metric("Banho", f"{banho_min} min", f"{banho_min - 12} min vs BR", delta_color="inverse")
    c2.metric("Transporte", f"{transporte_km} km", f"{transporte_km - 15} km vs BR", delta_color="inverse")
    c3.metric("Carne", f"{carne_dias} dias", f"{carne_dias - 3} dias vs BR", delta_color="inverse")
    c4.metric("Lixo", f"{lixo_sacos} sacos", f"{lixo_sacos - 4} sacos vs BR", delta_color="inverse")

# ==========================================
# 3. ABA: CARBON TWIN
# ==========================================
with tabs[2]:
    st.header("🌳 Carbon Twin | Gêmeo Digital Florestal")
    st.markdown("""
    <div class="eco-card">
        <h4>O que é o Débito de Carbono?</h4>
        <p>Cada atividade do dia a dia (energia, transporte, alimentação) emite gases de efeito estufa. O <b>Carbon Twin</b> calcula quantas árvores seriam necessárias para "respirar" e neutralizar essa poluição ao longo de um ano.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader(f"Sua Floresta Virtual ({arvores_eq} árvores necessárias)")
    
    if arvores_eq > 100:
        st.warning("Seu consumo exige uma floresta muito grande! Reduza seus impactos.")
    
    # Renderização da floresta
    grid_arvores = "🌳 " * min(arvores_eq, 200) # Cap visual em 200
    st.markdown(f"<div style='font-size: 24px; line-height: 1.6; background: #0A1C14; padding: 15px; border-radius: 10px;'>{grid_arvores}</div>", unsafe_allow_html=True)

# ==========================================
# 4. ABA: MODELO DE IA
# ==========================================
with tabs[3]:
    st.header("🧠 Modelo de IA (Projeção Linear)")
    st.write("Usando Machine Learning (Scikit-Learn) para prever seu consumo futuro de energia.")
    
    # Dados históricos simulados (com base no consumo atual)
    meses_hist = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    consumo_hist = np.array([energia_kwh*0.9, energia_kwh*0.95, energia_kwh*1.05, energia_kwh*0.98, energia_kwh*1.02, energia_kwh])
    
    # Regressão Linear
    model = LinearRegression()
    model.fit(meses_hist, consumo_hist)
    
    # Previsão para próximos meses
    meses_futuros = np.array([7, 8, 9]).reshape(-1, 1)
    previsoes = model.predict(meses_futuros)
    
    # Gráfico
    fig_ml = go.Figure()
    fig_ml.add_trace(go.Scatter(x=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"], y=consumo_hist, mode='lines+markers', name='Histórico', line=dict(color='#10B981', width=3)))
    fig_ml.add_trace(go.Scatter(x=["Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"], y=[consumo_hist[-1]] + list(previsoes), mode='lines+markers', name='Projeção IA', line=dict(color='#3B82F6', width=3, dash='dash')))
    fig_ml.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E2E8F0'))
    
    st.plotly_chart(fig_ml, use_container_width=True)
    st.info(f"💡 **IA Analítica:** A tendência aponta que seu consumo médio nos próximos meses será de **{previsoes.mean():.0f} kWh**.")

# ==========================================
# 5. ABA: CHAT AERO
# ==========================================
with tabs[4]:
    st.header("🤖 Consultoria com o Assistente Aero")
    st.write("Tire dúvidas sobre seus dados de consumo.")
    
    # Botões rápidos
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    perg_clicada = None
    if c_btn1.button("⚡ Como diminuir energia?"): perg_clicada = "Como posso reduzir meu consumo de energia?"
    if c_btn2.button("🌳 O que é Carbon Twin?"): perg_clicada = "Me explique o conceito do Carbon Twin."
    if c_btn3.button("💧 Dica sobre banhos?"): perg_clicada = "Tem alguma dica para economizar água no banho?"
    
    st.markdown("---")
    
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input
    user_input = st.chat_input("Pergunte ao Aero...")
    prompt = perg_clicada or user_input
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Resposta Simples do Bot
        with st.chat_message("assistant"):
            p_lower = prompt.lower()
            if "energia" in p_lower:
                resp = f"Você consome {energia_kwh} kWh. Tente apagar luzes desnecessárias e reduzir o tempo de eletrônicos ligados. A meta é reduzir {meta_reducao}%!"
            elif "twin" in p_lower or "árvore" in p_lower:
                resp = f"Seu Carbon Twin mostra que você precisa de {arvores_eq} árvores para compensar suas emissões anuais de {co2_total:,.0f} kg."
            elif "água" in p_lower or "banho" in p_lower:
                resp = f"Tomar banhos mais curtos economiza dezenas de litros. 1 minuto a menos por dia poupa muita água no mês!"
            else:
                resp = "Que interessante! Como assistente Aero, sugiro sempre olhar o painel 'Diagnóstico' para rastrear seu impacto geral."
            
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# ==========================================
# 6. ABA: QUIZ E GAMIFICAÇÃO
# ==========================================
with tabs[5]:
    st.header("📝 Quiz Gamificado: Mito ou Verdade?")
    st.write("Teste seus conhecimentos ambientais!")
    
    q1 = st.radio("1. Deixar aparelhos na tomada em stand-by não consome energia.", ["Selecione...", "Mito", "Verdade"])
    q2 = st.radio("2. A produção de carne bovina é uma das maiores geradoras de gás metano.", ["Selecione...", "Mito", "Verdade"])
    
    if st.button("Verificar Respostas 🎮"):
        if q1 == "Mito" and q2 == "Verdade":
            st.success("🎉 Parabéns! Você acertou todas!")
            st.balloons()
        else:
            st.error("❌ Ops, algumas respostas estão incorretas. Tente novamente!")

# ==========================================
# 7. ABA: VAZAMENTOS
# ==========================================
with tabs[6]:
    st.header("🔍 Simulador e Registro de Vazamentos")
    st.write("Descubra quanta água um pequeno vazamento desperdiça.")
    
    local = st.selectbox("Local do Vazamento", ["Torneira Pingando", "Vaso Sanitário (Filete)", "Cano Estourado"])
    gotas = st.slider("Intensidade (Escala 1 a 10)", 1, 10, 5)
    
    perda_estimada = gotas * 30 * 15 # Multiplicador simulado
    st.warning(f"💧 Perda estimada: **{perda_estimada} Litros/mês**")
    
    if st.button("Registrar Vazamento"):
        st.session_state.vazamentos.append({"Local": local, "Intensidade": gotas, "Perda L": perda_estimada})
        st.success("Ocorrência registrada no sistema!")
        
    if st.session_state.vazamentos:
        st.markdown("### Histórico de Ocorrências")
        st.dataframe(pd.DataFrame(st.session_state.vazamentos))

# ==========================================
# 8. ABA: RELATÓRIOS PDF
# ==========================================
with tabs[7]:
    st.header("📄 Geração de Laudo em PDF")
    st.write("Baixe o consolidado das suas métricas para impressão ou envio.")
    
    def gerar_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.HexColor('#065f46'))
        
        elements = [
            Paragraph("Relatório de Impacto Ambiental - EcoTwin", title_style),
            Spacer(1, 15)
        ]
        
        dados = [
            ["Métrica", "Resultado"],
            ["Moradores", str(moradores)],
            ["Energia Mensal", f"{energia_kwh} kWh"],
            ["Pegada de Carbono", f"{co2_total:,.1f} kg CO2/ano"],
            ["Equivalência Florestal", f"{arvores_eq} árvores"],
            ["Meta de Redução", f"{meta_reducao}%"]
        ]
        
        tabela = Table(dados, colWidths=[200, 200])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        
        elements.append(tabela)
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    pdf_file = gerar_pdf()
    
    st.download_button(
        label="📥 Fazer Download do Relatório (PDF)",
        data=pdf_file,
        file_name="EcoTwin_Relatorio.pdf",
        mime="application/pdf",
        use_container_width=True
    )