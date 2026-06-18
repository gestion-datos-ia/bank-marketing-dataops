import os
import pandas as pd
from sqlalchemy import create_engine
from src.config import RUTA_DATOS_PROCESSED
from src.utils.logger import logger

def ejecutar_carga():
    logger.info("Iniciando etapa de Carga (Capa Oro)...")
    
    # 1. Leer el archivo final validado de la capa plata
    ruta_entrada = RUTA_DATOS_PROCESSED / "bank_final.csv"
    if not ruta_entrada.exists():
        logger.error(f"No se encontró el archivo validado en: {ruta_entrada}")
        raise FileNotFoundError(f"Falta bank_final.csv")
        
    try:
        df = pd.read_csv(ruta_entrada)
        
        # 2. Capturar la variable de entorno de Render
        db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            raise ValueError("La variable SUPABASE_DB_URL no está configurada en el entorno.")
        
        if "ñ" in db_url:
            db_url = db_url.replace("ñ", "%C3%B1")
            
        # 3. Crear el motor de conexión a PostgreSQL
        engine = create_engine(db_url)
        
        # 4. Inyectar los 11,162 registros en bloque (Crea la tabla automáticamente)
        logger.info("Inyectando datos en Supabase... (Esto puede tardar unos segundos)")
        df.to_sql("bank_marketing_gold", con=engine, if_exists="replace", index=False)
        
        logger.info("Datos cargados exitosamente en el destino final.")
        
    except Exception as e:
        logger.error(f"Error crítico en la fase de carga a Supabase: {str(e)}")
        raise e