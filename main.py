import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import io

# Imports do ReportLab para geração de PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO SUSTENTÁVEL (VERDE CLARO E ESCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTwin - Plataforma Dinâmica Sustentável",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Tons de Verde Claro e Escuro)
st.markdown("""
    <style>
    /* Estilo do fundo e da sidebar */
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
    
    /* Botões personalizados */
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

    /* Títulos e Destaques */
    h1, h2, h3 {
        color: #1b4332 !important;
    }
    
    /* Destaques de métricas */
    [data-testid="stMetricValue"] {
        color: #2d6a4f !important;
    }

    /* Abas estilizadas */
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
    </style>
""", unsafe_allow_html=True)

# Inicialização do Session State
if "historico" not in st.session_state:
    st.session_state.historico = []

if "vazamentos_detectados" not in st.session_state:
    st.session_state.vazamentos_detectados = []

if "quiz_pontos" not in st.session_state:
    st.session_state.quiz_pontos = 0

# -----------------------------------------------------------------------------
# ALERTA AMBIENTAL DO AERO NO TOPO
# -----------------------------------------------------------------------------
alertas_aero = [
    "☀️ **Alerta do Aero:** Previsão de dias quentes! Banhos de até 5 minutos economizam água e reduzem o consumo de energia.",
    "🌧️ **Dica do Aero:** Aproveite os dias de chuva para captação de água pluvial. Utilize para regar plantas e lavar áreas externas!",
    "💡 **Dica do Aero:** Lâmpadas LED e aparelhos fora da tomada ajudam a reduzir a emissão indireta de gases de efeito estufa.",
    "🚗 **Dica do Aero:** Reduzir o uso de veículo individual diminui o impacto de emissões de carbono no mês!",
    "🚿 **Desafio do Aero:** Lembre-se de fechar a torneira enquanto ensaboa as mãos ou escova os dentes hoje."
]
st.warning(random.choice(alertas_aero))

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR) - DADOS RESIDENCIAIS E SUSTENTABILIDADE
# -----------------------------------------------------------------------------
st.sidebar.title("🌿 EcoTwin")
st.sidebar.caption("Gêmeo Digital de Consumo Sustentável")

st.sidebar.markdown("---")
st.sidebar.header("🏠 Dados da Residência (Água)")

moradores = st.sidebar.number_input("Número de moradores", min_value=1, max_value=15, value=4, step=1)
tempo_banho = st.sidebar.number_input("Tempo médio de banho (min por pessoa/dia)", min_value=1, max_value=60, value=12, step=1)
frequencia_maquina = st.sidebar.number_input("Uso da máquina de lavar (vezes/semana)", min_value=0, max_value=21, value=3, step=1)
banheiros = st.sidebar.number_input("Número de banheiros na casa", min_value=1, max_value=10, value=2, step=1)
uso_jardim_piscina = st.sidebar.selectbox("Possui jardim ou piscina com uso de água?", ["Não", "Jardim pequeno", "Jardim grande / Piscina"])

st.sidebar.markdown("---")
st.sidebar.header("🌍 Sustentabilidade & Carbono")

energia_kwh = st.sidebar.number_input("Consumo mensal de energia (kWh)", min_value=0, max_value=2000, value=220, step=10)
usa_carro = st.sidebar.radio("Utiliza veículo próprio?", ["Não", "Sim"], index=1)

if usa_carro == "Sim":
    tipo_combustivel = st.sidebar.selectbox(
        "Tipo de combustível / veículo",
        ["Gasolina", "Etanol", "Diesel", "Híbrido", "Elétrico"]
    )
    km_mes = st.sidebar.slider("Quilômetros rodados por mês (km)", min_value=0, max_value=5000, value=400, step=50)
else:
    tipo_combustivel = "N/A"
    km_mes = 0

