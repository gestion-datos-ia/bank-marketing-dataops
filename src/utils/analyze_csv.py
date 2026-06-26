"""Utilidad para analizar estructura de archivos CSV."""

import pandas as pd
from pathlib import Path


def describe_csv_columns(file_path: str, max_unique_display: int = 20) -> None:
    """
    Describe todas las columnas de un CSV: tipo de dato, únicos y valores.
    
    Args:
        file_path: Ruta del archivo CSV
        max_unique_display: Máximo número de valores únicos a mostrar
    """
    df = pd.read_csv(file_path)
    
    print("\n" + "=" * 100)
    print(f"📊 ANÁLISIS DE: {Path(file_path).name}")
    print("=" * 100 + "\n")
    
    for col in df.columns:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        null_count = df[col].isnull().sum()
        
        # Obtener valores únicos
        unique_values = df[col].dropna().unique()
        
        # Formatear valores únicos
        if len(unique_values) > max_unique_display:
            values_str = "; ".join(str(v) for v in unique_values[:max_unique_display]) + f"... (+{len(unique_values) - max_unique_display} más)"
        else:
            values_str = "; ".join(str(v) for v in unique_values)
        
        # Imprimir información
        print(f"📌 {col.upper()}")
        print(f"   Tipo: {dtype}")
        print(f"   Únicos: {unique_count}")
        if null_count > 0:
            print(f"   Nulos: {null_count}")
        print(f"   Valores: {values_str}")
        print()


def get_csv_summary(file_path: str) -> pd.DataFrame:
    """
    Retorna un DataFrame con resumen de columnas.
    
    Returns:
        DataFrame con columnas: [column, dtype, unique_count, unique_values]
    """
    df = pd.read_csv(file_path)
    
    summary_data = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        unique_values = "; ".join(str(v) for v in df[col].dropna().unique()[:20])
        
        summary_data.append({
            'column': col,
            'dtype': dtype,
            'unique_count': unique_count,
            'null_count': df[col].isnull().sum(),
            'unique_values': unique_values
        })
    
    return pd.DataFrame(summary_data)


if __name__ == "__main__":
    # Uso directo
    csv_path = "data/raw/02_bank.csv"
    describe_csv_columns(csv_path)
