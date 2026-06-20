import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.utils.logger import logger
from src.pipeline.ingestion.ingest import ejecutar_ingesta
from src.pipeline.processing.transform import ejecutar_limpieza
from src.pipeline.validation.schemas import ejecutar_validacion
from src.pipeline.loading.load import ejecutar_carga

class RenderFreeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/run":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Ejecutando pipeline en segundo plano... Revisa los logs en Render.".encode("utf-8"))
            
            # Corre el pipeline en un hilo separado para evitar el timeout de Render
            threading.Thread(target=ejecutar_pipeline_completo).start()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Servicio DataOps Activo. Ve a /run para activar el pipeline gratis.".encode("utf-8"))

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

def iniciar_servidor():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), RenderFreeHandler)
    logger.info(f"Servidor activo para Render Free en el puerto {port}")
    server.serve_forever()

if __name__ == "__main__":
    iniciar_servidor()