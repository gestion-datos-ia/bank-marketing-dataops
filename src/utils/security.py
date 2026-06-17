import hashlib
from src.utils.logger import logger

def anonimizar_columna(df, columna):
    """
    Anonimiza datos sensibles mediante hashing SHA-256.
    Cumple con el principio de minimización de datos (Ley Chilena).
    """
    if columna in df.columns:
        logger.info(f"Aplicando anonimización SHA-256 a la columna: {columna}")
        df[columna] = df[columna].apply(
            lambda x: hashlib.sha256(str(x).encode()).hexdigest()
        )
        return df
    else:
        logger.warning(f"La columna {columna} no existe, no se pudo anonimizar.")
        return df