meta_reducao_pct = st.sidebar.slider("Meta de redução ambiental (%)", min_value=5, max_value=50, value=10, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("🍃 Assistente Aero")
st.sidebar.caption("Seu guia de Água, Energia & Carbono!")
st.sidebar.caption("Desenvolvido por **Maria Laura** e **Julia Aguiar**")

# -----------------------------------------------------------------------------
# CÁLCULOS PRINCIPAIS
# -----------------------------------------------------------------------------
# 1. Água
litros_banho_pessoa_dia = tempo_banho * 9
litros_banho_total_mes = litros_banho_pessoa_dia * moradores * 30
litros_maquina_mes = frequencia_maquina * 4 * 100

fator_jardim = 0
if uso_jardim_piscina == "Jardim pequeno":
    fator_jardim = 1500
elif uso_jardim_piscina == "Jardim grande / Piscina":
    fator_jardim = 4000

consumo_outro_mes = moradores * 30 * 40 + fator_jardim
consumo_atual_litros = litros_banho_total_mes + litros_maquina_mes + consumo_outro_mes

consumo_ideal_litros = consumo_atual_litros * (1.0 - (meta_reducao_pct / 100.0))
economia_agua_litros = consumo_atual_litros - consumo_ideal_litros

custo_agua_atual = consumo_atual_litros * 0.008
custo_agua_ideal = consumo_ideal_litros * 0.008

# 2. Energia (kWh)
co2_energia_kg = energia_kwh * 0.085
custo_energia_atual = energia_kwh * 0.75

# 3. Transporte (CO2)
fatores_combustivel = {
    "Gasolina": 0.19,
    "Etanol": 0.07,
    "Diesel": 0.24,
    "Híbrido": 0.10,
    "Elétrico": 0.03,
    "N/A": 0.00
}
fator_transporte = fatores_combustivel.get(tipo_combustivel, 0.0)
co2_transporte_kg = km_mes * fator_transporte

# 4. Emissões Totais e Cenário Sustentável
co2_agua_kg = consumo_atual_litros * 0.0005
co2_total_atual_kg = co2_energia_kg + co2_transporte_kg + co2_agua_kg

co2_energia_sust = co2_energia_kg * (1.0 - (meta_reducao_pct / 100.0))
co2_transporte_sust = co2_transporte_kg * (1.0 - (meta_reducao_pct / 100.0))
co2_agua_sust = co2_agua_kg * (1.0 - (meta_reducao_pct / 100.0))
co2_total_sust_kg = co2_energia_sust + co2_transporte_sust + co2_agua_sust

co2_evitado_mes_kg = co2_total_atual_kg - co2_total_sust_kg
co2_evitado_ano_kg = co2_evitado_mes_kg * 12

creditos_carbono_potenciais_mes = co2_evitado_mes_kg / 1000.0
creditos_carbono_potenciais_ano = co2_evitado_ano_kg / 1000.0

# -----------------------------------------------------------------------------
# GAMIFICAÇÃO - LÓGICA DE NÍVEIS
# -----------------------------------------------------------------------------
def obter_nivel_gamificacao(economia_l, co2_evit_kg):
    pontos = (economia_l / 100) + (co2_evit_kg * 5)
    if pontos >= 300:
        return "🏆 Guardião do Planeta (Nível 3)", "Excelente desempenho! Sua casa é uma referência em práticas sustentáveis."
    elif pontos >= 100:
        return "🛡️ Defensor EcoTwin (Nível 2)", "Ótimo progresso! Suas reduções estão fazendo a diferença."
    else:
        return "🌱 Aprendiz do Consumo Consciente (Nível 1)", "Bom começo! Ajuste suas metas para avançar para o próximo nível."

nivel_badge, mensagem_nivel = obter_nivel_gamificacao(economia_agua_litros, co2_evitado_mes_kg)

# -----------------------------------------------------------------------------
# FUNÇÃO DE GERAÇÃO DO RELATÓRIO PDF
# -----------------------------------------------------------------------------
def gerar_pdf_relatorio():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1B4332'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#2D6A4F'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )

    story.append(Paragraph("🌿 EcoTwin - Relatório Integrado e Diagnóstico", title_style))
    story.append(Paragraph("<b>Desenvolvido por:</b> Maria Laura e Julia Aguiar", body_style))
    story.append(Spacer(1, 10))

    data_agua = [
        ["Métrica de Água", "Valor Atual", "Cenário Sustentável", "Economia Prevista"],
        ["Consumo de Água", f"{consumo_atual_litros:,.0f} L/mês", f"{consumo_ideal_litros:,.0f} L/mês", f"{economia_agua_litros:,.0f} L/mês"],
        ["Custo Estimado de Água", f"R$ {custo_agua_atual:.2f}", f"R$ {custo_agua_ideal:.2f}", f"R$ {(custo_agua_atual - custo_agua_ideal):.2f}"]
    ]
    t_agua = Table(data_agua, colWidths=[140, 120, 130, 120])
    t_agua.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D6A4F')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC'))
    ]))
    story.append(Paragraph("1. Diagnóstico do Consumo de Água", h2_style))
    story.append(t_agua)
    story.append(Spacer(1, 12))

    data_eco = [
        ["Categoria", "Parâmetro Residencial", "Emissões Estimadas de CO₂e"],
        ["Energia Elétrica", f"{energia_kwh} kWh/mês", f"{co2_energia_kg:.2f} kg CO₂e/mês"],
        ["Transporte", f"{km_mes} km/mês ({tipo_combustivel})", f"{co2_transporte_kg:.2f} kg CO₂e/mês"],
        ["Tratamento de Água", f"{consumo_atual_litros:,.0f} Litros/mês", f"{co2_agua_kg:.2f} kg CO₂e/mês"],
        ["TOTAL ATUAL", "-", f"{co2_total_atual_kg:.2f} kg CO₂e/mês"]
    ]
    t_eco = Table(data_eco, colWidths=[140, 180, 190])
    t_eco.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4332')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC'))
    ]))
    story.append(Paragraph("2. Energia, Transporte e Impacto Ambiental", h2_style))
    story.append(t_eco)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Projeção Sustentável e Crédito de Carbono Potencial", h2_style))
    story.append(Paragraph(f"<b>Meta de Redução Aplicada:</b> {meta_reducao_pct}%", body_style))
    story.append(Paragraph(f"<b>Redução Potencial de CO₂e:</b> {co2_evitado_mes_kg:.2f} kg CO₂e/mês ({co2_evitado_ano_kg:.2f} kg CO₂e/ano)", body_style))
    story.append(Paragraph(f"<b>Equivalente Potencial em Crédito de Carbono:</b> {creditos_carbono_potenciais_ano:.4f} tCO₂e/ano", body_style))
    story.append(Paragraph("<i>Nota Explicativa: Estes valores representam estimativas educativas de impacto ambiental evitado e NÃO constituem créditos de carbono certificados ou disponíveis para comercialização.</i>", ParagraphStyle('Note', parent=body_style, fontSize=8, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Orientação do Aero", h2_style))
    story.append(Paragraph("• Reduza o tempo nos banhos para até 5 minutos.", body_style))
    story.append(Paragraph("• Mantenha a capacidade da máquina de lavar cheia antes do uso.", body_style))
    story.append(Paragraph("• Evite manter eletrônicos no modo de espera (stand-by).", body_style))
    story.append(Paragraph("• Priorize a otimização de viagens de carro para reduzir uso de combustível.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL - NAVEGAÇÃO POR ABAS
# -----------------------------------------------------------------------------
st.title("EcoTwin - Plataforma Dinâmica Sustentável 🏠🌿")
st.caption("Simulações, diagnósticos interativos, crédito de carbono e prevenção para sua casa.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Diagnóstico & Metas",
    "🌍 Impacto & Carbono",
    "📝 Quiz de Hábitos",
    "🔍 Caça a Vazamentos",
    "🎮 Gamificação",
    "📄 Relatório & Dicas do Aero"
])

# -----------------------------------------------------------------------------
# ABA 1: DIAGNÓSTICO E METAS
# -----------------------------------------------------------------------------
with tab1:
    st.header("📊 Diagnóstico do Consumo Residencial")
    st.write("Acompanhe como os hábitos da sua residência impactam o consumo direto de recursos.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Consumo Mensal de Água", f"{consumo_atual_litros:,.0f} L", f"R$ {custo_agua_atual:.2f}/mês")
    with col2:
        st.metric("Meta de Consumo Sustentável", f"{consumo_ideal_litros:,.0f} L", f"-{meta_reducao_pct}%")
    with col3:
        st.metric("Economia Potencial", f"{economia_agua_litros:,.0f} L", f"R$ {(custo_agua_atual - custo_agua_ideal):.2f}/mês")

    df_agua = pd.DataFrame({
        "Categoria": ["Banhos", "Máquina de Lavar", "Outros Usos (Pias/Jardim/Descargas)"],
        "Litros/Mês": [litros_banho_total_mes, litros_maquina_mes, consumo_outro_mes]
    })
    fig_agua = px.pie(
        df_agua, 
        values="Litros/Mês", 
        names="Categoria", 
        title="Distribuição do Consumo de Água Residencial", 
        hole=0.4,
        color_discrete_sequence=['#2d6a4f', '#52b788', '#74c69d']
    )
    st.plotly_chart(fig_agua, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 2: IMPACTO AMBIENTAL & CRÉDITO DE CARBONO
# -----------------------------------------------------------------------------
with tab2:
    st.header("🌍 Impacto Ambiental & Crédito de Carbono")
    st.write("Acompanhe as emissões de gases de efeito estufa da sua residência e sua projeção sustentável.")

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.metric("Consumo de Energia Elétrica", f"{energia_kwh} kWh", f"{co2_energia_kg:.2f} kg CO₂e/mês")
    with col_e2:
        st.metric("Uso de Transporte", f"{km_mes} km", f"{co2_transporte_kg:.2f} kg CO₂e/mês")
    with col_e3:
        st.metric("Emissões Mensais Totais", f"{co2_total_atual_kg:.2f} kg CO₂e", "estimativa")

    st.markdown("---")
    
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        df_impacto = pd.DataFrame({
            "Fonte de Emissão": ["Energia Elétrica", "Transporte (Veículos)", "Tratamento de Água"],
            "Emissões (kg CO₂e/mês)": [co2_energia_kg, co2_transporte_kg, co2_agua_kg]
        })
        fig_impacto = px.bar(
            df_impacto,
            x="Fonte de Emissão",
            y="Emissões (kg CO₂e/mês)",
            color="Fonte de Emissão",
            title="Distribuição de Emissões de CO₂e",
            text_auto='.2f',
            color_discrete_sequence=['#1b4332', '#2d6a4f', '#52b788']
        )
        st.plotly_chart(fig_impacto, use_container_width=True)

    with col_g2:
        st.subheader("📊 Fator Dominante")
        if co2_energia_kg >= co2_transporte_kg and co2_energia_kg >= co2_agua_kg:
            categoria_maior = "Energia Elétrica"
            dica_categoria = "A energia elétrica representa sua principal fonte de emissão indireta. Desligar aparelhos da tomada reduz essa demanda."
        elif co2_transporte_kg >= co2_energia_kg and co2_transporte_kg >= co2_agua_kg:
            categoria_maior = "Transporte"
            dica_categoria = "O uso de combustível é a principal fonte de emissão. Otimizar viagens de carro ajuda na redução do indicador."
        else:
            categoria_maior = "Consumo de Água"
            dica_categoria = "O volume de água tratada consumido na residência é o destaque no seu perfil de uso."

        st.info(f"👉 **A categoria com maior peso é:** **{categoria_maior}**\n\n{dica_categoria}")

    st.markdown("---")
    st.subheader("🍃 Estimativa de Crédito de Carbono Potencial")
    
    recom_col1, recom_col2 = st.columns(2)
    with recom_col1:
        st.success(f"🌱 **Cenário de Meta ({meta_reducao_pct}% de Redução):**\n"
                   f"- Emissão Atual: **{co2_total_atual_kg:.2f} kg CO₂e/mês**\n"
                   f"- Emissão Projetada: **{co2_total_sust_kg:.2f} kg CO₂e/mês**\n"
                   f"- Redução de Emissão: **{co2_evitado_mes_kg:.2f} kg CO₂e/mês** ({co2_evitado_ano_kg:.2f} kg CO₂e/ano)")

    with recom_col2:
        st.warning(f"📜 **Crédito de Carbono Potencial Evitado:**\n"
                   f"- **{creditos_carbono_potenciais_mes:.4f} tCO₂e/mês**\n"
                   f"- **{creditos_carbono_potenciais_ano:.4f} tCO₂e/ano**\n\n"
                   f"*Nota importante: Os valores calculados representam estimativas educativas de impacto ambiental evitado.*")

# -----------------------------------------------------------------------------
# ABA 3: QUIZ DE HÁBITOS
# -----------------------------------------------------------------------------
with tab3:
    st.header("📝 Quiz de Hábitos Sustentáveis")
    st.write("Avalie as práticas cotidianas da sua residência.")

    p1 = st.radio("1. Você fecha a torneira enquanto escova os dentes?", ["Sempre", "Às vezes", "Raramente"])
    p2 = st.radio("2. Você utiliza a máquina de lavar roupas em sua capacidade máxima?", ["Sempre", "Às vezes", "Raramente"])
    p3 = st.radio("3. Você desliga aparelhos eletrônicos do modo de espera quando não está usando?", ["Sempre", "Às vezes", "Raramente"])

    if st.button("Calcular Pontuação"):
        pontos = 0
        for resp in [p1, p2, p3]:
            if resp == "Sempre":
                pontos += 10
            elif resp == "Às vezes":
                pontos += 5
        
        st.session_state.quiz_pontos = pontos
        st.success(f"Sua pontuação no Quiz é: **{pontos} de 30 pontos**!")
        
        if pontos == 30:
            st.balloons()
            st.write("🎉 Excelente! Seus hábitos estão alinhados com o consumo consciente.")
        elif pontos >= 15:
            st.write("👍 Bom trabalho! Ajustes simples em sua rotina podem melhorar ainda mais esses resultados.")
        else:
            st.write("⚠️ Oportunidade de melhoria: Pequenas atitudes diárias geram grande economia de recursos.")

# -----------------------------------------------------------------------------
# ABA 4: CAÇA A VAZAMENTOS
# -----------------------------------------------------------------------------
with tab4:
    st.header("🔍 Caça a Vazamentos")
    st.write("Identifique e registre pontos de atenção para evitar o desperdício de água.")

    tipo_vazamento = st.selectbox(
        "Selecione o local ou tipo de suspeita:",
        ["Torneira pingando", "Descarga acionando sozinhos / vazando", "Chuveiro gotejando", "Infiltração em parede", "Tubulação externa"]
    )
    intensidade = st.select_slider("Frequência / Intensidade:", options=["Gotejamento lento", "Gotejamento constante", "Fluxo contínuo"])

    if st.button("Registrar Ocorrência"):
        st.session_state.vazamentos_detectados.append({"Tipo": tipo_vazamento, "Intensidade": intensidade})
        st.success("Ocorrência registrada no histórico da residência!")

    if st.session_state.vazamentos_detectados:
        st.subheader("📋 Ocorrências Registradas")
        st.table(pd.DataFrame(st.session_state.vazamentos_detectados))

# -----------------------------------------------------------------------------
# ABA 5: GAMIFICAÇÃO (CORRIGIDA)
# -----------------------------------------------------------------------------
with tab5:
    st.header("🎮 Sistema de Conquistas EcoTwin")
    st.write("Acompanhe sua evolução e desbloqueie insígnias de sustentabilidade!")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.metric("Nível Atual", nivel_badge)
    with col_g2:
        st.metric("Redução Prevista de CO₂e", f"{co2_evitado_mes_kg:.2f} kg/mês")

    st.info(f"💬 **Mensagem do Aero:** {mensagem_nivel}")

    st.markdown("---")
    st.subheader("🏆 Insígnias Conquistadas")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.success("🌱 **Aprendiz do Consumo**\n\nConfigurou suas primeiras metas no EcoTwin.")
    with col_b2:
        if co2_evitado_mes_kg > 10:
            st.success("🛡️ **Defensor EcoTwin**\n\nAlcançou redução superior a 10 kg CO₂e/mês!")
        else:
            st.info("🛡️ **Defensor EcoTwin**\n\n*(Bloqueado: Alcance 10 kg de redução de CO₂e/mês)*")
    with col_b3:
        if co2_evitado_mes_kg > 30:
            st.success("🏆 **Guardião do Planeta**\n\nAlcançou redução superior a 30 kg CO₂e/mês!")
        else:
            st.info("🏆 **Guardião do Planeta**\n\n*(Bloqueado: Alcance 30 kg de redução de CO₂e/mês)*")

# -----------------------------------------------------------------------------
# ABA 6: RELATÓRIO & DICAS DO AERO
# -----------------------------------------------------------------------------
with tab6:
    st.header("📄 Relatório Completo & Dicas do Aero")
    st.write("Consulte as recomendações de otimização do assistente **Aero** e faça o download do relatório técnico consolidado.")

    st.subheader("🍃 Recomendações Práticas do Aero")
    
    c_dica1, c_dica2 = st.columns(2)
    with c_dica1:
        st.info("💧 **Economia de Água:**\n"
                "- Reduza o tempo de banho para 5 minutos.\n"
                "- Utilize a máquina de lavar em capacidade máxima.\n"
                "- Instale arejadores nas torneiras para diminuir a vazão.")
    with c_dica2:
        st.success("💡 **Energia e Redução de Carbono:**\n"
                   "- Priorize a iluminação natural durante o dia.\n"
                   "- Retire aparelhos em stand-by da tomada.\n"
                   "- Planeje rotas para otimizar o uso do veículo.")

    st.markdown("---")
    st.subheader("📥 Exportação de Documento em PDF")
    st.write("Gere o relatório impresso com os dados consolidados de água, energia, carbono e histórico da residência.")

    pdf_bytes = gerar_pdf_relatorio()

    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_ecotwin_completo.pdf",
        mime="application/pdf",
        use_container_width=True
    )