import pandas as pd
from src.utils.logger import logger


# Para aplicar las reglas de negocio
def validar_semantica(df: pd.DataFrame) -> pd.Series:
    logger.info("--- Iniciando Validación Semántica (Reglas de Negocio) ---")
    
    
    # Regla 1: Rango de edad logico para contratos
    regla_edad = (df['age'] >= 18) & (df['age'] <= 100)
    
    
    # Regla 2: Coherencia de calendario y fechas
    regla_dias = (df['day'] >= 1) & (df['day'] <= 31)
    meses_validos = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    regla_mes = df['month'].str.lower().isin(meses_validos)
    
    
    # Regla 3: Metricas operacionales coherentes
    regla_duracion = df['duration'] >= 0
    regla_campaign = df['campaign'] >= 1
    
    
    # Regla 4: Consistencia en el historial de campañas
    # Si pdays es -1 (primer contacto), 'previous' debe ser necesariamente 0
    regla_historial = ~((df['pdays'] == -1) & (df['previous'] > 0))
    
    
    # Regla 5: Restriccion de valores en variables de respuesta binaria
    valores_binarios = ['yes', 'no']
    regla_binarias = (
        df['default'].str.lower().isin(valores_binarios) &
        df['housing'].str.lower().isin(valores_binarios) &
        df['loan'].str.lower().isin(valores_binarios) &
        df['deposit'].str.lower().isin(valores_binarios)
    )
    
    
    # Unificacion de todas las reglas para validar filas
    filas_validas = regla_edad & regla_dias & regla_mes & regla_duracion & regla_campaign & regla_historial & regla_binarias
    
    
    # Reporte de anomalias para logs
    total_filas = len(df)
    
    if not regla_edad.all():
        logger.warning(f"Negocio: {total_filas - regla_edad.sum()} registros presentan edades fuera del rango [18-100].")
    if not regla_historial.all():
        logger.warning(f"Negocio: {total_filas - regla_historial.sum()} registros tienen inconsistencia entre 'pdays=-1' y 'previous > 0'.")
    if not regla_binarias.all():
        logger.warning(f"Negocio: {total_filas - regla_binarias.sum()} registros contienen respuestas binarias distintas a 'yes'/'no'.")
        
    return filas_validas