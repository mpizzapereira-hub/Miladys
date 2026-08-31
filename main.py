import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EcoTwin - Monitoramento Residencial",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def formatar_numero(valor, casas=0):
    texto = f"{valor:,.{casas}f}"
    return (
        texto
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


# ESTILIZAÇÃO VISUAL
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg,
            #f7fbf3 0%,
            #eef7e8 55%,
            #e4f1dd 100%
        );
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #075b32 0%,
            #064526 55%,
            #04371f 100%
        );
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stNumberInput"] input {
        background-color: #073d25 !important;
        color: white !important;
        border: 1px solid #3b9c68 !important;
        border-radius: 10px !important;
    }

    .hero {
        position: relative;
        background: linear-gradient(
            110deg,
            rgba(255,255,255,0.98),
            rgba(239,248,231,0.97)
        );
        border: 1px solid #d9e8d4;
        border-radius: 24px;
        padding: 30px 38px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(29,79,42,0.10);
    }

    .hero-title {
        color: #075b32;
        font-size: 38px;
        font-weight: 850;
    }

    .hero-subtitle {
        color: #3d893b;
        font-size: 17px;
        font-weight: 750;
        margin-top: 6px;
    }

    .section-title {
        color: #174a2e;
        font-size: 22px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.97);
        border: 1px solid #dbe8d8;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 7px 18px rgba(36,70,42,0.10);
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #1b4d2c !important;
        font-weight: 800 !important;
    }

    div[data-testid="stDownloadButton"] button {
        background: #075b32;
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: 800;
    }

    .badge-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #38b000;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# BARRA LATERAL - ENTRADA DE DADOS
st.sidebar.markdown("# 💧 EcoTwin")
st.sidebar.markdown("### Perfil da Residência")
st.sidebar.markdown("---")

moradores = st.sidebar.number_input(
    "Número de moradores",
    min_value=1,
    value=3,
    step=1,
)

banheiros = st.sidebar.number_input(
    "Número de banheiros",
    min_value=1,
    value=2,
    step=1,
)

