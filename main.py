# EcoTwin - EcoMonitor Urbano
# Simulação de economia de água e energia

def ler_numero(mensagem, valor_padrao):
    """
    Solicita um número ao usuário.
    Caso ele deixe em branco, utiliza o valor padrão.
    """
    while True:
        entrada = input(f"{mensagem} [padrão: {valor_padrao}]: ").strip()

        if entrada == "":
            return float(valor_padrao)

        # Permite digitar valores com vírgula ou ponto
        entrada = entrada.replace(",", ".")

        try:
            valor = float(entrada)

            if valor <= 0:
                print("Digite um valor maior que zero.")
                continue

            return valor

        except ValueError:
            print("Valor inválido. Digite apenas números.")


def calcular_resultados(
    residencias,
    agua_por_casa,
    energia_por_casa,
    tarifa_kwh,
    percentual_reducao
):
    consumo_agua_total = residencias * agua_por_casa
    consumo_energia_total = residencias * energia_por_casa

    reducao_decimal = percentual_reducao / 100

    economia_agua_mensal = consumo_agua_total * reducao_decimal
    economia_energia_mensal = consumo_energia_total * reducao_decimal
    economia_financeira_mensal = economia_energia_mensal * tarifa_kwh

    consumo_agua_sustentavel = consumo_agua_total - economia_agua_mensal
    consumo_energia_sustentavel = (
        consumo_energia_total - economia_energia_mensal
    )

    economia_agua_anual = economia_agua_mensal * 12
    economia_energia_anual = economia_energia_mensal * 12
    economia_financeira_anual = economia_financeira_mensal * 12

    return {
        "consumo_agua_total": consumo_agua_total,
        "consumo_energia_total": consumo_energia_total,
        "economia_agua_mensal": economia_agua_mensal,
        "economia_energia_mensal": economia_energia_mensal,
        "economia_financeira_mensal": economia_financeira_mensal,
        "consumo_agua_sustentavel": consumo_agua_sustentavel,
        "consumo_energia_sustentavel": consumo_energia_sustentavel,
        "economia_agua_anual": economia_agua_anual,
        "economia_energia_anual": economia_energia_anual,
        "economia_financeira_anual": economia_financeira_anual
    }


def mostrar_resultados(residencias, percentual_reducao, resultados):
    print("\n" + "=" * 62)
    print("             ECOTWIN - ECOMONITOR URBANO")
    print("=" * 62)

    print(f"Residências simuladas: {residencias:,.0f}")
    print(f"Meta de redução: {percentual_reducao:.1f}%")

    print("\n--- CONSUMO ATUAL DA COMUNIDADE ---")
    print(
        f"Água:    "
        f"{resultados['consumo_agua_total']:,.0f} litros por mês"
    )
    print(
        f"Energia: "
        f"{resultados['consumo_energia_total']:,.0f} kWh por mês"
    )

    print("\n--- CONSUMO APÓS A REDUÇÃO ---")
    print(
        f"Água:    "
        f"{resultados['consumo_agua_sustentavel']:,.0f} litros por mês"
    )
    print(
        f"Energia: "
        f"{resultados['consumo_energia_sustentavel']:,.0f} kWh por mês"
    )

    print("\n--- ECONOMIA MENSAL ---")
    print(
        f"Água economizada:    "
        f"{resultados['economia_agua_mensal']:,.0f} litros"
    )
    print(
        f"Energia economizada: "
        f"{resultados['economia_energia_mensal']:,.0f} kWh"
    )
    print(
        f"Economia financeira: "
        f"R$ {resultados['economia_financeira_mensal']:,.2f}"
    )

    print("\n--- ECONOMIA ANUAL ---")
    print(
        f"Água economizada:    "
        f"{resultados['economia_agua_anual']:,.0f} litros"
    )
    print(
        f"Energia economizada: "
        f"{resultados['economia_energia_anual']:,.0f} kWh"
    )
    print(
        f"Economia financeira: "
        f"R$ {resultados['economia_financeira_anual']:,.2f}"
    )

    print("=" * 62)


def main():
    print("=" * 62)
    print("         BEM-VINDO AO SIMULADOR ECOTWIN")
    print("=" * 62)
    print("Pressione Enter para utilizar os valores padrão.\n")

    residencias = ler_numero(
        "Número de residências",
        1000
    )

    agua_por_casa = ler_numero(
        "Consumo mensal de água por residência, em litros",
        18000
    )

    energia_por_casa = ler_numero(
        "Consumo mensal de energia por residência, em kWh",
        200
    )

    tarifa_kwh = ler_numero(
        "Tarifa de energia, em reais por kWh",
        0.75
    )

    percentual_reducao = ler_numero(
        "Porcentagem de redução desejada",
        10
    )

    if percentual_reducao > 100:
        print("\nA porcentagem não pode ser maior que 100%.")
        return

    resultados = calcular_resultados(
        residencias,
        agua_por_casa,
        energia_por_casa,
        tarifa_kwh,
        percentual_reducao
    )

    mostrar_resultados(
        residencias,
        percentual_reducao,
        resultados
    )


if __name__ == "__main__":
    main()