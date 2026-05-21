from src.config import RUTA_DATOS_PROCESSED
from src.utils.logger import logger

def ejecutar_limpieza():
    logger.info("Iniciando etapa de Limpieza y Transformación (Capa Plata)...")

    # TODO: Benjamin: Aqui va el codigo

    logger.info("Proceso de limpieza completado.")

    # En caso de error, se puede usar:
    # logger.error("Mensaje de error detallado")
    # pero para eso debes crear una condicion que detecte el error
    # y asi no se imprima un falso exito de limpieza de datos