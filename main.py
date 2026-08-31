import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EcoTwin",
    page_icon="🌿",
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


def criar_grafico(dados, titulo_eixo, cores):
    return (
        alt.Chart(dados)
        .mark_bar(
            cornerRadiusTopLeft=10,
            cornerRadiusTopRight=10,
            size=90,
        )
        .encode(
            x=alt.X(
                "Cenário:N",
                title=None,
                sort=["Consumo atual", "Após a redução"],
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=13,
                ),
            ),
            y=alt.Y(
                "Valor:Q",
                title=titulo_eixo,
                axis=alt.Axis(
                    format=",.0f",
                    gridColor="#dce8df",
                ),
            ),
            color=alt.Color(
                "Cenário:N",
                scale=alt.Scale(
                    domain=[
                        "Consumo atual",
                        "Após a redução",
                    ],
                    range=cores,
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Cenário:N", title="Cenário"),
                alt.Tooltip(
                    "Valor:Q",
                    title="Valor",
                    format=",.0f",
                ),
            ],
        )
        .properties(
            height=330,
            background="#ffffff",
        )
        .configure_view(stroke=None)
    )


# VISUAL
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
        overflow: hidden;
        background: linear-gradient(
            110deg,
            rgba(255,255,255,0.98),
            rgba(239,248,231,0.97)
        );
        border: 1px solid #d9e8d4;
        border-radius: 24px;
        padding: 34px 38px;
        margin-bottom: 28px;
        box-shadow: 0 8px 24px rgba(29,79,42,0.10);
    }

    .hero::before {
        content: "🌿";
        position: absolute;
        right: 72px;
        top: 18px;
        font-size: 65px;
        opacity: 0.18;
        transform: rotate(-18deg);
    }

    .hero::after {
        content: "⚡";
        position: absolute;
        right: 14px;
        bottom: 2px;
        font-size: 68px;
        opacity: 0.15;
        transform: rotate(14deg);
    }

    .hero-title {
        color: #075b32;
        font-size: 46px;
        font-weight: 850;
    }

    .hero-subtitle {
        color: #3d893b;
        font-size: 19px;
        font-weight: 750;
        margin-top: 10px;
    }

    .hero-text {
        color: #4d5f52;
        font-size: 17px;
        margin-top: 18px;
        max-width: 790px;
    }

    .section-title {
        color: #174a2e;
        font-size: 25px;
        font-weight: 800;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.97);
        border: 1px solid #dbe8d8;
        border-radius: 18px;
        padding: 20px;
        min-height: 145px;
        box-shadow: 0 7px 18px rgba(36,70,42,0.10);
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #1b4d2c !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #176936;
    }

    .summary {
        background: linear-gradient(
            90deg,
            #075b32,
            #168447
        );
        color: white;
        border-radius: 18px;
        padding: 24px;
        margin-top: 20px;
    }

    .summary h3,
    .summary p {
        color: white;
    }

    div[data-testid="stDownloadButton"] button {
        background: #075b32;
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: 800;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# BARRA LATERAL
st.sidebar.markdown("# EcoTwin")
st.sidebar.markdown("### EcoMonitoramento Urbano Inteligente")
st.sidebar.markdown("---")
st.sidebar.markdown("## Dados da simulação")

residencias = st.sidebar.number_input(
    "Número de residências",
    min_value=1,
    value=1000,
    step=100,
)

agua_por_casa = st.sidebar.number_input(
    "Consumo mensal de água por residência (litros)",
    min_value=1.0,
    value=18000.0,
    step=500.0,
)

energia_por_casa = st.sidebar.number_input(
    "Consumo mensal de energia por residência (kWh)",
    min_value=1.0,
    value=200.0,
    step=10.0,
)

tarifa_kwh = st.sidebar.number_input(
    "Tarifa de energia (R$/kWh)",
    min_value=0.01,
    value=0.75,
    step=0.05,
)

percentual_reducao = st.sidebar.slider(
    "Meta de redução (%)",
    min_value=1,
    max_value=100,
    value=10,
)


# CÁLCULOS
reducao = percentual_reducao / 100

agua_total = residencias * agua_por_casa
energia_total = residencias * energia_por_casa

economia_agua = agua_total * reducao
economia_energia = energia_total * reducao

agua_reduzida = agua_total - economia_agua
energia_reduzida = energia_total - economia_energia

economia_financeira = economia_energia * tarifa_kwh

economia_agua_anual = economia_agua * 12
economia_energia_anual = economia_energia * 12
economia_financeira_anual = economia_financeira * 12

fator_co2 = 0.084
co2_toneladas = (
    economia_energia_anual * fator_co2
) / 1000


# CABEÇALHO
st.markdown(
    (
        '<div class="hero">'
        '<div class="hero-title">EcoTwin</div>'
        '<div class="hero-subtitle">'
        'EcoMonitoramento Urbano Inteligente'
        '</div>'
        '<div class="hero-text">'
        'Simule o impacto da redução do consumo de água e energia '
        'e visualize benefícios econômicos e ambientais.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# RESULTADOS
st.markdown(
    '<div class="section-title">Resultados da simulação</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Água economizada por mês",
    f"{formatar_numero(economia_agua)} L",
)

c2.metric(
    "Energia economizada por mês",
    f"{formatar_numero(economia_energia)} kWh",
)

c3.metric(
    "Economia financeira mensal",
    f"R$ {formatar_numero(economia_financeira, 2)}",
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "Água economizada por ano",
    f"{formatar_numero(economia_agua_anual)} L",
)

c5.metric(
    "Energia economizada por ano",
    f"{formatar_numero(economia_energia_anual)} kWh",
)

c6.metric(
    "CO₂ evitado por ano",
    f"{formatar_numero(co2_toneladas, 2)} toneladas",
)


# GRÁFICOS
st.markdown(
    '<div class="section-title">Comparação de consumo</div>',
    unsafe_allow_html=True,
)

dados_agua = pd.DataFrame(
    {
        "Cenário": [
            "Consumo atual",
            "Após a redução",
        ],
        "Valor": [
            agua_total,
            agua_reduzida,
        ],
    }
)

dados_energia = pd.DataFrame(
    {
        "Cenário": [
            "Consumo atual",
            "Após a redução",
        ],
        "Valor": [
            energia_total,
            energia_reduzida,
        ],
    }
)

g1 = criar_grafico(
    dados_agua,
    "Litros por mês",
    ["#0d67a8", "#82c4ef"],
)

g2 = criar_grafico(
    dados_energia,
    "kWh por mês",
    ["#f08a0c", "#ffc474"],
)

cg1, cg2 = st.columns(2)

with cg1:
    st.subheader("Consumo de água")
    st.altair_chart(
        g1,
        use_container_width=True,
        theme=None,
    )

with cg2:
    st.subheader("Consumo de energia")
    st.altair_chart(
        g2,
        use_container_width=True,
        theme=None,
    )


# ANÁLISE
if percentual_reducao >= 20:
    classificacao = "Excelente"
    recomendacao = (
        "Mantenha o monitoramento e as ações de conscientização."
    )

elif percentual_reducao >= 10:
    classificacao = "Muito boa"
    recomendacao = (
        "Campanhas de conscientização e monitoramento "
        "podem ajudar a alcançar a meta."
    )

else:
    classificacao = "Inicial"
    recomendacao = (
        "A meta pode ser aumentada gradualmente."
    )


st.markdown(
    '<div class="section-title">Análise inteligente do EcoTwin</div>',
    unsafe_allow_html=True,
)

a1, a2 = st.columns(2)

with a1:
    st.success(
        f"### Classificação\n{classificacao}"
    )

with a2:
    st.info(
        f"### Recomendação\n{recomendacao}"
    )


# RESUMO
st.markdown(
    (
        '<div class="summary">'
        '<h3>Resumo anual</h3>'
        f'<p>Com redução de {percentual_reducao}%, '
        'a comunidade economizaria aproximadamente:</p>'
        f'<h2>R$ {formatar_numero(economia_financeira_anual, 2)} '
        'por ano</h2>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# RELATÓRIO
relatorio = f"""
ECOTWIN - RELATÓRIO DA SIMULAÇÃO

Número de residências:
{formatar_numero(residencias)}

Meta de redução:
{percentual_reducao}%

Água economizada por ano:
{formatar_numero(economia_agua_anual)} litros

Energia economizada por ano:
{formatar_numero(economia_energia_anual)} kWh

Economia financeira anual:
R$ {formatar_numero(economia_financeira_anual, 2)}

CO₂ evitado:
{formatar_numero(co2_toneladas, 2)} toneladas

Classificação:
{classificacao}

Recomendação:
{recomendacao}
"""

st.markdown(
    '<div class="section-title">Relatório</div>',
    unsafe_allow_html=True,
)

st.download_button(
    "Baixar relatório",
    data=relatorio,
    file_name="relatorio_ecotwin.txt",
    mime="text/plain",
    use_container_width=True,
)