uso_jardim_piscina = st.sidebar.checkbox(
    "Possui quintal com lavagem ou piscina?",
    value=False,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Consumo Mensal")

consumo_atual_m3 = st.sidebar.number_input(
    "Seu consumo mensal atual (m³)",
    help="1 m³ equivale a 1.000 litros. Verifique em sua conta.",
    min_value=1.0,
    value=18.0,
    step=1.0,
)

tarifa_m3 = st.sidebar.number_input(
    "Tarifa aproximada (R$/m³)",
    min_value=1.0,
    value=8.50,
    step=0.50,
)

meta_reducao_desejada = st.sidebar.slider(
    "Sua meta de redução (%)",
    min_value=0,
    max_value=50,
    value=15,
    step=5,
)


# CÁLCULOS PRINCIPAIS
consumo_base_pessoa_m3 = 3.6
adicional_banheiro_m3 = banheiros * 0.5
adicional_jardim_m3 = 3.0 if uso_jardim_piscina else 0.0

consumo_estimado_ideal_m3 = (
    (moradores * consumo_base_pessoa_m3)
    + adicional_banheiro_m3
    + adicional_jardim_m3
)

consumo_atual_litros = consumo_atual_m3 * 1000
consumo_ideal_litros = consumo_estimado_ideal_m3 * 1000

reducao_meta_litros = consumo_atual_litros * (meta_reducao_desejada / 100)
consumo_meta_litros = consumo_atual_litros - reducao_meta_litros

custo_atual_mes = consumo_atual_m3 * tarifa_m3
economia_financeira_mes = (reducao_meta_litros / 1000) * tarifa_m3
economia_financeira_ano = economia_financeira_mes * 12
litros_economizados_ano = reducao_meta_litros * 12

diferenca_ideal_pct = (
    ((consumo_atual_litros - consumo_ideal_litros) / consumo_ideal_litros) * 100
)


# CLASSIFICAÇÃO E BADGES
if diferenca_ideal_pct <= -10:
    classificacao = "Excelente"
    badge = "🏆 Mestre EcoTwin"
    cor_status = "success"
    explicacao = "Parabéns! O consumo da sua casa está abaixo da média recomendada."
elif diferenca_ideal_pct <= 5:
    classificacao = "Muito boa"
    badge = "⚡ Guardião dos Recursos"
    cor_status = "success"
    explicacao = "Muito bom! O consumo da sua residência está dentro da média estimada."
elif diferenca_ideal_pct <= 25:
    classificacao = "Boa"
    badge = "🌿 Consumidor Consciente"
    cor_status = "info"
    explicacao = "Seu consumo está aceitável, mas há espaço para otimizações na rotina."
elif diferenca_ideal_pct <= 50:
    classificacao = "Dá para melhorar"
    badge = "💧 Aprendiz da Sustentabilidade"
    cor_status = "warning"
    explicacao = "Consumo acima da média ideal. Aplicar a meta trará ótimo alívio na conta."
else:
    classificacao = "Péssima"
    badge = "🚨 Alerta Vermelho de Desperdício"
    cor_status = "error"
    explicacao = "Atenção! Consumo muito elevado. Verifique se há vazamentos ocultos."


# CABEÇALHO
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">EcoTwin - Plataforma Dinâmica de Água 🏠💧</div>
        <div class="hero-subtitle">
            Simulações, diagnósticos interativos e caça a vazamentos para sua casa.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ABAS DE NAVEGAÇÃO INTERATIVAS
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Diagnóstico & Metas",
        "🎛️ Quiz de Hábitos",
        "🚰 Caça aos Vazamentos",
        "📈 Histórico do Ano",
        "📄 Relatório & Dicas",
    ]
)


