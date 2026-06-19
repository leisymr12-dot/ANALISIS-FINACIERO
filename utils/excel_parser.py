import pandas as pd
import re
import unicodedata

def clean_text(text):
    """Normalize text: remove accents, spaces, and convert to lowercase."""
    if text is None:
        return ""
    # Convert to string and clean float suffix if it is a year-like float
    text_str = str(text).strip()
    if text_str.endswith('.0'):
        text_str = text_str[:-2]
    text_str = text_str.lower()
    text_str = "".join(
        c for c in unicodedata.normalize('NFD', text_str)
        if unicodedata.category(c) != 'Mn'
    )
    text_str = re.sub(r'\s+', ' ', text_str)
    return text_str

def to_numeric_clean(series):
    """
    Robustly converts a series of strings/numbers to floats, removing currency
    symbols, parenthesis, and handling different decimal/thousands separators.
    """
    cleaned = []
    for val in series:
        if pd.isna(val):
            cleaned.append(0.0)
            continue
        if isinstance(val, (int, float)):
            cleaned.append(float(val))
            continue
            
        val_str = str(val).strip()
        if not val_str:
            cleaned.append(0.0)
            continue
            
        # Strip currency symbols, spaces, percent signs, and byte marks
        val_str = re.sub(r'[\$\s\€\£\¥\%\u200b]', '', val_str)
        
        # Handle parenthesis for negative values e.g. (1,250.00)
        is_neg = False
        if val_str.startswith('(') and val_str.endswith(')'):
            is_neg = True
            val_str = val_str[1:-1]
        elif val_str.startswith('-'):
            is_neg = True
            val_str = val_str[1:]
            
        if not val_str:
            cleaned.append(0.0)
            continue
            
        # Handle Spanish vs US formatting:
        # German/Spanish style: 1.234,56 -> 1234.56
        # US style: 1,234.56 -> 1234.56
        if ',' in val_str and '.' in val_str:
            comma_idx = val_str.find(',')
            period_idx = val_str.find('.')
            if comma_idx > period_idx:
                val_str = val_str.replace('.', '').replace(',', '.')
            else:
                val_str = val_str.replace(',', '')
        elif ',' in val_str:
            # Single comma: check if it looks like thousands (e.g. 1,234) or decimal (123,45)
            parts = val_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 3:
                val_str = val_str.replace(',', '')
            else:
                val_str = val_str.replace(',', '.')
                
        try:
            num = float(val_str)
            cleaned.append(-num if is_neg else num)
        except ValueError:
            cleaned.append(0.0)
            
    return pd.Series(cleaned, index=series.index)

