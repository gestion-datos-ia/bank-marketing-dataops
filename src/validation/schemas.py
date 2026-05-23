import pandas as pd
import os
from src.utils.logger import logger
from src.validation.structural import validar_estructura
from src.validation.semantic import validar_semantica


def ejecutar_validacion(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    logger.info("=============================================================")
    logger.info("Iniciando validacion estructural y semantica de los datos...")
    logger.info("=============================================================")


    # Validacion estructural
    estructura_ok = validar_estructura(df)
    if not estructura_ok:
        logger.error("La validacion estructural fallo. Deteniendo proceso.")
        return pd.DataFrame(columns=df.columns), df
    
    
    
    # Validacion semantica
    mascara_validos = validar_semantica(df)
    
    # Separacion de datos validos e invalidos
    df_validos = df[mascara_validos].copy()
    df_invalidos = df[~mascara_validos].copy()
    
    
    # Logs para cerrar procesos
    logger.info("Proceso de validacion finalizado.")
    logger.info(f" -> Registros Totales Evaluados: {len(df)}")
    logger.info(f" -> Registros VALIDOS (pasan al modelo): {len(df_validos)}")
    logger.info(f" -> Registros INVALIDOS (enviados a cuarentena): {len(df_invalidos)}")
    
    
    return df_validos, df_invalidos