from src.config import RUTA_DATOS_RAW
from src.utils.logger import logger

def ejecutar_ingesta():
    logger.info("Iniciando etapa  de ingesta (capa bronce)...")

    # TODO: Benjamin: Aqui va el codigo (si si se que sabes)

    logger.info("Ingesta completada de forma exitosa")

    # En caso de error, se puede usar:
    # logger.error("Mensaje de error detallado")
    # pero para eso debes crear una condicion que detecte el error
    # y asi no se imprima un falso exito de ingesta