def classify_account(code, name, is_financial_institution=False):
    """
    Classifies an account based on its accounting code prefix or account name.
    """
    code_clean = re.sub(r'[^0-9\.]', '', str(code)).strip()
    name_clean = clean_text(name)
    
    category = ""
    subcategory = ""
    
    # 1. Classify using code first
    if code_clean:
        first_char = code_clean[0]
        if first_char == '1':
            category = "Activo"
            if is_financial_institution:
                # 11-14 are current assets in bank (cash, investments, loan portfolio)
                if code_clean.startswith(('11', '12', '13', '14', '1.1', '1.2', '1.3', '1.4')):
                    subcategory = "Activo Corriente"
                else:
                    subcategory = "Activo No Corriente"
            else:
                if code_clean.startswith(('1.1', '101', '11')):
                    subcategory = "Activo Corriente"
                else:
                    subcategory = "Activo No Corriente"
        elif first_char == '2':
            category = "Pasivo"
            if is_financial_institution:
                # 21-24 are current liabilities in bank (deposits, public obligations)
                if code_clean.startswith(('21', '22', '23', '24', '2.1', '2.2', '2.3', '2.4')):
                    subcategory = "Pasivo Corriente"
                else:
                    subcategory = "Pasivo No Corriente"
            else:
                if code_clean.startswith(('2.1', '201', '21')):
                    subcategory = "Pasivo Corriente"
                else:
                    subcategory = "Pasivo No Corriente"
        elif first_char == '3':
            category = "Patrimonio"
        elif first_char == '4':
            if is_financial_institution:
                category = "Egreso"  # Banks use 4 for expenses/egresos
            else:
                category = "Ingreso"  # Companies use 4 for revenues
        elif first_char == '5':
            if is_financial_institution:
                category = "Ingreso"  # Banks use 5 for revenues
            else:
                category = "Egreso"  # Companies use 5 for expenses
        elif first_char == '6':
            category = "Egreso"  # Cost of sales
            
    # 2. Heuristics based on account names
    if not category:
        if "activo" in name_clean:
            category = "Activo"
            if "corriente" in name_clean or "circulante" in name_clean or "disponible" in name_clean:
                subcategory = "Activo Corriente"
            elif "no corriente" in name_clean or "fijo" in name_clean:
                subcategory = "Activo No Corriente"
        elif "pasivo" in name_clean:
            category = "Pasivo"
            if "corriente" in name_clean or "circulante" in name_clean or "corto plazo" in name_clean:
                subcategory = "Pasivo Corriente"
            elif "no corriente" in name_clean or "largo plazo" in name_clean:
                subcategory = "Pasivo No Corriente"
        elif "patrimonio" in name_clean or "capital social" in name_clean or "capital contable" in name_clean:
            category = "Patrimonio"
        elif "ingreso" in name_clean or "venta" in name_clean or "comision" in name_clean or "facturacion" in name_clean:
            category = "Ingreso"
        elif "gasto" in name_clean or "costo" in name_clean or "egreso" in name_clean or "perdida" in name_clean:
            category = "Egreso"
            
    # 3. Fallback name matches for common terms
    if not category:
        if name_clean in ['caja', 'bancos', 'clientes', 'inventarios', 'caja y bancos', 'efectivo', 'cuentas por cobrar', 'existencias', 'fondos disponibles']:
            category = "Activo"
            subcategory = "Activo Corriente"
        elif name_clean in ['proveedores', 'cuentas por pagar', 'documentos por pagar', 'obligaciones con el publico', 'depositos']:
            category = "Pasivo"
            subcategory = "Pasivo Corriente"
        elif name_clean in ['capital', 'reservas', 'utilidades acumuladas', 'capital social']:
            category = "Patrimonio"
        elif name_clean in ['ventas', 'otros ingresos', 'ingresos financieros']:
            category = "Ingreso"
        elif name_clean in ['costo de ventas', 'compras', 'sueldos', 'servicios', 'arriendos', 'intereses', 'gastos financieros', 'gastos de administracion']:
            category = "Egreso"
            
    # 4. Refine subcategory if empty
    if category == "Activo" and not subcategory:
        if any(w in name_clean for w in ['corriente', 'circulante', 'caja', 'banco', 'efectivo', 'cliente', 'cobrar', 'inventario', 'existencia', 'disponible', 'mercancia']):
            subcategory = "Activo Corriente"
        else:
            subcategory = "Activo No Corriente"
            
    if category == "Pasivo" and not subcategory:
        if any(w in name_clean for w in ['corriente', 'circulante', 'corto plazo', 'proveedor', 'pagar', 'deposito', 'obligacion corriente']):
            subcategory = "Pasivo Corriente"
        else:
            subcategory = "Pasivo No Corriente"
            
    return category, subcategory