# ABA 1: DIAGNÓSTICO E METAS
with tab1:
    st.markdown('<div class="section-title">Resultados da Sua Residência</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Consumo Atual Mensal", f"{formatar_numero(consumo_atual_litros)} L", f"{consumo_atual_m3:.0f} m³/mês")
    c2.metric("Estimativa Ideal da Casa", f"{formatar_numero(consumo_ideal_litros)} L", f"{consumo_estimado_ideal_m3:.1f} m³ ideal")
    c3.metric("Gasto Mensal Atual", f"R$ {formatar_numero(custo_atual_mes, 2)}")

    st.markdown("---")
    st.markdown('<div class="section-title">Sua Meta e Economia Estimada</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Água a Economizar/Mês", f"{formatar_numero(reducao_meta_litros)} L", f"-{meta_reducao_desejada}%")
    m2.metric("Economia Financeira/Mês", f"R$ {formatar_numero(economia_financeira_mes, 2)}")
    m3.metric("Economia Financeira/Ano", f"R$ {formatar_numero(economia_financeira_ano, 2)}")

    g_col1, g_col2 = st.columns([2, 1])

    with g_col1:
        st.subheader("Comparativo de Consumo x Metas")
        df_grafico = pd.DataFrame(
            {
                "Cenário": ["Consumo Atual", "Estimativa Ideal", f"Meta (-{meta_reducao_desejada}%)"],
                "Litros": [consumo_atual_litros, consumo_ideal_litros, consumo_meta_litros],
            }
        )
        grafico = (
            alt.Chart(df_grafico)
            .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10, size=70)
            .encode(
                x=alt.X("Cenário:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Litros:Q", title="Litros por Mês"),
                color=alt.Color(
                    "Cenário:N",
                    scale=alt.Scale(
                        domain=["Consumo Atual", "Estimativa Ideal", f"Meta (-{meta_reducao_desejada}%)"],
                        range=["#0d67a8", "#2a9d8f", "#e76f51"],
                    ),
                    legend=None,
                ),
                tooltip=["Cenário", "Litros"],
            )
            .properties(height=320, background="#ffffff")
            .configure_view(stroke=None)
        )
        st.altair_chart(grafico, use_container_width=True, theme=None)

    with g_col2:
        st.subheader("Sua Conquista")
        st.markdown(
            f"""
            <div class="badge-card">
                <h2 style="margin:0;">{badge}</h2>
                <p style="font-weight:bold; color:#174a2e; margin-top:10px;">Status: {classificacao}</p>
                <p style="font-size:14px; color:#555;">{explicacao}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🌳 Impacto Equivalente Anual")
        caixas_agua = litros_economizados_ano / 1000
        garrafas_pet = litros_economizados_ano / 2
        st.write(f"• **{formatar_numero(caixas_agua)}** caixas d'água de 1.000L salvas")
        st.write(f"• **{formatar_numero(garrafas_pet)}** garrafas PET de 2L poupadas")


# ABA 2: QUIZ DE HÁBITOS
with tab2:
    st.markdown('<div class="section-title">🎛️ Simule seu consumo baseado em hábitos reais</div>', unsafe_allow_html=True)
    st.info("Responda abaixo para calcular uma estimativa rápida do gasto de água da sua rotina:")

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        tempo_banho = st.select_slider(
            "Tempo médio do banho por pessoa (minutos):",
            options=[5, 10, 15, 20, 25],
            value=10,
        )
        escova_torneira_aberta = st.radio(
            "Escova os dentes com a torneira aberta?",
            ["Nunca", "Às vezes", "Sempre"],
        )

    with col_q2:
        frequencia_roupa = st.number_input(
            "Quantas vezes usam a máquina de lavar por semana?",
            min_value=1,
            value=3,
        )
        lava_calcada = st.checkbox("Lava calçada/quintal com mangueira?", value=False)

    # Cálculo aproximado do Quiz
    gasto_banho_mes = moradores * (tempo_banho * 12) * 30
    gasto_escovar_mes = moradores * (24 if escova_torneira_aberta == "Sempre" else (12 if escova_torneira_aberta == "Às vezes" else 0)) * 30
    gasto_roupa_mes = frequencia_roupa * 100 * 4
    gasto_calcada_mes = 280 * 4 if lava_calcada else 0

    consumo_quiz_total = gasto_banho_mes + gasto_escovar_mes + gasto_roupa_mes + gasto_calcada_mes

    st.success(f"### Estimativa Calculada pelo Quiz: **{formatar_numero(consumo_quiz_total)} Litros / mês**")

    # Gráfico do Quiz
    df_quiz = pd.DataFrame(
        {
            "Atividade": ["Banhos", "Torneira/Dentes", "Lavar Roupa", "Calçada/Quintal"],
            "Litros": [gasto_banho_mes, gasto_escovar_mes, gasto_roupa_mes, gasto_calcada_mes],
        }
    )
    grafico_quiz = alt.Chart(df_quiz).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("Litros:Q"),
        color=alt.Color("Atividade:N", scale=alt.Scale(scheme="category10")),
        tooltip=["Atividade", "Litros"],
    ).properties(height=300)

    st.altair_chart(grafico_quiz, use_container_width=True)


# ABA 3: CAÇA AOS VAZAMENTOS
with tab3:
    st.markdown('<div class="section-title">🚰 Calculadora de Desperdícios Ocultos</div>', unsafe_allow_html=True)
    st.warning("Selecione os problemas que você suspeita ou encontrou na sua casa:")

    v1 = st.checkbox("Torneira pingando devagar (1 gota/segundo) — ~46 L/dia")
    v2 = st.checkbox("Torneira correndo em fio fino — ~180 L/dia")
    v3 = st.checkbox("Vazamento contínuo no vaso sanitário / descarga — ~330 L/dia")

    perda_diaria = (46 if v1 else 0) + (180 if v2 else 0) + (330 if v3 else 0)
    perda_mensal_litros = perda_diaria * 30
    perda_mensal_reais = (perda_mensal_litros / 1000) * tarifa_m3

    v_col1, v_col2 = st.columns(2)
    v_col1.metric("Perda Diária Desperdiçada", f"{formatar_numero(perda_diaria)} Litros/dia")
    v_col2.metric("Prejuízo Estimado na Conta", f"R$ {formatar_numero(perda_mensal_reais, 2)} / mês")

    if perda_diaria > 0:
        st.error(f"🚨 Você pode estar jogando fora **{formatar_numero(perda_mensal_litros)} litros de água** todos os meses!")


# ABA 4: HISTÓRICO DO ANO
with tab4:
    st.markdown('<div class="section-title">📈 Histórico e Tendência do Consumo</div>', unsafe_allow_html=True)

    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    # Simulação de variação histórica em volta do consumo digitado
    valores_historicos = [
        consumo_atual_m3 * 1.1,
        consumo_atual_m3 * 1.05,
        consumo_atual_m3 * 1.15,
        consumo_atual_m3 * 0.98,
        consumo_atual_m3 * 1.02,
        consumo_atual_m3,
    ]

    df_historico = pd.DataFrame({"Mês": meses, "Consumo (m³)": valores_historicos})

    grafico_linha = (
        alt.Chart(df_historico)
        .mark_line(point=True, color="#075b32", strokeWidth=3)
        .encode(
            x=alt.X("Mês:N", sort=None),
            y=alt.Y("Consumo (m³):Q"),
            tooltip=["Mês", "Consumo (m³)"],
        )
        .properties(height=320)
    )

    st.altair_chart(grafico_linha, use_container_width=True)


# ABA 5: RELATÓRIO E DICAS
with tab5:
    st.markdown('<div class="section-title">💡 Dicas de Economia Recomendadas</div>', unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown("🚿 **Banhos mais curtos:** Reduzir 5 min no banho economiza 90 Litros/dia.")
    with d2:
        st.markdown("🚰 **Torneiras fechadas:** Fechar ao escovar dentes economiza 12 Litros/uso.")
    with d3:
        st.markdown("🌧️ **Reuso de água:** Usar água da chuva ou da máquina para lavar quintal.")

    st.markdown("---")
    st.markdown('<div class="section-title">📄 Baixar Relatório do Projeto</div>', unsafe_allow_html=True)

    relatorio_texto = f"""
==================================================
        RELATÓRIO DE CONSUMO - ECOTWIN
==================================================

DADOS DA RESIDÊNCIA:
Moradores: {moradores} | Banheiros: {banheiros}
Área externa com lavagem: {'Sim' if uso_jardim_piscina else 'Não'}

RESULTADOS DO DIAGNÓSTICO:
Consumo Atual: {formatar_numero(consumo_atual_litros)} Litros ({consumo_atual_m3} m³)
Consumo Ideal Recomendado: {formatar_numero(consumo_ideal_litros)} Litros ({consumo_estimado_ideal_m3:.1f} m³)
Gasto Mensal Estimado: R$ {formatar_numero(custo_atual_mes, 2)}
Classificação: {classificacao.upper()} ({badge})

PLANOS E METAS (-{meta_reducao_desejada}%):
Meta de economia mensal: {formatar_numero(reducao_meta_litros)} Litros
Economia financeira mensal: R$ {formatar_numero(economia_financeira_mes, 2)}
Economia financeira anual: R$ {formatar_numero(economia_financeira_ano, 2)}

==================================================
Gerado pelo EcoTwin - EcoMonitoramento Inteligente
==================================================
"""

    st.download_button(
        "Baixar Relatório Completo (.txt)",
        data=relatorio_texto,
        file_name="relatorio_ecotwin_completo.txt",
        mime="text/plain",
        use_container_width=True,
    )