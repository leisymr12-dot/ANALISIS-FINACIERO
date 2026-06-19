import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
import importlib

# Import and force reload custom modules to clear python cache
import utils.excel_parser
import utils.vertical_analysis
import utils.horizontal_analysis
import utils.indicators_gitman
import utils.indicators_camel
import utils.indicators_perlas
import utils.charts
import utils.pdf_report

importlib.reload(utils.excel_parser)
importlib.reload(utils.vertical_analysis)
importlib.reload(utils.horizontal_analysis)
importlib.reload(utils.indicators_gitman)
importlib.reload(utils.indicators_camel)
importlib.reload(utils.indicators_perlas)
importlib.reload(utils.charts)
importlib.reload(utils.pdf_report)

from utils.excel_parser import parse_financial_excel
from utils.vertical_analysis import calculate_vertical_analysis
from utils.horizontal_analysis import calculate_horizontal_analysis
from utils.indicators_gitman import calculate_gitman_indicators
from utils.indicators_camel import get_camel_structure, calculate_camel_placeholders
from utils.indicators_perlas import get_perlas_structure, calculate_perlas_placeholders
from utils.charts import plot_balance_composition, plot_income_composition, plot_key_accounts_evolution
from utils.pdf_report import generate_pdf_report

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Plataforma de Análisis Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS for UI styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main Header container */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0D9488 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .main-header p {
        color: #E2E8F0 !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
        font-weight: 300;
    }
    
    /* Styled metric cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        text-align: center;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.8rem;
        color: #6B7280;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #1E3A8A;
        font-weight: 700;
    }
    .metric-desc {
        font-size: 0.72rem;
        color: #9CA3AF;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Render main header banner
st.markdown("""
<div class="main-header">
    <h1>📈 Plataforma Inteligente de Análisis Financiero</h1>
    <p>Carga estados financieros en Excel ordenados por pestañas anuales para análisis vertical, horizontal e indicadores financieros avanzados.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.markdown("### ⚙️ Configuración General")

tipo_institucion = st.sidebar.selectbox(
    "1. Tipo de Institución:",
    ["Empresa Comercial (Gitman)", "Institución Bancaria (CAMEL)", "Cooperativa de Ahorro (PERLAS)"]
)

nombre_institucion = st.sidebar.text_input(
    "Nombre de la Institución:",
    value="Nombre de la Institución",
    help="Ingrese el nombre comercial de la empresa, banco o cooperativa."
)

uploaded_file = st.sidebar.file_uploader(
    "2. Subir Excel Financiero:",
    type=["xlsx"],
    help="Suba un libro donde cada pestaña tenga el nombre de un año (ej. 2021, 2022)."
)

# Render sample/structure format guide
with st.sidebar.expander("ℹ️ Guía de Estructura Excel"):
    st.markdown("""
    **Formato requerido:**
    - **Pestañas**: Cada una nombrada con el número del año (ej. `2022`, `2023`).
    - **Contenido**: Cada pestaña debe incluir el **Balance General** y **Estado de Resultados** unidos en una sola hoja.
    - **Columnas**:
      - `codigo`: Códigos contables (ej. 1, 1.1, 2, 3, 4, 5).
      - `cuenta`: Nombre de la cuenta (ej. Caja, Ventas).
      - `saldo` / `monto` / `valor`: Saldo final del periodo.
    """)

# Sidebar settings for GITMAN indicators
gitman_params = {}
if "Gitman" in tipo_institucion and uploaded_file is not None:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Parámetros de Mercado (Gitman)")
    
    gitman_params['precio_accion'] = st.sidebar.number_input(
        "Precio de la Acción (USD):",
        min_value=0.01,
        value=15.0,
        step=1.0,
        help="Precio de mercado por acción común."
    )
    
    gitman_params['num_acciones'] = st.sidebar.number_input(
        "Acciones en Circulación:",
        min_value=1,
        value=50000,
        step=5000,
        help="Número total de acciones ordinarias emitidas."
    )
    
    gitman_params['tasa_impuestos'] = st.sidebar.slider(
        "Tasa de Impuestos (%):",
        min_value=0.0,
        max_value=100.0,
        value=25.0,
        step=1.0,
        help="Tasa impositiva para calcular la cobertura de pagos fijos."
    ) / 100.0
    
    gitman_params['pagos_principal'] = st.sidebar.number_input(
        "Pagos de Principal ($):",
        min_value=0.0,
        value=5000.0,
        step=1000.0,
        help="Monto anual pagado por amortización de capital de deuda."
    )
    
    gitman_params['dividendos_preferentes'] = st.sidebar.number_input(
        "Dividendos Preferentes ($):",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Dividendos comprometidos a accionistas preferentes."
    )
    
    gitman_params['compras_anuales'] = st.sidebar.number_input(
        "Compras de Inventario ($):",
        min_value=0.0,
        value=0.0,
        step=5000.0,
        help="Compras anuales a crédito. Si es 0, se estimará a partir del Costo de Ventas."
    )

# ==========================================
# CORE APPLICATION LOGIC
# ==========================================
if uploaded_file is not None:
    try:
        is_fin = "Empresa" not in tipo_institucion
        
        # Parse Excel data
        with st.spinner("Leyendo pestañas de años y procesando cuentas..."):
            parsed_data = parse_financial_excel(uploaded_file, is_financial_institution=is_fin)
            
        df_bg = parsed_data['df_bg']
        df_er = parsed_data['df_er']
        periods = parsed_data['periods']
        key_values = parsed_data['key_values']
        
        if not periods:
            st.error("❌ No se detectaron pestañas con nombres de años numéricos (ej. 2021, 2022).")
            st.stop()
            
        st.sidebar.success(f"✅ Cargado. Periodos: {', '.join(map(str, periods))}")
        
        # Select analysis years
        selected_av_year = st.sidebar.selectbox("Año para Análisis Vertical:", periods, index=len(periods)-1)
        
        # Horizontal analysis selection
        if len(periods) >= 2:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📊 Análisis Horizontal")
            period_a = st.sidebar.selectbox("Año Base (A):", periods, index=0)
            period_b = st.sidebar.selectbox("Año Comparación (B):", periods, index=len(periods)-1)
        else:
            period_a, period_b = None, None
            st.sidebar.warning("⚠️ Se requieren mínimo 2 años para Análisis Horizontal.")
            
        # --- TAB NAVIGATION ---
        tabs = st.tabs([
            "📂 Datos Consolidados",
            "📊 Análisis Vertical",
            "📈 Análisis Horizontal",
            "🏆 Indicadores de Gestión",
            "👁️ Visualizaciones",
            "📄 Generar Reporte PDF"
        ])
        
        # ----------------------------------------------------
        # TAB 1: DATOS CONSOLIDADOS
        # ----------------------------------------------------
        with tabs[0]:
            st.subheader("Cuentas Consolidadas")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📄 Balance General")
                cols_to_show = [c for c in df_bg.columns if not c.endswith('_clean')]
                st.dataframe(df_bg[cols_to_show], use_container_width=True, height=500)
                
            with col2:
                st.markdown("### 📊 Estado de Resultados")
                cols_to_show_er = [c for c in df_er.columns if not c.endswith('_clean')]
                st.dataframe(df_er[cols_to_show_er], use_container_width=True, height=500)
                
        # ----------------------------------------------------
        # TAB 2: ANÁLISIS VERTICAL
        # ----------------------------------------------------
        with tabs[1]:
            st.subheader(f"Análisis Vertical - Período Seleccionado: {selected_av_year}")
            
            df_bg_av, df_er_av = calculate_vertical_analysis(df_bg, df_er, periods, key_values)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Balance General (Activo % Act. Total | Pasivo % Pas. Total | Pat. % Pat. Total)")
                cols_av_bg = ['codigo', 'cuenta', 'categoria', 'subcategoria', selected_av_year, f"{selected_av_year} (%)"]
                bg_disp = df_bg_av[cols_av_bg].copy()
                st.dataframe(
                    bg_disp.style.format({selected_av_year: "${:,.2f}", f"{selected_av_year} (%)": "{:.2f}%"}),
                    use_container_width=True,
                    height=500
                )
                
            with col2:
                st.markdown("#### Estado de Resultados (Ingreso % Ingresos | Egreso % Egresos | Utilidad % Util. Neta)")
                cols_av_er = ['codigo', 'cuenta', 'categoria', selected_av_year, f"{selected_av_year} (%)"]
                er_disp = df_er_av[cols_av_er].copy()
                st.dataframe(
                    er_disp.style.format({selected_av_year: "${:,.2f}", f"{selected_av_year} (%)": "{:.2f}%"}),
                    use_container_width=True,
                    height=500
                )
                
        # ----------------------------------------------------
        # TAB 3: ANÁLISIS HORIZONTAL
        # ----------------------------------------------------
        with tabs[2]:
            if period_a and period_b:
                st.subheader(f"Análisis Horizontal ({period_b} vs {period_a})")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Variaciones en Balance General")
                    df_bg_hor = calculate_horizontal_analysis(df_bg, period_a, period_b)
                    st.dataframe(
                        df_bg_hor.style.format({
                            f'Valor {period_a}': "${:,.2f}",
                            f'Valor {period_b}': "${:,.2f}",
                            'Var. Absoluta': "${:+,.2f}",
                            'Var. Porcentual (%)': "{:+.2f}%"
                        }),
                        use_container_width=True,
                        height=500
                    )
                    
                with col2:
                    st.markdown("#### Variaciones en Estado de Resultados")
                    df_er_hor = calculate_horizontal_analysis(df_er, period_a, period_b)
                    st.dataframe(
                        df_er_hor.style.format({
                            f'Valor {period_a}': "${:,.2f}",
                            f'Valor {period_b}': "${:,.2f}",
                            'Var. Absoluta': "${:+,.2f}",
                            'Var. Porcentual (%)': "{:+.2f}%"
                        }),
                        use_container_width=True,
                        height=500
                    )
            else:
                st.warning("Se requieren al menos 2 periodos en el archivo Excel para realizar el análisis horizontal.")
                
        # ----------------------------------------------------
        # TAB 4: INDICADORES DE GESTIÓN
        # ----------------------------------------------------
        with tabs[3]:
            st.subheader(f"Indicadores de Gestión - Modelo: {tipo_institucion}")
            
            if "Gitman" in tipo_institucion:
                # Calculate indicators with custom params
                ratios_git, df_git = calculate_gitman_indicators(key_values, gitman_params)
                
                # Show key cards for latest year
                latest_year = periods[-1]
                latest_ratios = ratios_git.get(latest_year, {})
                
                st.markdown(f"#### Ratios Clave ({latest_year})")
                
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Razón Circulante</div>
                        <div class="metric-value">{latest_ratios.get('Razón Circulante (Veces)', 0.0):.2f}x</div>
                        <div class="metric-desc">Corto plazo (Ideal > 1.5)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Prueba del Ácido</div>
                        <div class="metric-value">{latest_ratios.get('Prueba del Ácido (Veces)', 0.0):.2f}x</div>
                        <div class="metric-desc">Excluye inventarios</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">ROA</div>
                        <div class="metric-value">{latest_ratios.get('Rendimiento sobre Activos (ROA %)', 0.0):.2f}%</div>
                        <div class="metric-desc">Eficiencia en Activos</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">ROE</div>
                        <div class="metric-value">{latest_ratios.get('Rendimiento sobre Capital (ROE %)', 0.0):.2f}%</div>
                        <div class="metric-desc">Rentabilidad de Socios</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c5:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">PER (P/E)</div>
                        <div class="metric-value">{latest_ratios.get('Relación Precio/Ganancias (PER)', 0.0):.1f}x</div>
                        <div class="metric-desc">Múltiplo de mercado</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("---")
                st.markdown("#### Tabla Histórica de Indicadores (Gitman)")
                st.dataframe(df_git.style.format(precision=2), use_container_width=True)
                
                st.info("💡 ** Lawrence J. Gitman**: Las razones financieras ayudan a evaluar el desempeño histórico y proyectar tendencias corporativas.")
                active_indicators_df = df_git
                
            elif "CAMEL" in tipo_institucion:
                st.markdown("### 🏦 Metodología de Calificación CAMEL")
                col_st, col_val = st.columns([2, 3])
                
                with col_st:
                    st.markdown("#### Dimensiones del Modelo CAMEL")
                    st.dataframe(get_camel_structure(), use_container_width=True)
                    
                with col_val:
                    st.markdown("#### Indicadores Financieros Bancarios")
                    df_camel = calculate_camel_placeholders(key_values)
                    st.dataframe(df_camel.style.format(precision=2), use_container_width=True)
                    st.info("💡 **Basilea / CAMEL**: Regulado para evaluar la liquidez y suficiencia de capital técnico frente a riesgos.")
                
                active_indicators_df = df_camel
                
            elif "PERLAS" in tipo_institucion:
                st.markdown("### 🤝 Sistema de Monitoreo PERLAS")
                col_st, col_val = st.columns([2, 3])
                
                with col_st:
                    st.markdown("#### Componentes y Metas WOCCU")
                    st.dataframe(get_perlas_structure(), use_container_width=True)
                    
                with col_val:
                    st.markdown("#### Indicadores de Cooperativas")
                    df_perlas = calculate_perlas_placeholders(key_values)
                    st.dataframe(df_perlas.style.format(precision=2), use_container_width=True)
                    st.info("💡 **PERLAS**: Herramienta de supervisión gerencial diseñada por la WOCCU para cooperativas.")
                
                active_indicators_df = df_perlas
                
        # ----------------------------------------------------
        # TAB 5: VISUALIZACIONES
        # ----------------------------------------------------
        with tabs[4]:
            st.subheader(f"Estructura Financiera - Periodo: {selected_av_year}")
            
            c1, c2 = st.columns(2)
            
            # Balance Composition
            figs_bal = plot_balance_composition(key_values, selected_av_year)
            fig_inc = plot_income_composition(key_values, selected_av_year)
            
            with c1:
                if figs_bal:
                    fig_assets, fig_liab = figs_bal
                    st.plotly_chart(fig_assets, use_container_width=True)
                    st.plotly_chart(fig_liab, use_container_width=True)
                else:
                    st.warning("No se pudo estructurar el balance general.")
                    
            with c2:
                if fig_inc:
                    st.plotly_chart(fig_inc, use_container_width=True)
                else:
                    st.warning("No se pudo estructurar el estado de resultados.")
                    
            st.markdown("---")
            st.subheader("Tendencias Históricas")
            fig_line = plot_key_accounts_evolution(key_values)
            st.plotly_chart(fig_line, use_container_width=True)
            
        # ----------------------------------------------------
        # TAB 6: GENERAR REPORTE PDF
        # ----------------------------------------------------
        with tabs[5]:
            st.subheader("Generar Informe Financiero PDF")
            st.markdown("Configure los textos finales que se incluirán en el informe dictaminado.")
            
            txt_av = st.text_area(
                "Observaciones del Análisis Vertical:",
                value="El análisis estructural demuestra que los recursos de la entidad se encuentran asignados adecuadamente conforme a la naturaleza del negocio.",
                height=80
            )
            
            txt_ah = st.text_area(
                "Observaciones del Análisis Horizontal:",
                value="La evolución histórica de las cuentas principales refleja un comportamiento de crecimiento consistente con el entorno macroeconómico actual.",
                height=80
            )
            
            st.markdown("---")
            if st.button("🚀 Compilar y Generar Reporte PDF"):
                with st.spinner("Escribiendo PDF con ReportLab..."):
                    pdf_buffer = generate_pdf_report(
                        tipo_institucion=tipo_institucion,
                        nombre_institucion=nombre_institucion,
                        key_values=key_values,
                        df_indicators=active_indicators_df,
                        vertical_summary_text=txt_av,
                        horizontal_summary_text=txt_ah
                    )
                    
                    st.success("🎉 Reporte PDF generado correctamente!")
                    
                    st.download_button(
                        label="💾 Descargar Reporte Financiero PDF",
                        data=pdf_buffer,
                        file_name=f"Reporte_Analisis_{tipo_institucion.split()[0]}.pdf",
                        mime="application/pdf"
                    )
                    
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo Excel: {e}")
        st.exception(e)
else:
    # Landing instructions
    st.info("📥 Por favor cargue un archivo Excel ordenado por años en la barra lateral para iniciar el análisis.")
    
    with st.expander("🛠️ Ver Estructura Ficticia Recomendada"):
        st.markdown("""
        **Estructura esperada por cada pestaña anual (ej. pestaña '2023'):**
        
        | codigo | cuenta | saldo |
        |---|---|---|
        | 1 | **Activo** | 500000 |
        | 1.1 | **Activo Corriente** | 200000 |
        | 1.1.01 | Caja y Bancos | 80000 |
        | 1.1.02 | Cuentas por Cobrar | 70000 |
        | 1.1.03 | Inventarios | 50000 |
        | 1.2 | **Activo No Corriente** | 300000 |
        | 1.2.01 | Propiedades, Planta y Equipo | 300000 |
        | 2 | **Pasivo** | 220000 |
        | 2.1 | **Pasivo Corriente** | 120000 |
        | 2.1.01 | Proveedores / Cuentas por Pagar | 70000 |
        | 2.1.02 | Obligaciones Corrientes | 50000 |
        | 2.2 | **Pasivo No Corriente** | 100000 |
        | 3 | **Patrimonio** | 280000 |
        | 3.1 | Capital Social | 200000 |
        | 3.2 | Utilidades Acumuladas | 80000 |
        | 4 | **Ingresos** | 600000 |
        | 4.1 | Ventas | 600000 |
        | 5 | **Egresos (Gastos)** | 480000 |
        | 5.1 | Costo de Ventas | 320000 |
        | 5.2 | Gastos Operativos | 130000 |
        | 5.3 | Gastos por Intereses | 10000 |
        | 5.4 | Utilidad Neta del Ejercicio | 120000 |
        """)
