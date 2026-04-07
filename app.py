# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 20:37:19 2026

@author: camir
"""

import streamlit as st
import pandas as pd

st.title("Encuesta del hogar")

# -------------------------
# Pregunta inicial
# -------------------------
n = st.number_input(
    "¿Cuántas personas viven en tu hogar?",
    min_value=1,
    max_value=15,
    step=1
)

# -------------------------
# Lista para guardar datos
# -------------------------
datos = []

# -------------------------
# Generación dinámica
# -------------------------
for i in range(n):

    st.subheader(f"Persona {i+1}")

    nombre = st.text_input("Nombre", key=f"nombre_{i}")
    genero = st.selectbox("Género", ["Femenino", "Masculino", "Otro"], key=f"genero_{i}")

    limpieza = st.number_input("Horas limpieza", min_value=0.0, key=f"limpieza_{i}")
    cocinar = st.number_input("Horas cocinar", min_value=0.0, key=f"cocinar_{i}")
    cuidado = st.number_input("Horas cuidado", min_value=0.0, key=f"cuidado_{i}")

    datos.append({
        "persona": i+1,
        "nombre": nombre,
        "genero": genero,
        "limpieza": limpieza,
        "cocinar": cocinar,
        "cuidado": cuidado
    })

# -------------------------
# Botón para exportar
# -------------------------
if st.button("Descargar CSV"):
    df = pd.DataFrame(datos)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Click para descargar",
        csv,
        "datos.csv",
        "text/csv"
    )