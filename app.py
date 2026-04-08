# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 20:37:19 2026

@author: camir
"""

import streamlit as st
import pandas as pd
import sqlite3

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Encuesta Hogar", layout="wide")
st.title("Encuesta de uso del tiempo en el hogar")

# -------------------------------------------------
# DB
# -------------------------------------------------
conn = sqlite3.connect("datos.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hogar_id INTEGER,
    persona INTEGER,
    nombre TEXT,
    genero TEXT,
    limpieza REAL,
    cocinar REAL,
    cuidado REAL
)
""")
conn.commit()

# -------------------------------------------------
# LIMPIAR DB
# -------------------------------------------------
# if st.button("🗑️ Borrar base de datos"):
#     c.execute("DELETE FROM respuestas")
#     conn.commit()
#     st.success("Base de datos limpiada")

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab1, tab2 = st.tabs(["📋 Formulario", "📊 Dashboard"])

# =================================================
# FORMULARIO
# =================================================
with tab1:

    st.header("Formulario")

    # -----------------------------
    # Número de personas
    # -----------------------------
    n = st.number_input(
        "¿Cuántas personas viven en tu hogar?",
        min_value=1,
        max_value=15,
        step=1
    )

    # -----------------------------
    # Generación dinámica
    # -----------------------------
    datos = []

    for i in range(n):

        with st.expander(f"Persona {i+1}", expanded=True):

            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre", key=f"nombre_{i}")
                genero = st.selectbox(
                    "Género",
                    ["Femenino", "Masculino", "Otro"],
                    key=f"genero_{i}"
                )

            with col2:
                limpieza = st.number_input("Limpieza (h)", min_value=0.0, max_value=24.0, step=0.5, key=f"limpieza_{i}")
                cocinar = st.number_input("Cocinar (h)", min_value=0.0, max_value=24.0, step=0.5, key=f"cocinar_{i}")
                cuidado = st.number_input("Cuidado (h)", min_value=0.0, max_value=24.0, step=0.5, key=f"cuidado_{i}")

            datos.append(
                (i+1, nombre, genero, limpieza, cocinar, cuidado)
            )

    # -----------------------------
    # Guardar
    # -----------------------------
    if st.button("Guardar respuestas"):
        
        errores = []

        for i, (persona, nombre, genero, limpieza, cocinar, cuidado) in enumerate(datos):
        
            if not nombre.strip():
                errores.append(f"Persona {persona}: nombre vacío")
        
            if genero not in ["Femenino", "Masculino", "Otro"]:
                errores.append(f"Persona {persona}: género inválido")
        
            if (limpieza is None) or (cocinar is None) or (cuidado is None):
                errores.append(f"Persona {persona}: hay campos vacíos")
        
        if errores:
            st.error("Formulario incompleto:")
            for e in errores:
                st.write("-", e)
            st.stop()   # 🔴 corta la ejecución
        
        
        # Generar hogar_id automáticamente
        c.execute("SELECT MAX(hogar_id) FROM respuestas")
        max_id = c.fetchone()[0]
        hogar_id = 1 if max_id is None else max_id + 1

        datos_final = [
            (hogar_id, persona, nombre, genero, limpieza, cocinar, cuidado)
            for (persona, nombre, genero, limpieza, cocinar, cuidado) in datos
        ]

        c.executemany("""
        INSERT INTO respuestas (hogar_id, persona, nombre, genero, limpieza, cocinar, cuidado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos_final)

        conn.commit()
        st.success(f"Datos guardados para hogar {hogar_id}")

# =================================================
# DASHBOARD
# =================================================
with tab2:

    st.header("Resultados")

    df = pd.read_sql_query("SELECT * FROM respuestas", conn)

    if df.empty:
        st.warning("No hay datos aún")
    else:

        # st.dataframe(df)

        # Promedios
        st.subheader("Promedios globales")

        prom = df[["limpieza", "cocinar", "cuidado"]].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Limpieza", round(prom["limpieza"], 2))
        col2.metric("Cocinar", round(prom["cocinar"], 2))
        col3.metric("Cuidado", round(prom["cuidado"], 2))
        
        
        # ---------- TOTAL POR PERSONA
        df["total"] = df["limpieza"] + df["cocinar"] + df["cuidado"]
        st.subheader("Carga total por persona")
        st.dataframe(df[["hogar_id", "persona", "nombre", "total"]])
        st.bar_chart(df.set_index("nombre")["total"])
        
        
        # ---------- PROMEDIOS POR GÉNERO 
        genero_stats = df.groupby("genero")[["limpieza", "cocinar", "cuidado", "total"]].mean()

        st.subheader("Promedios por género")
        st.dataframe(genero_stats)
        
        st.bar_chart(genero_stats)
        
        st.subheader("Carga total por género")
        st.bar_chart(df.groupby("genero")["total"].mean())
        

        # # Comparación
        # st.subheader("Comparación por hogar")

        # hogar_sel = st.selectbox("Hogar", df["hogar_id"].unique())

        # df_hogar = df[df["hogar_id"] == hogar_sel]

        # prom_hogar = df_hogar[["limpieza", "cocinar", "cuidado"]].mean()

        # comp = pd.DataFrame({
        #     "Hogar": prom_hogar,
        #     "Global": prom
        # })

        # st.bar_chart(comp)

        # Descargar
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "datos.csv",
            "text/csv"
        )
