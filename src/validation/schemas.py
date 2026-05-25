import pandas as pd
from src.config import RUTA_DATOS_PROCESSED
from src.utils.logger import logger
from src.validation.structural import validar_estructura
from src.validation.semantic import validar_semantica

def ejecutar_validacion(df: pd.DataFrame = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("=============================================================")
    logger.info("Iniciando validacion estructural y semantica de los datos...")
    logger.info("=============================================================")

    # Si no viene un DataFrame por parámetro (como pasa en tu main.py), lo leemos de la capa plata
    if df is None:
        ruta_plata = RUTA_DATOS_PROCESSED / "bank_processed.csv"
        if not ruta_plata.exists():
            error_msg = f"Fallo de flujo: No se encontró el archivo procesado en {ruta_plata}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        df = pd.read_csv(ruta_plata)

    # Validación estructural
    estructura_ok = validar_estructura(df)
    if not estructura_ok:
        logger.error("La validacion estructural fallo. Deteniendo proceso.")
        raise ValueError("Fallo crítico en la validación estructural del esquema.")
    
    # Validación semántica
    mascara_validos = validar_semantica(df)
    
    # Separación de datos válidos e inválidos
    df_validos = df[mascara_validos].copy()
    df_invalidos = df[~mascara_validos].copy()
    
    # PERSISTENCIA: Guardamos el set final aprobado y la cuarentena (si existiese)
    df_validos.to_csv(RUTA_DATOS_PROCESSED / "bank_final.csv", index=False)
    if not df_invalidos.empty:
        df_invalidos.to_csv(RUTA_DATOS_PROCESSED / "cuarentena.csv", index=False)
    
    # Logs para cerrar procesos
    logger.info("Proceso de validacion finalizado.")
    logger.info(f" -> Registros Totales Evaluados: {len(df)}")
    logger.info(f" -> Registros VALIDOS (pasan al modelo): {len(df_validos)}")
    logger.info(f" -> Registros INVALIDOS (enviados a cuarentena): {len(df_invalidos)}")
    
    return df_validos, df_invalidos