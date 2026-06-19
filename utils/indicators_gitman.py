import pandas as pd

def calculate_gitman_indicators(key_values, params=None):
    """
    Calculates Gitman financial indicators for each year based on Lawrence J. Gitman's formulas.
    Args:
        key_values (dict): Parsed financial key values by period.
        params (dict): Optional external parameters (market price, shares outstanding, etc.)
    Returns:
        dict: Dict of indicators by year.
        pd.DataFrame: DataFrame containing indicators for all years.
    """
    if params is None:
        params = {}
        
    ratios = {}
    
    # Extra parameters with default values
    precio_accion = params.get('precio_accion', 15.0)
    num_acciones = params.get('num_acciones', 50000.0)
    tasa_impuestos = params.get('tasa_impuestos', 0.25)
    pagos_principal = params.get('pagos_principal', 5000.0)
    dividendos_preferentes = params.get('dividendos_preferentes', 0.0)
    compras_anuales = params.get('compras_anuales', 0.0)  # 0 indicates to use Cost of Sales as proxy
    
    for year, vals in key_values.items():
        act_corr = vals.get('activo_corriente', 0.0)
        pas_corr = vals.get('pasivo_corriente', 0.0)
        inv = vals.get('inventarios', 0.0)
        cxc = vals.get('cuentas_por_cobrar', 0.0)
        cxp = vals.get('cuentas_por_pagar', 0.0)
        act_tot = vals.get('activo_total', 0.0)
        pas_tot = vals.get('pasivo_total', 0.0)
        pat_tot = vals.get('patrimonio_total', 0.0)
        ingresos = vals.get('ingresos', 0.0)
        costos = vals.get('costos', 0.0)
        gastos = vals.get('gastos', 0.0)
        ebit = vals.get('utilidad_operativa', 0.0)
        intereses = vals.get('gastos_interes', 0.0)
        arrendamientos = vals.get('pagos_arrendamiento', 0.0)
        utilidad = vals.get('utilidad_neta', 0.0)
        ut_bruta = vals.get('utilidad_bruta', 0.0)
        
        # 1. INDICADORES DE LIQUIDEZ
        razon_corriente = act_corr / pas_corr if pas_corr and pas_corr != 0.0 else 0.0
        prueba_acida = (act_corr - inv) / pas_corr if pas_corr and pas_corr != 0.0 else 0.0
        
        # 2. INDICADORES DE ACTIVIDAD
        rot_inventario = costos / inv if inv and inv != 0.0 else 0.0
        periodo_cobro = (cxc * 365) / ingresos if ingresos and ingresos != 0.0 else 0.0
        
        compras_period = compras_anuales if compras_anuales > 0 else (costos * 0.7)  # Heurística: 70% de costo de ventas son compras
        periodo_pago = (cxp * 365) / compras_period if compras_period and compras_period != 0.0 else 0.0
        rot_activos = ingresos / act_tot if act_tot and act_tot != 0.0 else 0.0
        
        # 3. INDICADORES DE ENDEUDAMIENTO
        razon_deuda = (pas_tot / act_tot) * 100 if act_tot and act_tot != 0.0 else 0.0
        cargos_interes_fijo = ebit / intereses if intereses and intereses != 0.0 else 0.0
        
        # Cobertura de pagos fijos
        numerador_cobertura = ebit + arrendamientos
        denominador_cobertura = intereses + arrendamientos + ((pagos_principal + dividendos_preferentes) * (1 / (1 - tasa_impuestos)))
        cobertura_pagos_fijos = numerador_cobertura / denominador_cobertura if denominador_cobertura and denominador_cobertura != 0.0 else 0.0
        
        # 4. INDICADORES DE RENTABILIDAD
        margen_bruto = (ut_bruta / ingresos) * 100 if ingresos and ingresos != 0.0 else 0.0
        margen_operativo = (ebit / ingresos) * 100 if ingresos and ingresos != 0.0 else 0.0
        margen_neto = (utilidad / ingresos) * 100 if ingresos and ingresos != 0.0 else 0.0
        
        gpa = utilidad / num_acciones if num_acciones and num_acciones != 0.0 else 0.0
        roa = (utilidad / act_tot) * 100 if act_tot and act_tot != 0.0 else 0.0
        roe = (utilidad / pat_tot) * 100 if pat_tot and pat_tot != 0.0 else 0.0
        
        # 5. INDICADORES DE MERCADO
        per = precio_accion / gpa if gpa and gpa != 0.0 else 0.0
        valor_libros = pat_tot / num_acciones if num_acciones and num_acciones != 0.0 else 0.0
        mercado_libro = precio_accion / valor_libros if valor_libros and valor_libros != 0.0 else 0.0
        
        ratios[year] = {
            'Razón Circulante (Veces)': razon_corriente,
            'Prueba del Ácido (Veces)': prueba_acida,
            'Rotación de Inventarios (Veces)': rot_inventario,
            'Periodo Promedio de Cobro (Días)': periodo_cobro,
            'Periodo Promedio de Pago (Días)': periodo_pago,
            'Rotación de Activos Totales (Veces)': rot_activos,
            'Índice de Endeudamiento (%)': razon_deuda,
            'Cargos de Interés Fijo (Veces)': cargos_interes_fijo,
            'Índice de Cobertura de Pagos Fijos (Veces)': cobertura_pagos_fijos,
            'Margen de Utilidad Bruta (%)': margen_bruto,
            'Margen de Utilidad Operativa (%)': margen_operativo,
            'Margen de Utilidad Neta (%)': margen_neto,
            'Ganancias por Acción (GPA)': gpa,
            'Rendimiento sobre Activos (ROA %)': roa,
            'Rendimiento sobre Capital (ROE %)': roe,
            'Relación Precio/Ganancias (PER)': per,
            'Relación Mercado/Libro (M/L)': mercado_libro
        }
        
    # Convert to DataFrame
    if ratios:
        df_ratios = pd.DataFrame(ratios)
        descriptions = [
            "Mide la capacidad de pagar deudas a corto plazo (Activo Corriente / Pasivo Corriente).",
            "Mide liquidez inmediata sin considerar inventarios ((Activo Corriente - Inventarios) / Pasivo Corriente).",
            "Mide la velocidad con la que se vende el inventario (Costo de Ventas / Inventario).",
            "Días promedio que toma cobrar las ventas a crédito ((Cuentas por Cobrar * 365) / Ventas).",
            "Días promedio que toma pagar a proveedores ((Cuentas por Pagar * 365) / Compras o Costos).",
            "Eficiencia en el uso de los activos para generar ingresos (Ventas / Activo Total).",
            "Proporción de activos totales financiados por acreedores ((Pasivo Total / Activo Total) * 100).",
            "Mide la capacidad de realizar pagos de intereses contractuales (EBIT / Gastos de Interés).",
            "Capacidad de cumplir pagos fijos de arrendamiento, intereses y principal bajo impuestos.",
            "Porcentaje de ganancia que queda después de restar costos de ventas ((Utilidad Bruta / Ventas) * 100).",
            "Porcentaje de ganancia antes de intereses e impuestos ((Utilidad Operativa / Ventas) * 100).",
            "Porcentaje final de utilidad sobre ventas ((Utilidad Neta / Ventas) * 100).",
            "Monto de ganancia obtenido por cada acción común en circulación (Utilidad Neta / Acciones).",
            "Rendimiento general generado por los activos de la empresa ((Utilidad Neta / Activo Total) * 100).",
            "Retorno obtenido sobre la inversión de los accionistas comunes ((Utilidad Neta / Patrimonio) * 100).",
            "Monto que los inversionistas pagan por cada dólar de ganancia (Precio Acción / GPA).",
            "Relación del valor de mercado respecto a su valor contable en libros (Precio Acción / Valor Libros)."
        ]
        df_ratios.insert(0, 'Descripción', descriptions)
    else:
        df_ratios = pd.DataFrame()
        
    return ratios, df_ratios
