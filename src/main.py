from src.utils.logger import logger
from src.ingestion.ingest import ejecutar_ingesta
from src.processing.transform import ejecutar_limpieza
from src.validation.schemas import ejecutar_validacion
from src.loading.load import ejecutar_carga

def ejecutar_pipeline_completo():
    logger.info("=== ARRANCANDO PIPELINE DATAOPS (BANK MARKETING) ===")
    
    try:
        ejecutar_ingesta()      
        ejecutar_limpieza()     
        ejecutar_validacion()   
        ejecutar_carga()       
        
        logger.success("=== PIPELINE EJECUTADO EXITOSAMENTE SIN ERRORES ===")
        
    except Exception as e:
        logger.critical(f"El pipeline colapsó debido a un error inesperado: {str(e)}")

if __name__ == "__main__":
    ejecutar_pipeline_completo()