def extract_key_values_for_period(df_bg, df_er, p, is_financial_institution=False):
    """
    Extracts key financial statement values for the specified period 'p'.
    """
    vals = {
        'activo_corriente': 0.0,
        'activo_total': 0.0,
        'inventarios': 0.0,
        'cuentas_por_cobrar': 0.0,
        'pasivo_corriente': 0.0,
        'pasivo_total': 0.0,
        'cuentas_por_pagar': 0.0,
        'patrimonio_total': 0.0,
        'ingresos': 0.0,
        'costos': 0.0,
        'gastos': 0.0,
        'utilidad_operativa': 0.0,
        'gastos_interes': 0.0,
        'pagos_arrendamiento': 0.0,
        'utilidad_neta': 0.0,
        'utilidad_bruta': 0.0
    }
    
    def get_val_by_name(df, terms, is_exact=False):
        for term in terms:
            term_clean = clean_text(term)
            if is_exact:
                matched = df[df['cuenta_clean'] == term_clean]
            else:
                matched = df[df['cuenta_clean'].str.contains(term_clean, na=False)]
            if not matched.empty:
                return float(matched[p].iloc[0])
        return None

    # Balance Sheet extraction
    if not df_bg.empty and p in df_bg.columns:
        # Activo Total
        act_tot = get_val_by_name(df_bg, ['total activo', 'activo total', 'activos totales'], is_exact=True)
        if act_tot is None:
            act_tot = get_val_by_name(df_bg, ['total activo', 'activo total', 'activos totales'], is_exact=False)
        if act_tot is None:
            act_tot = df_bg[df_bg['categoria_clean'] == 'activo'][p].sum()
        vals['activo_total'] = act_tot or 0.0
        
        # Activo Corriente
        act_corr = get_val_by_name(df_bg, ['total activo corriente', 'total activos corrientes', 'total activo circulante', 'total corriente', 'total circulante'], is_exact=True)
        if act_corr is None:
            act_corr = get_val_by_name(df_bg, ['total activo corriente', 'total activos corrientes', 'total activo circulante', 'total corriente', 'total circulante'], is_exact=False)
        if act_corr is None:
            act_corr = df_bg[(df_bg['categoria_clean'] == 'activo') & (df_bg['subcategoria_clean'] == 'activo corriente')][p].sum()
        vals['activo_corriente'] = act_corr or 0.0
        
        # Inventarios
        inv = get_val_by_name(df_bg, ['inventarios', 'inventario', 'existencias', 'mercancias'], is_exact=True)
        if inv is None:
            inv = get_val_by_name(df_bg, ['inventario', 'existencia', 'mercancia'], is_exact=False)
        vals['inventarios'] = inv or 0.0
        
        # Cuentas por Cobrar
        cxc = get_val_by_name(df_bg, ['cuentas por cobrar', 'clientes', 'cuentas por cobrar comerciales', 'deudores'], is_exact=True)
        if cxc is None:
            cxc = get_val_by_name(df_bg, ['cuentas por cobrar', 'clientes', 'deudores'], is_exact=False)
        vals['cuentas_por_cobrar'] = cxc or 0.0
        
        # Pasivo Total
        pas_tot = get_val_by_name(df_bg, ['total pasivo', 'pasivo total', 'pasivos totales'], is_exact=True)
        if pas_tot is None:
            pas_tot = get_val_by_name(df_bg, ['total pasivo', 'pasivo total', 'pasivos totales'], is_exact=False)
        if pas_tot is None:
            pas_tot = df_bg[df_bg['categoria_clean'] == 'pasivo'][p].sum()
        vals['pasivo_total'] = pas_tot or 0.0
        
        # Pasivo Corriente
        pas_corr = get_val_by_name(df_bg, ['total pasivo corriente', 'total pasivos corrientes', 'total pasivo circulante', 'total pasivo a corto plazo'], is_exact=True)
        if pas_corr is None:
            pas_corr = get_val_by_name(df_bg, ['total pasivo corriente', 'total pasivos corrientes', 'total pasivo circulante', 'total pasivo a corto plazo'], is_exact=False)
        if pas_corr is None:
            pas_corr = df_bg[(df_bg['categoria_clean'] == 'pasivo') & (df_bg['subcategoria_clean'] == 'pasivo corriente')][p].sum()
        vals['pasivo_corriente'] = pas_corr or 0.0
        
        # Cuentas por Pagar
        cxp = get_val_by_name(df_bg, ['cuentas por pagar', 'proveedores', 'cuentas por pagar comerciales', 'acreedores'], is_exact=True)
        if cxp is None:
            cxp = get_val_by_name(df_bg, ['cuentas por pagar', 'proveedor', 'acreedor'], is_exact=False)
        vals['cuentas_por_pagar'] = cxp or 0.0
        
        # Patrimonio Total
        pat_tot = get_val_by_name(df_bg, ['total patrimonio', 'patrimonio total', 'total patrimonio neto', 'patrimonio neto', 'total capital contable'], is_exact=True)
        if pat_tot is None:
            pat_tot = get_val_by_name(df_bg, ['total patrimonio', 'patrimonio total', 'total patrimonio neto', 'patrimonio neto', 'total capital contable'], is_exact=False)
        if pat_tot is None:
            pat_tot = df_bg[df_bg['categoria_clean'] == 'patrimonio'][p].sum()
        vals['patrimonio_total'] = pat_tot or 0.0
        
    # Income Statement extraction
    if not df_er.empty and p in df_er.columns:
        # Ingresos (Ventas)
        ing = get_val_by_name(df_er, ['total ingresos', 'ingresos totales', 'ingresos operacionales', 'ventas netas', 'ventas', 'ingresos de actividades ordinarias'], is_exact=True)
        if ing is None:
            ing = get_val_by_name(df_er, ['total ingresos', 'ingresos totales', 'ingresos operacionales', 'ventas', 'ingresos'], is_exact=False)
        if ing is None:
            ing = df_er[df_er['categoria_clean'] == 'ingreso'][p].sum()
        vals['ingresos'] = ing or 0.0
        
        # Costos (Costo de ventas)
        cost = get_val_by_name(df_er, ['costo de ventas', 'costos de ventas', 'costo de venta', 'costo de producción', 'costo de lo vendido'], is_exact=True)
        if cost is None:
            cost = get_val_by_name(df_er, ['costo de ventas', 'costo de venta', 'costo de produccion', 'costos', 'costo'], is_exact=False)
        vals['costos'] = cost or 0.0
        
        # Utilidad Bruta
        ut_bruta = get_val_by_name(df_er, ['utilidad bruta', 'ganancia bruta', 'margen bruto', 'resultado bruto'], is_exact=True)
        if ut_bruta is None:
            ut_bruta = get_val_by_name(df_er, ['utilidad bruta', 'ganancia bruta', 'resultado bruto'], is_exact=False)
        if ut_bruta is None:
            ut_bruta = vals['ingresos'] - vals['costos']
        vals['utilidad_bruta'] = ut_bruta or 0.0
        
        # Gastos (Gastos Operativos)
        gast = get_val_by_name(df_er, ['total gastos operacionales', 'total gastos de operacion', 'gastos operacionales', 'total gastos', 'gastos administrativos y ventas'], is_exact=True)
        if gast is None:
            gast = get_val_by_name(df_er, ['total gastos operacionales', 'total gastos de operacion', 'gastos operacionales', 'total gastos', 'gastos operativos'], is_exact=False)
        if gast is None:
            gast = df_er[df_er['categoria_clean'] == 'egreso'][p].sum() - vals['costos']
        vals['gastos'] = gast or 0.0
        
        # Utilidad Operativa (EBIT)
        ut_op = get_val_by_name(df_er, ['utilidad operativa', 'utilidad de operacion', 'ebit', 'utilidad antes de intereses e impuestos', 'resultado operacional'], is_exact=True)
        if ut_op is None:
            ut_op = get_val_by_name(df_er, ['utilidad operativa', 'utilidad de operacion', 'ebit', 'resultado operacional'], is_exact=False)
        if ut_op is None:
            ut_op = vals['utilidad_bruta'] - vals['gastos']
        vals['utilidad_operativa'] = ut_op or 0.0
        
        # Gastos por Intereses
        g_int = get_val_by_name(df_er, ['gastos por intereses', 'intereses pagados', 'gastos financieros', 'gastos de intereses', 'intereses'], is_exact=True)
        if g_int is None:
            g_int = get_val_by_name(df_er, ['gastos por intereses', 'intereses pagados', 'gastos financieros', 'intereses'], is_exact=False)
        vals['gastos_interes'] = g_int or 0.0
        
        # Pagos de Arrendamiento
        arriendo = get_val_by_name(df_er, ['arriendos', 'arrendamientos', 'gastos de arriendo', 'alquileres'], is_exact=True)
        if arriendo is None:
            arriendo = get_val_by_name(df_er, ['arriendo', 'arrendamiento', 'alquiler'], is_exact=False)
        vals['pagos_arrendamiento'] = arriendo or 0.0
        
        # Utilidad Neta
        ut_neta = get_val_by_name(df_er, ['utilidad neta', 'utilidad del ejercicio', 'resultado del ejercicio', 'ganancia neta', 'utilidad liquida', 'utilidad neta del ejercicio'], is_exact=True)
        if ut_neta is None:
            ut_neta = get_val_by_name(df_er, ['utilidad neta', 'utilidad del ejercicio', 'resultado del ejercicio', 'ganancia neta', 'utilidad neta del ejercicio'], is_exact=False)
        if ut_neta is None:
            ut_neta = vals['utilidad_operativa'] - vals['gastos_interes']
        vals['utilidad_neta'] = ut_neta or 0.0
        
    return vals

