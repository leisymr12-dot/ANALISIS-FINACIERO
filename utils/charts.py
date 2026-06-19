import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_balance_composition(key_values, selected_period):
    """
    Generates premium pie/donut charts of the balance sheet composition (Assets and Liabilities + Equity)
    for a selected period.
    """
    if selected_period not in key_values:
        return None
        
    vals = key_values[selected_period]
    act_corr = vals.get('activo_corriente', 0.0)
    act_tot = vals.get('activo_total', 0.0)
    act_no_corr = max(0.0, act_tot - act_corr)
    
    pas_corr = vals.get('pasivo_corriente', 0.0)
    pas_tot = vals.get('pasivo_total', 0.0)
    pas_no_corr = max(0.0, pas_tot - pas_corr)
    pat_tot = vals.get('patrimonio_total', 0.0)
    
    # 1. Assets Donut Chart
    df_assets = pd.DataFrame({
        'Componente': ['Activo Corriente', 'Activo No Corriente'],
        'Monto': [act_corr, act_no_corr]
    })
    
    # Premium colors: Teal-blue palette
    colors_assets = ['#0D9488', '#3B82F6']
    
    fig_assets = px.pie(
        df_assets, 
        values='Monto', 
        names='Componente', 
        title=f"Composición del Activo ({selected_period})",
        hole=0.4,
        color_discrete_sequence=colors_assets
    )
    fig_assets.update_traces(
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    fig_assets.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(t=50, b=40, l=10, r=10),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title_font=dict(size=14, color='#1E3A8A', family="Plus Jakarta Sans, sans-serif")
    )
    
    # 2. Liabilities & Equity Donut Chart
    df_liab_eq = pd.DataFrame({
        'Componente': ['Pasivo Corriente', 'Pasivo No Corriente', 'Patrimonio Neto'],
        'Monto': [pas_corr, pas_no_corr, pat_tot]
    })
    
    # Premium colors: Rose/Indigo/Emerald
    colors_liab_eq = ['#EF4444', '#F59E0B', '#10B981']
    
    fig_liab_eq = px.pie(
        df_liab_eq, 
        values='Monto', 
        names='Componente', 
        title=f"Composición de Pasivo y Patrimonio ({selected_period})",
        hole=0.4,
        color_discrete_sequence=colors_liab_eq
    )
    fig_liab_eq.update_traces(
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    fig_liab_eq.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(t=50, b=40, l=10, r=10),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title_font=dict(size=14, color='#1E3A8A', family="Plus Jakarta Sans, sans-serif")
    )
    
    return fig_assets, fig_liab_eq

def plot_income_composition(key_values, selected_period):
    """
    Generates a donut chart showing the breakdown of revenue into Costs, Expenses, and Net profit.
    """
    if selected_period not in key_values:
        return None
        
    vals = key_values[selected_period]
    ingresos = vals.get('ingresos', 0.0)
    costos = vals.get('costos', 0.0)
    gastos = vals.get('gastos', 0.0)
    utilidad = vals.get('utilidad_neta', 0.0)
    
    # Sum of items might not equal revenues due to taxes/interest, represent differences
    otros = max(0.0, ingresos - (costos + gastos + utilidad))
    
    labels = ['Costos de Ventas', 'Gastos Operativos', 'Utilidad Neta']
    values = [costos, gastos, utilidad]
    
    # Premium colors: Orange/Red/Green
    colors_inc = ['#F97316', '#DC2626', '#10B981']
    
    if otros > 0.01 * ingresos:
        labels.append('Otros Egresos/Impuestos')
        values.append(otros)
        colors_inc.append('#6B7280') # Gray for other items
        
    df_inc = pd.DataFrame({
        'Concepto': labels,
        'Valor': values
    })
    
    fig = px.pie(
        df_inc, 
        values='Valor', 
        names='Concepto', 
        title=f"Distribución del Ingreso ({selected_period})",
        hole=0.4,
        color_discrete_sequence=colors_inc
    )
    fig.update_traces(
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        margin=dict(t=50, b=40, l=10, r=10),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title_font=dict(size=14, color='#1E3A8A', family="Plus Jakarta Sans, sans-serif")
    )
    
    return fig

def plot_key_accounts_evolution(key_values):
    """
    Generates a premium line chart showing the trend/evolution of key accounts over time.
    """
    periods = sorted(list(key_values.keys()), key=lambda x: int(x))
    
    data = []
    for p in periods:
        vals = key_values[p]
        data.append({
            'Período': str(p),
            'Activo Total': vals.get('activo_total', 0.0),
            'Pasivo Total': vals.get('pasivo_total', 0.0),
            'Patrimonio Neto': vals.get('patrimonio_total', 0.0),
            'Ingresos Totales': vals.get('ingresos', 0.0),
            'Utilidad Neta': vals.get('utilidad_neta', 0.0)
        })
        
    df_long = pd.DataFrame(data)
    
    df_melted = df_long.melt(
        id_vars=['Período'], 
        value_vars=['Activo Total', 'Pasivo Total', 'Patrimonio Neto', 'Ingresos Totales', 'Utilidad Neta'],
        var_name='Cuenta Financiera',
        value_name='Monto (USD)'
    )
    
    # Custom color palette for accounts
    color_map = {
        'Activo Total': '#3B82F6',       # Blue
        'Pasivo Total': '#EF4444',       # Red
        'Patrimonio Neto': '#10B981',   # Emerald Green
        'Ingresos Totales': '#8B5CF6',  # Purple
        'Utilidad Neta': '#F59E0B'       # Amber
    }
    
    fig = px.line(
        df_melted, 
        x='Período', 
        y='Monto (USD)', 
        color='Cuenta Financiera', 
        color_discrete_map=color_map,
        markers=True,
        title="Evolución Histórica de Cuentas Principales"
    )
    
    # Enable smooth lines (spline) and styling
    fig.update_traces(
        line=dict(width=3, shape='spline'),
        marker=dict(size=8, symbol='circle', line=dict(width=2, color='#FFFFFF'))
    )
    
    fig.update_layout(
        xaxis_title="Período (Año)",
        yaxis_title="Monto (USD)",
        legend_title="Cuentas",
        hovermode="x unified",
        grid=dict(rows=1, columns=1),
        margin=dict(t=60, b=40, l=40, r=40),
        plot_bgcolor='rgba(243, 244, 246, 0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11),
        title_font=dict(size=16, color='#1E3A8A', family="Plus Jakarta Sans, sans-serif"),
        yaxis=dict(
            gridcolor='#E5E7EB',
            zerolinecolor='#9CA3AF'
        ),
        xaxis=dict(
            gridcolor='#E5E7EB'
        )
    )
    
    return fig
