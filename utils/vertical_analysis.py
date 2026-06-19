import pandas as pd

def calculate_vertical_analysis(df_bg, df_er, periods, key_values):
    """
    Calculates vertical analysis.
    - Balance General:
      - Activo accounts as % of Activo Total
      - Pasivo accounts as % of Pasivo Total
      - Patrimonio accounts as % of Patrimonio Total
    - Estado de Resultados:
      - Ingreso accounts as % of Total Ingresos
      - Egreso/Costos/Gastos accounts as % of Total Egresos (Gastos/Costos)
      - Utility accounts (Utilidad Bruta, Operativa, Neta) as % of Utilidad Neta
    """
    df_bg_av = df_bg.copy()
    df_er_av = df_er.copy()
    
    for p in periods:
        vals = key_values.get(p, {})
        act_tot = vals.get('activo_total', 0.0)
        pas_tot = vals.get('pasivo_total', 0.0)
        pat_tot = vals.get('patrimonio_total', 0.0)
        
        # Calculate BG percentages
        bg_percentages = []
        for idx, row in df_bg_av.iterrows():
            val = float(row[p])
            cat = row['categoria']
            
            pct = 0.0
            if cat == "Activo":
                if act_tot != 0.0:
                    pct = (val / act_tot) * 100
            elif cat == "Pasivo":
                if pas_tot != 0.0:
                    pct = (val / pas_tot) * 100
            elif cat == "Patrimonio":
                if pat_tot != 0.0:
                    pct = (val / pat_tot) * 100
            bg_percentages.append(pct)
            
        df_bg_av[f"{p} (%)"] = bg_percentages
        
        # Calculate ER percentages
        ing_tot = vals.get('ingresos', 0.0)
        # Sum up all Egresos in this year to get total expenses/costs
        egr_tot = df_er_av[df_er_av['categoria'] == 'Egreso'][p].sum()
        if egr_tot == 0.0:
            egr_tot = vals.get('costos', 0.0) + vals.get('gastos', 0.0)
            
        ut_neta = vals.get('utilidad_neta', 0.0)
        
        er_percentages = []
        for idx, row in df_er_av.iterrows():
            val = float(row[p])
            cat = row['categoria']
            ac_name_clean = row['cuenta_clean']
            
            # Identify if it is a profit/utility row
            is_utility = any(term in ac_name_clean for term in ['utilidad', 'ganancia', 'resultado', 'ebit', 'operacional', 'perdida'])
            
            pct = 0.0
            if is_utility:
                if ut_neta != 0.0:
                    pct = (val / ut_neta) * 100
                elif ing_tot != 0.0:
                    pct = (val / ing_tot) * 100
            elif cat == "Ingreso":
                if ing_tot != 0.0:
                    pct = (val / ing_tot) * 100
            elif cat == "Egreso":
                if egr_tot != 0.0:
                    pct = (val / egr_tot) * 100
            else:
                if ing_tot != 0.0:
                    pct = (val / ing_tot) * 100
            er_percentages.append(pct)
            
        df_er_av[f"{p} (%)"] = er_percentages
        
    return df_bg_av, df_er_av