def parse_financial_excel(file_path_or_bytes, is_financial_institution=False):
    """
    Parses the Excel file where each tab is a year (e.g. 2021, 2022, 2023)
    containing combined Balance Sheet and Income Statement.
    """
    xl = pd.ExcelFile(file_path_or_bytes)
    sheet_names = xl.sheet_names
    
    # Filter year-based sheets (e.g. 2021, 2022, 2023)
    year_sheets = []
    for s in sheet_names:
        s_clean = s.strip()
        if re.match(r'^(19|20)\d\d$', s_clean):
            year_sheets.append(s_clean)
            
    if not year_sheets:
        raise ValueError("No se detectaron pestañas numéricas correspondientes a años (ej. 2022, 2023). Verifique el archivo.")
        
    # Sort chronologically
    year_sheets = sorted(year_sheets, key=lambda x: int(x))
    
    dfs_by_year = {}
    
    for year in year_sheets:
        df_raw = xl.parse(year, header=None)
        if df_raw.empty:
            continue
            
        # Scan first 25 rows to identify the headers row
        header_row_idx = 0
        max_matches = 0
        cols_to_find = ['codigo', 'cuenta', 'nombre', 'saldo', 'valor', 'monto', 'desc', 'saldo final', 'saldo_final']
        
        for i in range(min(25, len(df_raw))):
            row_vals = [clean_text(val) for val in df_raw.iloc[i].values]
            matches = sum(1 for val in row_vals if any(col_name in val for col_name in cols_to_find))
            if matches > max_matches:
                max_matches = matches
                header_row_idx = i
                
        df_year = xl.parse(year, skiprows=header_row_idx)
        df_year.columns = [str(c).strip() for c in df_year.columns]
        
        # Identify code, account name and balance columns
        code_col = None
        name_col = None
        balance_col = None
        
        # Look for code column
        for c in df_year.columns:
            c_clean = clean_text(c)
            if c_clean in ['codigo', 'cod', 'código', 'codigo contable', 'cod.']:
                code_col = c
                break
        if not code_col:
            # Fallback: check if any column contains code pattern
            for c in df_year.columns:
                if df_year[c].astype(str).str.match(r'^[0-9\.]+$').any():
                    code_col = c
                    break
        if not code_col:
            code_col = df_year.columns[0]
            
        # Look for account name column
        for c in df_year.columns:
            c_clean = clean_text(c)
            if c_clean in ['cuenta', 'nombre de la cuenta', 'nombre de cuenta', 'cuenta contable', 'nombre', 'descripcion', 'descripción', 'concepto', 'detalle']:
                name_col = c
                break
        if not name_col:
            for c in df_year.columns:
                if c != code_col and df_year[c].dtype == 'object':
                    name_col = c
                    break
        if not name_col:
            name_col = df_year.columns[1] if len(df_year.columns) > 1 else df_year.columns[0]
            
        # Look for balance column
        # A. Exact Match
        for c in df_year.columns:
            c_clean = clean_text(c)
            if c_clean in ['saldo', 'valor', 'monto', 'saldo final', 'saldo_final', 'balance', 'total', 'neto', year]:
                balance_col = c
                break
                
        # B. Substring Match
        if not balance_col:
            for c in df_year.columns:
                c_clean = clean_text(c)
                if any(kw in c_clean for kw in ['saldo', 'valor', 'monto', 'neto', year]):
                    balance_col = c
                    break
                    
        # C. Highest Numeric values ratio Match
        if not balance_col:
            best_col = None
            max_numeric_ratio = 0.0
            for c in df_year.columns:
                if c in [code_col, name_col]:
                    continue
                series_numeric = to_numeric_clean(df_year[c])
                num_valid = (series_numeric != 0.0).sum()
                total_vals = len(df_year[c])
                if total_vals > 0:
                    ratio = num_valid / total_vals
                    if ratio > max_numeric_ratio:
                        max_numeric_ratio = ratio
                        best_col = c
            if max_numeric_ratio > 0.3:
                balance_col = best_col
                
        # D. Ultimate Fallback to last column
        if not balance_col:
            balance_col = df_year.columns[-1]
            
        # Clean dataframe structure using the robust to_numeric_clean
        df_clean = pd.DataFrame()
        df_clean['codigo'] = df_year[code_col].fillna("").astype(str).str.strip()
        df_clean['cuenta'] = df_year[name_col].fillna("").astype(str).str.strip()
        df_clean[year] = to_numeric_clean(df_year[balance_col])
        
        # Remove empty rows
        df_clean = df_clean[(df_clean['codigo'] != "") | (df_clean['cuenta'] != "")]
        
        # Group and sum duplicates inside the same year
        df_clean = df_clean.groupby(['codigo', 'cuenta'], as_index=False)[year].sum()
        dfs_by_year[year] = df_clean
        
    # Consolidate all years
    merged_df = None
    for year, df in dfs_by_year.items():
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=['codigo', 'cuenta'], how='outer')
            
    if merged_df is None or merged_df.empty:
        raise ValueError("No se pudo extraer información financiera de las pestañas del Excel.")
        
    merged_df.fillna(0.0, inplace=True)
    
    # Classify all accounts
    merged_df['categoria'] = ""
    merged_df['subcategoria'] = ""
    
    for idx, row in merged_df.iterrows():
        code = str(row['codigo']).strip()
        name = str(row['cuenta']).strip()
        cat, subcat = classify_account(code, name, is_financial_institution)
        merged_df.at[idx, 'categoria'] = cat
        merged_df.at[idx, 'subcategoria'] = subcat
        
    # Split into BG and ER
    df_bg = merged_df[merged_df['categoria'].isin(['Activo', 'Pasivo', 'Patrimonio'])].copy()
    df_er = merged_df[merged_df['categoria'].isin(['Ingreso', 'Egreso'])].copy()
    
    # Normalize clean text columns
    for df in [df_bg, df_er]:
        df['cuenta_clean'] = df['cuenta'].apply(clean_text)
        df['categoria_clean'] = df['categoria'].apply(clean_text)
        df['subcategoria_clean'] = df['subcategoria'].apply(clean_text)
        
    # Extract key values per year
    key_values = {}
    periods = year_sheets
    
    for p in periods:
        key_values[p] = extract_key_values_for_period(df_bg, df_er, p, is_financial_institution)
        
    # Ensure other columns are string to prevent streamlit type casting crashes
    for df in [df_bg, df_er]:
        for col in df.columns:
            if col not in periods:
                df[col] = df[col].astype(str).replace('nan', '')
                
    return {
        'df_bg': df_bg,
        'df_er': df_er,
        'periods': periods,
        'key_values': key_values
    }
