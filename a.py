"""
=============================================================================
CASO ESTUDIO 2 – BANK MARKETING DATASET
Fase 2: Modelado y Evaluación de Machine Learning
=============================================================================
Objetivo: Predecir la probabilidad de que un cliente suscriba un depósito a
plazo (variable 'deposit'), permitiendo al banco enfocar sus campañas de
marketing en los prospectos más prometedores.

Autor  : Ingeniero de Machine Learning
Versión: 1.0
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 0 ▸ IMPORTACIONES Y CONFIGURACIÓN DE LOGGING
# ─────────────────────────────────────────────────────────────────────────────
import logging
import hashlib
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    recall_score,
    precision_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    ConfusionMatrixDisplay,
)

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────
# Configuración del sistema de logs
# Se usa logging en lugar de print() para:
#   1) Controlar niveles de severidad (INFO / WARNING / ERROR).
#   2) Facilitar la trazabilidad en entornos de producción / CI.
#   3) Redirigir fácilmente la salida a archivos o sistemas externos (Splunk, ELK).
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                          # Consola
        logging.FileHandler("pipeline_bank.log", "w"),   # Archivo de auditoría
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 1 ▸ SEGURIDAD – ANONIMIZACIÓN DE IDENTIFICADORES SENSIBLES
# ─────────────────────────────────────────────────────────────────────────────
def anonimizar_id(valor: str) -> str:
    """
    Aplica SHA-256 a un identificador sensible (RUT, DNI, email, etc.).

    ¿Por qué SHA-256?
      • Es un hash criptográfico de sentido único: no se puede revertir sin
        fuerza bruta, lo que cumple con requisitos de privacidad (GDPR / Ley 19.628 CL).
      • Determinista: el mismo valor siempre produce el mismo hash, permitiendo
        agrupar o unir tablas sin exponer el dato original.
      • Ampliamente auditado y aceptado en entornos bancarios.

    Parámetros
    ----------
    valor : str  –  Identificador en texto plano.

    Retorna
    -------
    str  –  Hash hexadecimal de 64 caracteres.
    """
    return hashlib.sha256(str(valor).encode("utf-8")).hexdigest()


def anonimizar_columnas(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
    """
    Aplica anonimización a una lista de columnas del DataFrame.

    Parámetros
    ----------
    df       : DataFrame original.
    columnas : Lista de nombres de columna a anonimizar.

    Retorna
    -------
    DataFrame con las columnas sensibles reemplazadas por sus hashes.
    """
    try:
        df_anon = df.copy()
        for col in columnas:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].astype(str).apply(anonimizar_id)
                logger.info("Columna '%s' anonimizada correctamente.", col)
            else:
                logger.warning("Columna '%s' no encontrada; se omite.", col)
        return df_anon
    except Exception as exc:
        logger.error("Error durante la anonimización: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 2 ▸ CARGA Y GENERACIÓN DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
def cargar_o_generar_datos(ruta: str | None = None) -> pd.DataFrame:
    """
    Carga el dataset desde un CSV o genera datos sintéticos si no existe archivo.

    ¿Por qué datos sintéticos como fallback?
      • Permite desarrollar y probar el pipeline sin depender de la disponibilidad
        del archivo real, facilitando el trabajo en entornos de CI/CD.
      • Los datos sintéticos replican la distribución y cardinalidad esperadas
        del dataset UCI Bank Marketing real.

    Parámetros
    ----------
    ruta : str o None  –  Ruta al archivo CSV. Si es None, genera datos sintéticos.

    Retorna
    -------
    pd.DataFrame  –  Dataset listo para procesar.
    """
    logger.info("=== INICIO: Carga de datos ===")
    try:
        if ruta:
            df = pd.read_csv(ruta, sep=";")
            logger.info("Dataset cargado desde '%s' (%d filas, %d cols).",
                        ruta, *df.shape)
        else:
            logger.warning("No se proporcionó ruta. Generando datos sintéticos...")
            np.random.seed(42)
            n = 4_521   # Tamaño similar al dataset UCI original

            jobs = ["admin.", "technician", "services", "management",
                    "retired", "blue-collar", "unemployed", "entrepreneur",
                    "housemaid", "student", "self-employed", "unknown"]
            months = ["jan", "feb", "mar", "apr", "may", "jun",
                      "jul", "aug", "sep", "oct", "nov", "dec"]
            poutcomes = ["success", "failure", "other", "unknown"]
            contacts = ["cellular", "telephone", "unknown"]
            educations = ["primary", "secondary", "tertiary", "unknown"]
            maritals = ["married", "single", "divorced"]

            df = pd.DataFrame({
                # Identificador sintético (simula RUT/DNI)
                "client_id"  : [f"RUT-{i:05d}" for i in range(n)],
                # Datos demográficos
                "age"        : np.random.randint(18, 95, n),
                "job"        : np.random.choice(jobs, n),
                "marital"    : np.random.choice(maritals, n),
                "education"  : np.random.choice(educations, n),
                # Perfil financiero
                "default"    : np.random.choice(["yes", "no"], n, p=[0.02, 0.98]),
                "balance"    : np.random.normal(1_500, 3_000, n).astype(int),
                "housing"    : np.random.choice(["yes", "no"], n, p=[0.55, 0.45]),
                "loan"       : np.random.choice(["yes", "no"], n, p=[0.16, 0.84]),
                # Historial de contacto
                "contact"    : np.random.choice(contacts, n),
                "day"        : np.random.randint(1, 32, n),
                "month"      : np.random.choice(months, n),
                "duration"   : np.abs(np.random.normal(258, 257, n)).astype(int),
                "campaign"   : np.random.randint(1, 63, n),
                "pdays"      : np.where(np.random.rand(n) < 0.82, -1,
                                        np.random.randint(0, 871, n)),
                "previous"   : np.random.randint(0, 275, n),
                "poutcome"   : np.random.choice(poutcomes, n,
                                                p=[0.07, 0.13, 0.04, 0.76]),
                # Variable objetivo con ~11 % positivos (similar al dataset real)
                "deposit"    : np.random.choice(["yes", "no"], n, p=[0.115, 0.885]),
            })

            # Introducir ~2 % de nulos en columnas clave para demostrar manejo
            for col in ["balance", "age", "pdays"]:
                idx = np.random.choice(df.index, size=int(n * 0.02), replace=False)
                df.loc[idx, col] = np.nan

            logger.info("Datos sintéticos generados: %d filas, %d columnas.", *df.shape)

        return df

    except FileNotFoundError as exc:
        logger.error("Archivo no encontrado: %s", exc)
        raise
    except Exception as exc:
        logger.error("Error inesperado en carga de datos: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 3 ▸ PRE-PROCESAMIENTO Y FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────
def preprocesar(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray,
                                           LabelEncoder, list]:
    """
    Limpia, imputa, codifica y escala el dataset.

    Decisiones de diseño documentadas
    ──────────────────────────────────
    Manejo de nulos
      • Numéricos  → Mediana (en lugar de media):
          La mediana es robusta ante outliers, frecuentes en variables
          financieras como 'balance' o 'pdays'. La media se desplaza
          ante valores extremos, introduciendo sesgo en la imputación.
      • Categóricos → Moda:
          Al no existir un orden natural en variables como 'job' o 'education',
          la categoría más frecuente minimiza la distorsión en la distribución.

    Codificación categórica
      • LabelEncoder (ordinal) para variables binarias (yes/no).
      • LabelEncoder genérico para nominal de baja cardinalidad.
        En producción con alta cardinalidad se preferiría TargetEncoder u
        OneHotEncoder para evitar que el modelo interprete orden artificial.

    Escalado
      • StandardScaler solo para Regresión Logística, que es sensible
        a la escala de las variables. RandomForest es invariante al escalado.

    Parámetros
    ----------
    df : DataFrame con datos crudos (ya anonimizados).

    Retorna
    -------
    X_scaled : Features escaladas (para LogReg).
    y        : Vector objetivo codificado.
    le_target: Encoder para decodificar la variable objetivo.
    feature_names: Nombres de las columnas de features.
    """
    logger.info("=== INICIO: Pre-procesamiento ===")
    try:
        df = df.copy()

        # ── Eliminar columna de ID si existe (ya fue anonimizada o no aporta) ──
        id_cols = [c for c in df.columns if "id" in c.lower() or "rut" in c.lower()]
        if id_cols:
            df.drop(columns=id_cols, inplace=True)
            logger.info("Columnas de identificador eliminadas del modelo: %s", id_cols)

        # ── Separar features y target ──
        TARGET = "deposit"
        X = df.drop(columns=[TARGET])
        y_raw = df[TARGET]

        # ── Identificar tipos de columnas ──
        num_cols = X.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = X.select_dtypes(include=["object"]).columns.tolist()

        # ── IMPUTACIÓN ──
        # Numéricos: mediana → robustez ante outliers financieros
        for col in num_cols:
            mediana = X[col].median()
            nulos = X[col].isna().sum()
            X[col] = X[col].fillna(mediana)
            if nulos:
                logger.info("Imputados %d nulos en '%s' con mediana=%.2f.",
                            nulos, col, mediana)

        # Categóricos: moda → preserva la distribución nominal
        for col in cat_cols:
            moda = X[col].mode()[0]
            nulos = X[col].isna().sum()
            X[col] = X[col].fillna(moda)
            if nulos:
                logger.info("Imputados %d nulos en '%s' con moda='%s'.",
                            nulos, col, moda)

        # ── CODIFICACIÓN CATEGÓRICA ──
        le_dict = {}
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            le_dict[col] = le

        # ── CODIFICACIÓN DEL TARGET ──
        le_target = LabelEncoder()
        y = le_target.fit_transform(y_raw.astype(str))
        logger.info("Clases objetivo: %s → %s", le_target.classes_, [0, 1])

        # ── ESCALADO (StandardScaler) ──
        # Solo se aplica para Logistic Regression; guardamos también X sin escalar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        feature_names = X.columns.tolist()
        logger.info("Pre-procesamiento completado. Features: %d", len(feature_names))
        return X_scaled, X.values, y, le_target, feature_names

    except Exception as exc:
        logger.error("Error en pre-procesamiento: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 4 ▸ ENTRENAMIENTO DE MODELOS
# ─────────────────────────────────────────────────────────────────────────────
def entrenar_modelos(X_scaled, X_raw, y):
    """
    Divide los datos y entrena dos modelos con enfoques complementarios.

    Modelos seleccionados
    ─────────────────────
    1. RandomForestClassifier
       • Conjunto de árboles de decisión que promedian sus predicciones.
       • Ventajas: maneja no-linealidades, robusto ante outliers, proporciona
         importancia de variables, no requiere escalado.
       • Ideal como baseline potente en problemas de clasificación bancaria.

    2. LogisticRegression
       • Modelo lineal con función sigmoide para probabilidades.
       • Ventajas: interpretable (coeficientes = log-odds), rápido, bien
         calibrado para probabilidades, regulable con C.
       • Complementa al RF para verificar si el problema es linealmente separable
         y como referencia de complejidad mínima razonable.

    random_state=42 garantiza reproducibilidad en cada ejecución.

    Parámetros
    ----------
    X_scaled : Features escaladas (para LogReg).
    X_raw    : Features sin escalar (para RF).
    y        : Vector objetivo.

    Retorna
    -------
    dict con splits y modelos entrenados.
    """
    logger.info("=== INICIO: Entrenamiento de modelos ===")
    try:
        # ── División train/test (80/20) ──
        # Estratificación (stratify=y) preserva la proporción de clases en ambos
        # conjuntos, crítico en datasets desbalanceados como este (~11 % positivos).
        (X_tr_sc, X_te_sc,
         X_tr_rw, X_te_rw,
         y_train, y_test) = train_test_split(
            X_scaled, X_raw, y,
            test_size=0.2, random_state=42, stratify=y
        )
        logger.info("Train: %d muestras | Test: %d muestras.", len(y_train), len(y_test))

        # ── Modelo 1: Random Forest ──
        logger.info("Entrenando RandomForestClassifier...")
        rf = RandomForestClassifier(
            n_estimators=200,      # 200 árboles: buen equilibrio bias-varianza
            max_depth=10,          # Limitar profundidad evita sobreajuste
            class_weight="balanced",  # Compensa desbalance de clases automáticamente
            random_state=42,
            n_jobs=-1              # Paralelismo en todos los núcleos disponibles
        )
        rf.fit(X_tr_rw, y_train)
        logger.info("RandomForest entrenado exitosamente.")

        # ── Modelo 2: Logistic Regression ──
        logger.info("Entrenando LogisticRegression...")
        lr = LogisticRegression(
            C=1.0,                 # Regularización L2 estándar (inverso de lambda)
            max_iter=1_000,        # Iteraciones suficientes para convergencia
            class_weight="balanced",
            random_state=42
        )
        lr.fit(X_tr_sc, y_train)
        logger.info("LogisticRegression entrenada exitosamente.")

        return {
            "rf": rf, "lr": lr,
            "X_tr_rw": X_tr_rw, "X_te_rw": X_te_rw,
            "X_tr_sc": X_tr_sc, "X_te_sc": X_te_sc,
            "y_train": y_train,  "y_test": y_test,
        }

    except Exception as exc:
        logger.error("Error durante el entrenamiento: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 5 ▸ EVALUACIÓN – MÉTRICAS Y GRÁFICOS
# ─────────────────────────────────────────────────────────────────────────────
def evaluar_modelo(nombre: str, modelo, X_test, y_test,
                   le_target: LabelEncoder, ax_roc=None) -> dict:
    """
    Calcula y visualiza el conjunto completo de métricas de clasificación.

    Métricas incluidas
    ──────────────────
    • Matriz de Confusión : desglosa TP, FP, TN, FN para analizar tipos de error.
    • Accuracy            : proporción global de aciertos.
    • Precision           : de los predichos positivos, ¿cuántos lo son realmente?
    • Recall (Sensitivity): de los positivos reales, ¿cuántos detectamos?
    • F1-Score            : media armónica de Precision y Recall; útil con clases
                            desbalanceadas donde Accuracy puede ser engañosa.
    • AUC-ROC             : capacidad del modelo para discriminar entre clases.
                            Independiente del umbral de decisión.
    • Coeficiente Gini    : Gini = 2·AUC − 1. Métrica estándar en scoring bancario;
                            0 = modelo aleatorio, 1 = modelo perfecto.

    Parámetros
    ----------
    nombre    : Nombre descriptivo del modelo.
    modelo    : Modelo sklearn entrenado.
    X_test    : Features de evaluación.
    y_test    : Etiquetas reales.
    le_target : Encoder de la clase objetivo.
    ax_roc    : Eje matplotlib para la curva ROC (opcional).

    Retorna
    -------
    dict con todas las métricas calculadas.
    """
    logger.info("--- Evaluando: %s ---", nombre)
    try:
        y_pred  = modelo.predict(X_test)
        y_proba = modelo.predict_proba(X_test)[:, 1]  # P(deposit=yes)

        # ── Métricas escalares ──
        acc  = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score(y_test, y_pred, zero_division=0)
        f1   = f1_score(y_test, y_pred, zero_division=0)
        auc  = roc_auc_score(y_test, y_proba)
        gini = 2 * auc - 1   # Coeficiente de Gini: estándar en banca para scoring

        # ── Imprimir resumen ──
        separador = "─" * 50
        print(f"\n{separador}")
        print(f"  MODELO: {nombre}")
        print(separador)
        print(f"  Accuracy  : {acc:.4f}")
        print(f"  Precision : {prec:.4f}")
        print(f"  Recall    : {rec:.4f}")
        print(f"  F1-Score  : {f1:.4f}")
        print(f"  AUC-ROC   : {auc:.4f}")
        print(f"  Gini Coef.: {gini:.4f}")
        print(separador)

        # ── Matriz de Confusión ──
        cm = confusion_matrix(y_test, y_pred)
        fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=le_target.classes_
        )
        disp.plot(ax=ax_cm, colorbar=False, cmap="Blues")
        ax_cm.set_title(f"Matriz de Confusión – {nombre}", fontsize=12, pad=10)
        plt.tight_layout()
        fname_cm = f"confusion_matrix_{nombre.replace(' ', '_')}.png"
        fig_cm.savefig(fname_cm, dpi=150)
        plt.show()
        logger.info("Matriz de confusión guardada como '%s'.", fname_cm)

        # ── Curva ROC ──
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        if ax_roc is not None:
            ax_roc.plot(fpr, tpr, lw=2,
                        label=f"{nombre} (AUC={auc:.3f} | Gini={gini:.3f})")

        logger.info("%s evaluado: AUC=%.4f | Gini=%.4f", nombre, auc, gini)

        return {
            "nombre": nombre, "accuracy": acc, "precision": prec,
            "recall": rec, "f1": f1, "auc": auc, "gini": gini,
            "y_pred": y_pred, "y_proba": y_proba,
        }

    except Exception as exc:
        logger.error("Error evaluando %s: %s", nombre, exc)
        raise


def graficar_roc_comparativa(resultados: list, y_test):
    """
    Genera una figura con las curvas ROC de todos los modelos superpuestas.

    La curva ROC muestra el trade-off entre Tasa de Verdaderos Positivos (TPR)
    y Tasa de Falsos Positivos (FPR) para todos los umbrales posibles.
    Superponer los modelos permite seleccionar el mejor discriminador de forma
    visual y cuantitativa.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    for res in resultados:
        fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
        ax.plot(fpr, tpr, lw=2,
                label=f"{res['nombre']} (AUC={res['auc']:.3f} | Gini={res['gini']:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Clasificador aleatorio (AUC=0.5)")
    ax.set_xlabel("Tasa de Falsos Positivos (FPR)", fontsize=11)
    ax.set_ylabel("Tasa de Verdaderos Positivos (TPR)", fontsize=11)
    ax.set_title("Curvas ROC – Comparativa de Modelos\nBank Marketing Dataset",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("roc_comparativa.png", dpi=150)
    plt.show()
    logger.info("Curva ROC comparativa guardada como 'roc_comparativa.png'.")


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 6 ▸ IMPORTANCIA DE VARIABLES (RandomForest)
# ─────────────────────────────────────────────────────────────────────────────
def graficar_importancia(rf_model, feature_names: list, top_n: int = 15):
    """
    Visualiza las variables más relevantes según el RandomForest.

    La importancia se basa en la reducción media de impureza (Gini Importance)
    en cada árbol del bosque. Variables con mayor importancia tienen mayor
    poder predictivo en el modelo de ensemble.

    Valor de negocio: permite al equipo de marketing priorizar segmentos de
    clientes basándose en variables objetivas (ej.: duración de llamada, saldo).
    """
    try:
        importancias = pd.Series(rf_model.feature_importances_, index=feature_names)
        top = importancias.nlargest(top_n).sort_values()

        fig, ax = plt.subplots(figsize=(8, 6))
        top.plot(kind="barh", ax=ax, color="steelblue", edgecolor="white")
        ax.set_title(f"Top {top_n} Variables – Importancia (RandomForest)",
                     fontsize=12, fontweight="bold")
        ax.set_xlabel("Importancia (Gini)")
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        plt.savefig("importancia_variables.png", dpi=150)
        plt.show()
        logger.info("Gráfico de importancia guardado como 'importancia_variables.png'.")
    except Exception as exc:
        logger.warning("No se pudo graficar importancia de variables: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 7 ▸ INTEGRACIÓN BI – EXPORTACIÓN DE RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────
def exportar_resultados_bi(df_test_original: pd.DataFrame,
                           y_test: np.ndarray,
                           y_pred: np.ndarray,
                           y_proba: np.ndarray,
                           le_target: LabelEncoder,
                           nombre_modelo: str = "RandomForest") -> pd.DataFrame:
    """
    Genera 'resultados_modelo.csv' consumible por Power BI o Metabase.

    Estructura del CSV
    ──────────────────
    • Todas las columnas del conjunto de prueba (datos originales).
    • 'target_real'        : etiqueta real decodificada ('yes'/'no').
    • 'prediccion'         : predicción del modelo decodificada.
    • 'prob_suscripcion'   : P(deposit='yes') → para scoring y ranking.
    • 'modelo'             : nombre del modelo usado.
    • 'segmento_riesgo'    : clasificación en tres segmentos según probabilidad,
                              útil para priorizar llamadas en la campaña.

    ¿Por qué exportar probabilidades y no solo predicciones?
      Las probabilidades permiten al equipo de BI ordenar clientes por
      propensión de compra y definir umbrales de campaña dinámicamente,
      maximizando el ROI según el presupuesto disponible.

    Parámetros
    ----------
    df_test_original : Porción de test del DataFrame original (antes de codificar).
    y_test           : Etiquetas reales codificadas.
    y_pred           : Predicciones codificadas.
    y_proba          : Probabilidades P(clase=1).
    le_target        : Encoder para decodificar etiquetas.
    nombre_modelo    : Etiqueta del modelo para trazabilidad.

    Retorna
    -------
    DataFrame exportado.
    """
    logger.info("=== INICIO: Exportación BI ===")
    try:
        df_out = df_test_original.reset_index(drop=True).copy()
        df_out["target_real"]      = le_target.inverse_transform(y_test)
        df_out["prediccion"]       = le_target.inverse_transform(y_pred)
        df_out["prob_suscripcion"] = np.round(y_proba, 4)
        df_out["modelo"]           = nombre_modelo

        # Segmentación por probabilidad → facilita decisiones de campaña en BI
        df_out["segmento_riesgo"] = pd.cut(
            df_out["prob_suscripcion"],
            bins=[0, 0.3, 0.6, 1.0],
            labels=["Bajo", "Medio", "Alto"],
            include_lowest=True
        )

        nombre_csv = "resultados_modelo.csv"
        df_out.to_csv(nombre_csv, index=False, encoding="utf-8-sig")
        logger.info("Resultados exportados a '%s' (%d filas).", nombre_csv, len(df_out))

        # Resumen de segmentos para el log
        resumen = df_out["segmento_riesgo"].value_counts()
        logger.info("Distribución de segmentos:\n%s", resumen.to_string())

        return df_out

    except Exception as exc:
        logger.error("Error al exportar resultados: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE 8 ▸ PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def main(ruta_csv: str | None = None):
    """
    Orquesta todo el pipeline de ML end-to-end.

    Flujo
    ─────
    1. Carga de datos.
    2. Anonimización de IDs sensibles.
    3. Pre-procesamiento (imputación, codificación, escalado).
    4. División y entrenamiento de modelos.
    5. Evaluación con métricas completas y gráficos.
    6. Exportación de resultados para BI.
    """
    logger.info("╔══════════════════════════════════════════════════╗")
    logger.info("║  PIPELINE BANK MARKETING – FASE 2 ML             ║")
    logger.info("╚══════════════════════════════════════════════════╝")

    # ── PASO 1: Carga ──
    df = cargar_o_generar_datos(ruta_csv)

    # ── PASO 2: Anonimización ──
    # Se anonimiza 'client_id' (simula RUT/DNI) antes de cualquier procesamiento.
    columnas_sensibles = ["client_id", "rut", "dni"]
    df = anonimizar_columnas(df, columnas_sensibles)

    # Guardar copia del test original (antes de codificar) para BI
    df_original = df.copy()

    # ── PASO 3: Pre-procesamiento ──
    X_scaled, X_raw, y, le_target, feature_names = preprocesar(df)

    # ── PASO 4: Entrenamiento ──
    splits = entrenar_modelos(X_scaled, X_raw, y)

    # ── PASO 5: Evaluación ──
    resultados = []

    # Evaluar RandomForest (usa features sin escalar)
    res_rf = evaluar_modelo(
        nombre="Random Forest",
        modelo=splits["rf"],
        X_test=splits["X_te_rw"],
        y_test=splits["y_test"],
        le_target=le_target,
    )
    resultados.append(res_rf)

    # Evaluar Logistic Regression (usa features escaladas)
    res_lr = evaluar_modelo(
        nombre="Logistic Regression",
        modelo=splits["lr"],
        X_test=splits["X_te_sc"],
        y_test=splits["y_test"],
        le_target=le_target,
    )
    resultados.append(res_lr)

    # Curva ROC comparativa
    graficar_roc_comparativa(resultados, splits["y_test"])

    # Importancia de variables (solo RandomForest la provee directamente)
    graficar_importancia(splits["rf"], feature_names)

    # ── PASO 6: Exportación BI ──
    # Se usa el mejor modelo (RF en este caso) para el CSV final.
    # El índice del test se obtiene de train_test_split.
    _, test_idx = train_test_split(
        np.arange(len(y)), test_size=0.2, random_state=42, stratify=y
    )
    df_test_original = df_original.iloc[test_idx].reset_index(drop=True)

    exportar_resultados_bi(
        df_test_original=df_test_original,
        y_test=splits["y_test"],
        y_pred=res_rf["y_pred"],
        y_proba=res_rf["y_proba"],
        le_target=le_target,
        nombre_modelo="RandomForest",
    )

    # ── Tabla resumen comparativa ──
    tabla = pd.DataFrame([
        {k: v for k, v in r.items() if k not in ("y_pred", "y_proba")}
        for r in resultados
    ]).set_index("nombre").round(4)

    print("\n" + "═" * 60)
    print("  COMPARATIVA FINAL DE MODELOS")
    print("═" * 60)
    print(tabla.to_string())
    print("═" * 60)

    mejor = tabla["f1"].idxmax()
    logger.info("Modelo con mejor F1-Score: %s (F1=%.4f)", mejor, tabla.loc[mejor, "f1"])
    logger.info("Pipeline completado exitosamente.")

    return tabla


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Para usar con el dataset real descargado de UCI:
    #   main(ruta_csv="bank-full.csv")
    # Sin argumento → genera datos sintéticos (modo demo/CI):
    main()