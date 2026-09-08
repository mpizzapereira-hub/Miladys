import streamlit as st
import pandas as pd
import altair as alt

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

# BARRA LATERAL
st.sidebar.markdown("# 🌿 EcoTwin")
st.sidebar.markdown("### EcoMonitoramento Urbano Inteligente")
st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Dados da simulação")

residencias = st.sidebar.number_input(
    "🏠 Número de residências",
    min_value=1,
    value=1000,
    step=100,
)
agua_por_casa = st.sidebar.number_input(
    "💧 Consumo mensal de água por residência (litros)",
    min_value=1.0,
    value=18000.0,
    step=500.0,
)
energia_por_casa = st.sidebar.number_input(
    "⚡ Consumo mensal de energia por residência (kWh)",
    min_value=1.0,
    value=200.0,
    step=10.0,
)
tarifa_kwh = st.sidebar.number_input(
    "💰 Tarifa de energia (R$/kWh)",
    min_value=0.01,
    value=0.75,
    step=0.05,
)
percentual_reducao = st.sidebar.slider(
    "🎯 Meta de redução (%)",
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
co2_toneladas = (economia_energia_anual * fator_co2) / 1000

# CABEÇALHO
st.markdown("# 🌿 EcoTwin")
st.markdown("### EcoMonitoramento Urbano Inteligente")
st.write("Simule o impacto da redução do consumo de água e energia e visualize benefícios econômicos e ambientais.")

# RESULTADOS
st.markdown("## 📊 Resultados da simulação")

c1, c2, c3 = st.columns(3)
c1.metric("💧 Água economizada por mês", f"{formatar_numero(economia_agua)} L")
c2.metric("⚡ Energia economizada por mês", f"{formatar_numero(economia_energia)} kWh")
c3.metric("💰 Economia financeira mensal", f"R$ {formatar_numero(economia_financeira, 2)}")

c4, c5, c6 = st.columns(3)
c4.metric("💧 Água economizada por ano", f"{formatar_numero(economia_agua_anual)} L")
c5.metric("⚡ Energia economizada por ano", f"{formatar_numero(economia_energia_anual)} kWh")
c6.metric("🌱 CO₂ evitado por ano (Crédito de Carbono)", f"{formatar_numero(co2_toneladas, 2)} toneladas")

# GRÁFICOS
st.markdown("## 📈 Comparação de consumo")

dados_agua = pd.DataFrame({
    "Cenário": ["Consumo atual", "Após a redução"],
    "Valor": [agua_total, agua_reduzida],
})
dados_energia = pd.DataFrame({
    "Cenário": ["Consumo atual", "Após a redução"],
    "Valor": [energia_total, energia_reduzida],
})

g1 = criar_grafico(dados_agua, "Litros por mês", ["#0d67a8", "#82c4ef"])
g2 = criar_grafico(dados_energia, "kWh por mês", ["#f08a0c", "#ffc474"])

cg1, cg2 = st.columns(2)
with cg1:
    st.subheader("💧 Consumo de água")
    st.altair_chart(g1, use_container_width=True)
with cg2:
    st.subheader("⚡ Consumo de energia")
    st.altair_chart(g2, use_container_width=True)

# ANÁLISE IA
if percentual_reducao >= 20:
    classificacao = "Excelente 🌳"
    recomendacao = "Mantenha o monitoramento e as ações de conscientização."
elif percentual_reducao >= 10:
    classificacao = "Muito boa 🌿"
    recomendacao = "Campanhas de conscientização e monitoramento podem ajudar a alcançar a meta."
else:
    classificacao = "Inicial 🌱"
    recomendacao = "A meta pode ser aumentada gradualmente."

st.markdown("## 🤖 Análise inteligente do EcoTwin")
a1, a2 = st.columns(2)
with a1:
    st.success(f"### 🏆 Classificação\n{classificacao}")
with a2:
    st.info(f"### 🎯 Recomendação\n{recomendacao}")

# RELATÓRIO
relatorio = f"""ECOTWIN - RELATÓRIO DA SIMULAÇÃO
Número de residências: {formatar_numero(residencias)}
Meta de redução: {percentual_reducao}%
Água economizada por ano: {formatar_numero(economia_agua_anual)} litros
Energia economizada por ano: {formatar_numero(economia_energia_anual)} kWh
Economia financeira anual: R$ {formatar_numero(economia_financeira_anual, 2)}
CO₂ evitado (Crédito de carbono): {formatar_numero(co2_toneladas, 2)} toneladas
Classificação: {classificacao}
Recomendação: {recomendacao}
"""

st.markdown("## 📄 Relatório")
st.download_button(
    "🌱 Baixar relatório",
    data=relatorio,
    file_name="relatorio_ecotwin.txt",
    mime="text/plain",
    use_container_width=True,
)