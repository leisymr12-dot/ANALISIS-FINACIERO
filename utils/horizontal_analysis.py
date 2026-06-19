import pandas as pd
import numpy as np

def calculate_horizontal_analysis(df, period_a, period_b):
    """
    Calculates horizontal analysis between period_a (base) and period_b (comparison).
    Returns a DataFrame with columns:
        cuenta, categoria, subcategoria, valor_a, valor_b, var_abs, var_pct
    """
    if period_a not in df.columns or period_b not in df.columns:
        # Return empty df with expected structure if periods not found
        return pd.DataFrame(columns=['cuenta', 'categoria', 'subcategoria', 'valor_a', 'valor_b', 'var_abs', 'var_pct'])
        
    df_res = pd.DataFrame()
    df_res['cuenta'] = df['cuenta']
    df_res['categoria'] = df['categoria']
    df_res['subcategoria'] = df['subcategoria']
    
    val_a = pd.to_numeric(df[period_a], errors='coerce').fillna(0.0)
    val_b = pd.to_numeric(df[period_b], errors='coerce').fillna(0.0)
    
    df_res[f'Valor {period_a}'] = val_a
    df_res[f'Valor {period_b}'] = val_b
    
    # Calculate variations
    var_abs = val_b - val_a
    
    # Handle division by zero using numpy
    var_pct = np.zeros_like(var_abs)
    non_zero_mask = val_a != 0.0
    var_pct[non_zero_mask] = (var_abs[non_zero_mask] / val_a[non_zero_mask]) * 100.0
    
    df_res['Var. Absoluta'] = var_abs
    df_res['Var. Porcentual (%)'] = var_pct
    
    return df_res
