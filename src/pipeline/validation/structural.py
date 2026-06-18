import pandas as pd
from src.utils.logger import logger


# Para el contrato
EXPECTED_COLUMNS = {
    'age': 'int64', 'job': 'object', 'marital': 'object', 'education': 'object',
    'default': 'object', 'balance': 'int64', 'housing': 'object', 'loan': 'object',
    'contact': 'object', 'day': 'int64', 'month': 'object', 'duration': 'int64',
    'campaign': 'int64', 'pdays': 'int64', 'previous': 'int64', 'poutcome': 'object',
    'deposit': 'object'
}


# validar columnas necesarias
def validar_estructura(df: pd.DataFrame) -> bool:
    logger.info("--- Iniciando Validacion Estructural ---")
    
    # ver columnas que faltans
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        logger.error(f"Falla Estructural: Faltan columnas requeridas: {missing_cols}")
        return False
        
    logger.info("Validacion estructural completada exitosamente. Todas las columnas estan presentes.")
    return True