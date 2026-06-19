import pandas as pd

def get_camel_structure():
    """
    Returns the CAMEL methodology structure for banking institutions.
    """
    camel_data = {
        'Componente': [
            'C - Suficiencia de Capital (Capital Adequacy)',
            'A - Calidad de Activos (Asset Quality)',
            'M - Gestión Administrativa (Management)',
            'E - Rentabilidad (Earnings)',
            'L - Liquidez (Liquidity)'
        ],
        'Descripción': [
            'Mide la solidez patrimonial de la institución financiera para absorber pérdidas inesperadas.',
            'Evalúa la calidad del portafolio de créditos (cartera) y el riesgo de crédito de los activos.',
            'Analiza la eficiencia operativa, controles internos y capacidad directiva.',
            'Evalúa la capacidad de generar ganancias sostenibles y eficientes en el tiempo.',
            'Mide la capacidad para hacer frente a retiros de depósitos y obligaciones de corto plazo.'
        ],
        'Fórmulas y Ratios Estándar': [
            'Patrimonio Técnico / Activos Ponderados por Riesgo (APR) - [Mínimo regulatorio: 9%]',
            'Cartera Improductiva / Cartera Total (Índice de Morosidad) | Provisiones / Cartera Improductiva',
            'Gastos de Operación / Activo Total Promedio | Gastos de Personal / Margen Financiero Neto',
            'ROA Financiero (Utilidad / Activo Promedio) | ROE Financiero (Utilidad / Patrimonio Promedio)',
            'Fondos Disponibles / Depósitos a la Vista | Activos Líquidos / Obligaciones a Corto Plazo'
        ],
        'Valor Referencial (%)': [
            '> 12.0% (Excelente)',
            '< 3.0% (Bajo riesgo)',
            '< 4.0% (Eficiente)',
            '> 1.5% (Sostenible)',
            '> 20.0% (Seguridad)'
        ]
    }
    return pd.DataFrame(camel_data)

def calculate_camel_placeholders(key_values):
    """
    Generates dummy/calculated parameters for CAMEL based on uploaded data where possible,
    acting as a prepared calculation structure.
    """
    periods = list(key_values.keys())
    camel_ratios = {}
    
    for year in periods:
        vals = key_values[year]
        act_tot = vals.get('activo_total', 1.0)
        pat_tot = vals.get('patrimonio_total', 1.0)
        utilidad = vals.get('utilidad_neta', 0.0)
        ingresos = vals.get('ingresos', 1.0)
        
        # Calculate ROA/ROE and approximate others for demonstration
        roa = (utilidad / act_tot) * 100 if act_tot else 0.0
        roe = (utilidad / pat_tot) * 100 if pat_tot else 0.0
        
        # We can mock banking-specific ones using typical proportions or leaving placeholders
        camel_ratios[year] = {
            'Suficiencia de Capital (Patrimonio Técnico / APR)': 14.5,  # Valor de referencia
            'Morosidad de la Cartera (Cartera Vencida / Total)': 2.8,   # Valor de referencia
            'Eficiencia Operativa (Gastos Adm. / Activos)': 3.5,        # Valor de referencia
            'Rentabilidad sobre Activos (ROA % Cal.)': roa,
            'Rentabilidad sobre Patrimonio (ROE % Cal.)': roe,
            'Ratio de Liquidez (Disponibilidades / Depósitos)': 24.2     # Valor de referencia
        }
        
    df = pd.DataFrame(camel_ratios)
    if not df.empty:
        descriptions = [
            "Mide el respaldo de capital para riesgos de crédito, mercado y operación.",
            "Proporción de créditos vencidos o en mora sobre la cartera total de la institución.",
            "Costo administrativo para operar la entidad respecto de sus activos totales.",
            "Rentabilidad sobre activos calculada a partir de los estados financieros cargados.",
            "Rentabilidad sobre el patrimonio calculada a partir de los estados financieros cargados.",
            "Proporción de activos líquidos disponibles para atender retiros del público."
        ]
        df.insert(0, 'Descripción', descriptions)
    return df
