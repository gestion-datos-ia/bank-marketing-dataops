import pandas as pd
from src.config import RUTA_DATOS_RAW, RUTA_DATOS_PROCESSED
from src.utils.logger import logger

def ejecutar_limpieza():
    logger.info("Iniciando etapa de Limpieza y Transformación (Capa Plata)...")
    
    ruta_entrada = RUTA_DATOS_RAW / "02_bank.csv"
    ruta_salida = RUTA_DATOS_PROCESSED / "bank_processed.csv"
    
    # Control de anomalías: verificar que la ingesta previa dejó el archivo listo
    if not ruta_entrada.exists():
        logger.error(f"No se encontró el archivo crudo en la ruta: {ruta_entrada}")
        raise FileNotFoundError(f"Falta el archivo raw requerido en: {ruta_entrada}")
        
    try:
        # 1. Cargar datos desde la Capa Bronce
        df = pd.read_csv(ruta_entrada)
        filas_originales = len(df)
        
        # 2. Control de duplicados (Higiene de datos básica)
        df = df.drop_duplicates()
        filas_sin_duplicados = len(df)
        
        # 3. Transformación de variables binarias (Mapeo de 'yes'/'no' a 1/0)
        # Esto prepara las columnas financieras y el target para el modelo de ML
        columnas_binarias = ['default', 'housing', 'loan', 'deposit']
        for col in columnas_binarias:
            if col in df.columns:
                df[col] = df[col].map({'yes': 1, 'no': 0})
        
        # 4. Guardar datos transformados e inmutables en la Capa Plata
        df.to_csv(ruta_salida, index=False)
        
        # Logs informativos para la auditoría de DataOps
        logger.info(f"Registros procesados: {filas_originales} -> Sin duplicados: {filas_sin_duplicados}")
        logger.info(f"Variables binarias transformadas de forma exitosa: {columnas_binarias}")
        logger.info(f"Archivo limpio guardado con éxito en: {ruta_salida}")
        logger.info("Proceso de limpieza completado.")
        
    except Exception as e:
        logger.error(f"Error crítico en la fase de transformación de datos: {str(e)}")
        raise e