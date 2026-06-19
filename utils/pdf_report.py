from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(tipo_institucion, nombre_institucion, key_values, df_indicators, vertical_summary_text="", horizontal_summary_text="", custom_params=None):
    """
    Generates a professional PDF financial report using ReportLab with dynamic
    analysis conclusions and recommendations based on indicator values.
    """
    pdf_buffer = BytesIO()
    
    # Page setup: letter size, 40pt margins (printable width = 612 - 80 = 532)
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=letter, 
        leftMargin=40, 
        rightMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    elementos = []
    styles = getSampleStyleSheet()
    
    # Premium Color Palette
    primary_color = colors.HexColor('#1E3A8A')    # Deep Indigo
    secondary_color = colors.HexColor('#0D9488')  # Teal
    text_dark = colors.HexColor('#1F2937')        # Charcoal
    bg_light = colors.HexColor('#F3F4F6')         # Soft Gray
    border_color = colors.HexColor('#E5E7EB')
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle', 
        parent=styles['Heading1'], 
        fontSize=20, 
        leading=24, 
        textColor=primary_color, 
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub', 
        parent=styles['Heading3'], 
        fontSize=11, 
        leading=14, 
        textColor=secondary_color, 
        spaceAfter=15,
        fontName='Helvetica-Oblique'
    )
    
    h1_style = ParagraphStyle(
        'DocH1', 
        parent=styles['Heading2'], 
        fontSize=13, 
        leading=16, 
        textColor=primary_color, 
        spaceBefore=14, 
        spaceAfter=6,
        keepWithNext=True,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'DocBody', 
        parent=styles['Normal'], 
        fontSize=9.5, 
        leading=13.5, 
        textColor=text_dark, 
        spaceAfter=6
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=text_dark
    )
    
    # --- Header ---
    elementos.append(Paragraph("INFORME OFICIAL DE ANÁLISIS FINANCIERO", title_style))
    elementos.append(Paragraph(f"<b>Entidad:</b> {nombre_institucion} | <b>Modelo:</b> {tipo_institucion}", subtitle_style))
    elementos.append(Spacer(1, 8))
    
    # --- 1. Introducción ---
    elementos.append(Paragraph("1. Introducción y Metodología", h1_style))
    intro_p = (
        f"El presente informe proporciona un análisis exhaustivo de la situación patrimonial y operativa "
        f"de la entidad bajo el marco metodológico correspondiente a: <b>{tipo_institucion}</b>. "
        f"Los estados financieros consolidados han sido analizados aplicando técnicas de análisis vertical y horizontal, "
        f"y se han calculado las razones financieras clave para determinar los niveles de liquidez, actividad, "
        f"solvencia y rentabilidad de la institución."
    )
    elementos.append(Paragraph(intro_p, body_style))
    elementos.append(Spacer(1, 8))
    
    # --- 2. Tabla de Indicadores ---
    elementos.append(Paragraph("2. Ratios e Indicadores Financieros Consolidados", h1_style))
    
    cols = df_indicators.columns.tolist()
    index_vals = df_indicators.index.tolist()
    
    # Header row
    header_row = [Paragraph("<b>Indicador / Ratio</b>", table_header_style)]
    for col in cols:
        header_row.append(Paragraph(f"<b>{col}</b>", table_header_style))
    
    table_data = [header_row]
    
    # Rows
    for idx in index_vals:
        row = [Paragraph(f"<b>{idx}</b>", table_cell_style)]
        for col in cols:
            val = df_indicators.loc[idx, col]
            if isinstance(val, float):
                if any(x in str(idx).lower() or '%' in str(col).lower() for x in ['%', 'roa', 'roe', 'margen', 'crecimiento', 'endeudamiento']):
                    val_str = f"{val:.2f}%"
                elif any(x in str(idx).lower() for x in ['gpa', 'precio', 'ganancias', 'libro']):
                    val_str = f"${val:.2f}"
                else:
                    val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            row.append(Paragraph(val_str, table_cell_style))
        table_data.append(row)
        
    # Dynamic column widths to prevent overflow (total printable width = 532)
    num_cols = len(cols)
    col_widths = [130] # 130 pt for indicator name
    
    if 'Descripción' in cols:
        desc_idx = cols.index('Descripción')
        for i, col in enumerate(cols):
            if i == desc_idx:
                col_widths.append(182) # 182 pt for description
            else:
                # Distribute remaining width (532 - 130 - 182 = 220) among year columns
                col_widths.append(220 / (num_cols - 1))
    else:
        # Distribute remaining width (532 - 130 = 402) among columns
        for col in cols:
            col_widths.append(402 / num_cols)
            
    t_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ])
    
    # Alternating rows
    for r in range(1, len(table_data)):
        bg = bg_light if r % 2 == 1 else colors.white
        t_style.add('BACKGROUND', (0, r), (-1, r), bg)
        
    indicators_table = Table(table_data, colWidths=col_widths)
    indicators_table.setStyle(t_style)
    elementos.append(indicators_table)
    elementos.append(Spacer(1, 10))
    
    # --- 3. Análisis Estructural ---
    elementos.append(Paragraph("3. Conclusiones del Análisis Estructural", h1_style))
    
    # Vertical analysis summary
    elementos.append(Paragraph("<b>Análisis Vertical:</b>", body_style))
    if vertical_summary_text:
        elementos.append(Paragraph(vertical_summary_text, body_style))
    else:
        elementos.append(Paragraph(
            "El análisis de estructura vertical muestra la composición proporcional de las inversiones (Activos) "
            "frente a las fuentes de financiamiento. Esto permite identificar la dependencia de capital de terceros "
            "e inversiones a corto plazo.",
            body_style
        ))
        
    elementos.append(Spacer(1, 4))
    
    # Horizontal analysis summary
    elementos.append(Paragraph("<b>Análisis Horizontal:</b>", body_style))
    if horizontal_summary_text:
        elementos.append(Paragraph(horizontal_summary_text, body_style))
    else:
        elementos.append(Paragraph(
            "La comparación de variaciones absolutas y porcentuales indica el ritmo de crecimiento o contracción "
            "de las principales partidas del balance y estado de resultados, identificando desviaciones presupuestarias.",
            body_style
        ))
        
    elementos.append(Spacer(1, 10))
    
    # --- 4. Conclusiones y Recomendaciones Basadas en Datos ---
    conclusiones_automaticas = []
    recomendaciones_automaticas = []
    
    # Extract latest year values to generate custom commentary
    periods = sorted(list(key_values.keys()), key=lambda x: int(x))
    if periods:
        latest_period = periods[-1]
        vals = key_values[latest_period]
        
        act_corr = vals.get('activo_corriente', 0.0)
        pas_corr = vals.get('pasivo_corriente', 0.0)
        inv = vals.get('inventarios', 0.0)
        act_tot = vals.get('activo_total', 0.0)
        pas_tot = vals.get('pasivo_total', 0.0)
        pat_tot = vals.get('patrimonio_total', 0.0)
        ingresos = vals.get('ingresos', 0.0)
        utilidad = vals.get('utilidad_neta', 0.0)
        
        # Calculate key ratios for commentary
        razon_corr = act_corr / pas_corr if pas_corr else 0.0
        pct_deuda = (pas_tot / act_tot) * 100 if act_tot else 0.0
        roe = (utilidad / pat_tot) * 100 if pat_tot else 0.0
        roa = (utilidad / act_tot) * 100 if act_tot else 0.0
        
        # 1. Liquidity evaluation
        if razon_corr < 1.0:
            conclusiones_automaticas.append(
                f"• <b>Liquidez Crítica:</b> En el año {latest_period}, la razón corriente se situó en {razon_corr:.2f}, "
                f"lo que significa que la entidad cuenta con menos de $1 de activo corriente por cada $1 de pasivo corriente, "
                f"presentando un riesgo elevado de liquidez a corto plazo."
            )
            recomendaciones_automaticas.append(
                "• <b>Optimización de Liquidez:</b> Se recomienda renegociar deudas a corto plazo para trasladarlas al largo plazo, "
                "mejorar el ciclo de conversión de efectivo o realizar inyecciones de capital de trabajo."
            )
        elif razon_corr < 1.5:
            conclusiones_automaticas.append(
                f"• <b>Liquidez Moderada:</b> La razón corriente se situó en {razon_corr:.2f} en el año {latest_period}, "
                f"lo que refleja un margen de cobertura ajustado para cubrir obligaciones inmediatas."
            )
            recomendaciones_automaticas.append(
                "• <b>Gestión de Tesorería:</b> Se aconseja acelerar la rotación de cuentas por cobrar y optimizar la rotación de inventarios "
                "para robustecer la posición de efectivo."
            )
        else:
            conclusiones_automaticas.append(
                f"• <b>Liquidez Solvente:</b> La razón corriente fue de {razon_corr:.2f} en el periodo {latest_period}, "
                f"mostrando una sólida cobertura de activos líquidos frente a los compromisos corrientes."
            )
            recomendaciones_automaticas.append(
                "• <b>Excedentes de Caja:</b> Se sugiere evaluar inversiones en instrumentos financieros de renta fija a corto plazo "
                "para rentabilizar los excesos de efectivo sin arriesgar la liquidez de operación."
            )
            
        # 2. Leverage evaluation
        if pct_deuda > 65.0:
            conclusiones_automaticas.append(
                f"• <b>Apalancamiento Elevado:</b> El nivel de endeudamiento alcanzó el {pct_deuda:.1f}% al cierre del periodo. "
                f"Los acreedores financian la mayor parte de la estructura productiva, lo que incrementa el riesgo financiero global."
            )
            recomendaciones_automaticas.append(
                "• <b>Desapalancamiento:</b> Se aconseja frenar la contratación de nuevos créditos financieros y priorizar la "
                "reinversión de utilidades o aportaciones directas de los socios."
            )
        elif pct_deuda > 40.0:
            conclusiones_automaticas.append(
                f"• <b>Estructura de Capital Equilibrada:</b> El índice de endeudamiento es del {pct_deuda:.1f}%, "
                f"reflejando una adecuada distribución entre fuentes de financiamiento externas e internas."
            )
            recomendaciones_automaticas.append(
                "• <b>Monitoreo de Deuda:</b> Mantener el monitoreo de las tasas de interés pactadas en pasivos bancarios "
                "para evitar encarecimientos en el costo promedio ponderado de capital."
            )
        else:
            conclusiones_automaticas.append(
                f"• <b>Bajo Nivel de Deuda:</b> El endeudamiento es conservador, situándose en {pct_deuda:.1f}%. "
                f"La entidad cuenta con una amplia capacidad crediticia no utilizada."
            )
            recomendaciones_automaticas.append(
                "• <b>Apalancamiento Productivo:</b> Evaluar la factibilidad de tomar deuda controlada para proyectos de inversión de alto retorno, "
                "potenciando así la rentabilidad de los accionistas."
            )
            
        # 3. Profitability evaluation
        if roe > 12.0:
            conclusiones_automaticas.append(
                f"• <b>Rentabilidad Destacada:</b> La rentabilidad sobre el patrimonio (ROE) fue del {roe:.1f}%, y la rentabilidad sobre activos (ROA) "
                f"de {roa:.1f}% en el año {latest_period}, mostrando una gestión eficiente en la generación de utilidades."
            )
            recomendaciones_automaticas.append(
                "• <b>Sostenibilidad:</b> Se sugiere continuar con la política de eficiencia en costos operativos para defender los márgenes "
                "y sostener la alta rentabilidad frente a la competencia."
            )
        elif roe > 5.0:
            conclusiones_automaticas.append(
                f"• <b>Rentabilidad Moderada:</b> La rentabilidad patrimonial se sitúa en {roe:.1f}%, indicando retornos aceptables "
                f"pero susceptibles de mejora operativa."
            )
            recomendaciones_automaticas.append(
                "• <b>Eficiencia en Gastos:</b> Analizar el margen de utilidad operativa para identificar fugas en los gastos de administración "
                "y ventas, buscando mejorar el margen neto."
            )
        else:
            conclusiones_automaticas.append(
                f"• <b>Baja Rentabilidad:</b> El ROE se situó en {roe:.1f}%, un retorno inferior a las tasas de interés de mercado libre de riesgo, "
                f"lo cual puede desalentar la inversión de los accionistas."
            )
            recomendaciones_automaticas.append(
                "• <b>Reingeniería Operativa:</b> Se hace imperativa una reestructuración de costos y gastos, y una revisión en la estrategia de precios "
                "para restablecer los niveles saludables de rentabilidad."
            )
            
    # Draw Dictamen & recommendations block
    dictamen_elements = [
        Paragraph("4. Dictamen Financiero y Recomendaciones del Analista", h1_style),
        Paragraph("<b>Conclusiones Clave:</b>", body_style),
    ]
    
    for concl in conclusiones_automaticas:
        dictamen_elements.append(Paragraph(concl, body_style))
        
    dictamen_elements.append(Spacer(1, 4))
    dictamen_elements.append(Paragraph("<b>Recomendaciones de Gestión:</b>", body_style))
    
    for rec in recomendaciones_automaticas:
        dictamen_elements.append(Paragraph(rec, body_style))
        
    dictamen_elements.append(Spacer(1, 25))
    
    # Signatures
    dictamen_elements.append(Table([
        [Paragraph("____________________________<br/><b>Analista Financiero Principal</b>", body_style),
         Paragraph("____________________________<br/><b>Aprobado y Dictaminado Por</b>", body_style)]
    ], colWidths=[250, 250]))
    
    elementos.append(KeepTogether(dictamen_elements))
    
    # Build PDF
    doc.build(elementos)
    
    pdf_buffer.seek(0)
    return pdf_buffer
