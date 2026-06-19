import pandas as pd

def get_perlas_structure():
    """
    Returns the PERLAS methodology structure for savings and credit cooperatives.
    """
    perlas_data = {
        'Componente': [
            'P - Protección (Protection)',
            'E - Estructura Financiera (Financial Structure)',
            'R - Rendimiento y Tarifas (Rates of Return & Costs)',
            'L - Liquidez (Liquidity)',
            'A - Calidad de Activos (Asset Quality)',
            'S - Señales de Crecimiento (Signs of Growth)'
        ],
        'Descripción': [
            'Evalúa la suficiencia de las provisiones para proteger los ahorros de los socios ante pérdidas de cartera.',
            'Analiza la composición de activos, pasivos y patrimonio buscando maximizar activos productivos.',
            'Mide los rendimientos generados por las inversiones y préstamos frente al costo del fondeo.',
            'Garantiza que la cooperativa mantenga suficiente liquidez para atender retiros y solicitudes de crédito.',
            'Evalúa el impacto de los activos no productivos (como la morosidad y bienes adjudicados).',
            'Mide la tasa de crecimiento anual de los activos, depósitos, patrimonio y membresía.'
        ],
        'Fórmulas y Ratios Estándar': [
            'Provisión Cartera Morosa (>12 meses) / Cartera Improductiva total - [Estándar: 100%]',
            'Préstamos Netos / Activo Total | Depósitos de Ahorro / Activo Total | Aportaciones / Activo Total',
            'Ingresos Financieros por Préstamos / Cartera Promedio | Costos de Ahorros / Depósitos de Ahorro',
            'Fondos Disponibles sin Restricción / Depósitos de Ahorros - [Estándar: 15% - 20%]',
            'Cartera en Mora / Cartera de Préstamos Total | Activos No Productivos / Activo Total',
            'Porcentaje de crecimiento en Activo Total, Depósitos de Ahorros y Capital Institucional'
        ],
        'Meta WOCCU (%)': [
            '100.0%',
            'Préstamos: 70-80% | Ahorros: 70-80% | Capital: >10%',
            'Rendimiento de mercado suficiente para pagar tasas de ahorro competitivas',
            '15.0% - 20.0%',
            '< 5.0% de morosidad',
            'Crecimiento superior a la inflación nacional'
        ]
    }
    return pd.DataFrame(perlas_data)

def calculate_perlas_placeholders(key_values):
    """
    Generates dummy/calculated parameters for PERLAS based on uploaded data where possible,
    acting as a prepared calculation structure.
    """
    periods = list(key_values.keys())
    perlas_ratios = {}
    
    # Sort periods chronologically
    sorted_periods = sorted(periods, key=lambda x: str(x))
    
    for i, year in enumerate(sorted_periods):
        vals = key_values[year]
        act_tot = vals.get('activo_total', 1.0)
        pat_tot = vals.get('patrimonio_total', 1.0)
        ingresos = vals.get('ingresos', 1.0)
        
        # Calculate asset growth if previous year exists
        crecimiento_activo = 0.0
        if i > 0:
            prev_year = sorted_periods[i - 1]
            prev_act = key_values[prev_year].get('activo_total', 0.0)
            if prev_act and prev_act != 0.0:
                crecimiento_activo = ((act_tot - prev_act) / prev_act) * 100
                
        # Mock savings and loans based on common structures if not found
        perlas_ratios[year] = {
            'P1 - Cobertura de Provisiones (Provisiones / Mora >12m)': 100.0, # Meta
            'E1 - Préstamos Netos / Activo Total (%)': 75.0,                 # Estructura típica
            'E5 - Depósitos de Ahorro / Activo Total (%)': 70.0,             # Estructura típica
            'R1 - Rendimiento de la Cartera de Préstamos (%)': 12.5,          # Rendimiento típico
            'L1 - Fondos Líquidos / Depósitos de Ahorro (%)': 18.2,           # Liquidez típica
            'A1 - Morosidad de Cartera (Mora / Cartera Total %)': 4.2,        # Calidad de activos típica
            'S1 - Crecimiento del Activo Total (% Cal.)': crecimiento_activo
        }
        
    df = pd.DataFrame(perlas_ratios)
    if not df.empty:
        descriptions = [
            "Proporción de reservas para pérdidas que cubren créditos con mora superior a 12 meses.",
            "Porcentaje del activo invertido directamente en préstamos productivos a socios.",
            "Porcentaje de los activos financiados mediante depósitos de ahorro de socios.",
            "Ingreso por intereses de préstamos anualizado respecto al saldo promedio de cartera.",
            "Fondos de reserva en efectivo disponibles para cubrir retiros repentinos de depósitos.",
            "Porcentaje de cartera de préstamos que se encuentra vencida o refinanciada.",
            "Tasa de crecimiento anual del activo total, calculada a partir de los balances provistos."
        ]
        df.insert(0, 'Descripción', descriptions)
    return df
