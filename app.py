import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crecimiento de Ingresos", layout="wide")
st.title("📈 Análisis de crecimiento de ingresos por empresa")

# Buscar archivos en la carpeta /analisis
ARCHIVO_DIR = "analisis"
archivos = sorted([
    f for f in os.listdir(ARCHIVO_DIR)
    if f.startswith("crecimiento_") and f.endswith(".csv")
])

if not archivos:
    st.warning("No hay análisis disponibles aún. Ejecuta el script de análisis para generar resultados.")
else:
    # Obtener lista de fechas disponibles
    fechas_disponibles = [f.replace("crecimiento_", "").replace(".csv", "") for f in archivos]

    # Seleccionar la fecha más reciente por defecto
    fecha_seleccionada = st.selectbox(
        "Selecciona la fecha del análisis:",
        fechas_disponibles[::-1],
        index=0
    )

    ruta = os.path.join(ARCHIVO_DIR, f"crecimiento_{fecha_seleccionada}.csv")
    df = pd.read_csv(ruta)

    st.success(f"📅 Mostrando resultados del {fecha_seleccionada}")
    st.dataframe(df, use_container_width=True)

    # Extra: permitir descarga
    st.download_button(
        label="📥 Descargar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"crecimiento_{fecha_seleccionada}.csv",
        mime="text/csv"
    )


st.markdown("---")
st.subheader("📉 Evolución histórica por empresa")

# Buscar archivos por empresa
empresa_files = sorted([
    f for f in os.listdir("empresa_data") if f.endswith(".csv")
])

if not empresa_files:
    st.warning("No hay datos históricos de empresas disponibles.")
else:
    empresa_seleccionada = st.selectbox(
        "Selecciona una empresa para ver su evolución:",
        [f.replace(".csv", "") for f in empresa_files]
    )

    df_empresa = pd.read_csv(f"empresa_data/{empresa_seleccionada}.csv")

    # Mostrar qué columnas están disponibles
    columnas_disponibles = [col for col in df_empresa.columns if col != "Fecha"]

    instrumento = st.selectbox(
        "Selecciona el instrumento a visualizar:",
        columnas_disponibles,
        index=0
    )

    # Limpiar y ordenar por fecha
    df_empresa["Fecha"] = pd.to_datetime(df_empresa["Fecha"])
    df_empresa = df_empresa.sort_values("Fecha")

    # Mostrar gráfico
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_empresa["Fecha"], df_empresa[instrumento], marker='o')
    ax.set_title(f"{instrumento} - {empresa_seleccionada}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel(instrumento)
    ax.grid(True)

    st.pyplot(fig)
