import pandas as pd
from src.config import RUTA_DATOS_RAW
from src.utils.logger import logger

def ejecutar_ingesta():
    logger.info("Iniciando etapa de ingesta (capa bronce)...")
    
    # Usamos RUTA_DATOS_RAW de config.py para saber exactamente dónde está el archivo
    ruta_archivo = RUTA_DATOS_RAW / "02_bank.csv"
    
    # Verificación: Si no está el archivo, cortamos el proceso con un error claro
    if not ruta_archivo.exists():
        logger.error(f"No se encontró el archivo en la ruta: {ruta_archivo}")
        raise FileNotFoundError(f"Falta el archivo requerido en: {ruta_archivo}")
        
    try:
        # Leemos el archivo para validar que los datos están ahí
        df = pd.read_csv(ruta_archivo)
        
        # Log de control para ver que todo cuadre (11162 filas, 17 columnas)
        logger.info(f"Lectura exitosa. Registros detectados: {len(df)} | Columnas: {df.shape[1]}")
        logger.info("Ingesta completada de forma exitosa")
        
    except Exception as e:
        logger.error(f"Error crítico al procesar el archivo en ingesta: {str(e)}")
        raise e