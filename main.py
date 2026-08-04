# Dados do Bairro Eco-Ville
casas = 1000
agua_por_casa = 18000  # em litros
energia_por_casa = 200  # em kWh
tarifa_kwh = 0.75

# Consumo Total
consumo_total_agua = casas * agua_por_casa
consumo_total_energia = casas * energia_por_casa

# Impacto dos 10%
economia_agua = consumo_total_agua * 0.10
economia_energia = consumo_total_energia * 0.10
economia_financeira = economia_energia * tarifa_kwh

print("=== ECOMONITOR URBANO - SIMULAÇÃO ECO-VILLE ===")
print(f"Água economizada por mês: {economia_agua:,.0f} Litros")
print(f"Energia economizada por mês: {economia_energia:,.0f} kWh")
print(f"Economia financeira mensal: R$ {economia_financeira:,.2f}")
# EcoMonitor Urbano - Simulação de Consumo
# Projeto Eco-Ville

# Dados Iniciais do Bairro
total_residencias = 1000
agua_por_casa = 18000     # em litros/mês
energia_por_casa = 200    # em kWh/mês
tarifa_kwh = 0.75         # valor médio em R$

# Consumo Total
consumo_agua_total = total_residencias * agua_por_casa
consumo_energia_total = total_residencias * energia_por_casa

# Impacto dos 10% de Redução
economia_agua_mensal = consumo_agua_total * 0.10
economia_energia_mensal = consumo_energia_total * 0.10
economia_financeira_mensal = economia_energia_mensal * tarifa_kwh
economia_financeira_anual = economia_financeira_mensal * 12

# Exibição dos Resultados no Terminal
print("=" * 50)
print("     ECOMONITOR URBANO - SIMULAÇÃO ECO-VILLE     ")
print("=" * 50)
print(f"Bairro: 1.000 residências simuladas\n")

print("--- CONSUMO ATUAL DA COMUNIDADE ---")
print(f"Água Total:    {consumo_agua_total:,.0f} L/mês")
print(f"Energia Total: {consumo_energia_total:,.0f} kWh/mês\n")

print("--- RESULTADOS COM O IMPACTO DOS 10% ---")
print(f"💧 Água Economizada/mês:    {economia_agua_mensal:,.0f} Litros")
print(f"⚡ Energia Economizada/mês: {economia_energia_mensal:,.0f} kWh")
print(f"💰 Economia Financeira/mês: R$ {economia_financeira_mensal:,.2f}")
print(f"📈 Economia Financeira/ano: R$ {economia_financeira_anual:,.2f}")
print("=" * 50)
git add .
git commit -m "Implementa simulacao dos 10% do EcoMonitor Urbano"
git push
