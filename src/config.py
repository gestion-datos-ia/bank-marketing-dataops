from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno si existiera un archivo .env
load_dotenv()

PROYECTO_RAIZ = Path(__file__).parents[1].resolve()

# Definir rutas estándar para el proyecto
RUTA_DATOS_RAW = PROYECTO_RAIZ / "data" / "raw"
RUTA_DATOS_PROCESSED = PROYECTO_RAIZ / "data" / "processed"

RUTA_LOGS = PROYECTO_RAIZ / "logs"

# Asegurar que las carpetas existan físicamente en el disco duro al arrancar
# Recomendacion de IA
RUTA_DATOS_RAW.mkdir(parents=True, exist_ok=True)
RUTA_DATOS_PROCESSED.mkdir(parents=True, exist_ok=True)
RUTA_LOGS.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Test rápido de verificación de infraestructura
    print(f"--- VERIFICACIÓN DE RUTAS ---")
    print(f"Raíz Proyecto: {PROYECTO_RAIZ}")
    print(f"Zona Bronce (Raw): {RUTA_DATOS_RAW}")
    print(f"Zona Plata (Processed): {RUTA_DATOS_PROCESSED}")
    print(f"Zona Alertas/Logs: {RUTA_LOGS}")





















""" from pathlib import Path

p = Path(__file__).parents[1]

p_absoluta = p.resolve()

path_raw = p_absoluta / "data" / "raw"
path_processed = p_absoluta / "data" / "processed"

print(f"Raw data path: {path_raw}")
print(f"Processed data path: {path_processed}") """