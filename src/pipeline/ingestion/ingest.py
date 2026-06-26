import pandas as pd
from src.config import RUTA_DATOS_RAW
from src.utils.logger import logger

def ejecutar_ingesta():
    logger.info("Iniciando etapa de ingesta (capa bronce)...")
    
    # Usamos RUTA_DATOS_RAW de config.py para saber exactamente dónde está el archivo
    ruta_archivo = RUTA_DATOS_RAW / "02_bank.csv"
    
    if not ruta_archivo.exists():
        logger.error(f"No se encontró el archivo en la ruta: {ruta_archivo}")
        raise FileNotFoundError(f"Falta el archivo requerido en: {ruta_archivo}")
        
    try:

        df = pd.read_csv(ruta_archivo)

        if df.empty:
            logger.warning(f"El archivo {ruta_archivo} está vacío. No se cargaron datos.")
            raise ValueError(f"Archivo vacío: {ruta_archivo}")
        
        logger.info(f"Lectura exitosa. Registros detectados: {len(df)} | Columnas: {df.shape[1]}")
        logger.info("Ingesta completada de forma exitosa")

        return df
        
    except Exception as e:
        logger.error(f"Error crítico al procesar el archivo en ingesta: {str(e)}")
        raise e