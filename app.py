import streamlit as st
import sqlite3
from datetime import datetime

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Petto",
    layout="wide"
)

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "petto.db",
    check_same_thread=False
)

c = conn.cursor()

# Tabla adopciones
c.execute("""
CREATE TABLE IF NOT EXISTS adopciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    familia TEXT,
    mascota TEXT,
    fecha TEXT,
    estado TEXT
)
""")

# Tabla checkins
c.execute("""
CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adopcion_id INTEGER,
    fecha TEXT,
    bienestar INTEGER,
    comportamiento TEXT,
    notas TEXT
)
""")

conn.commit()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("🐾 Petto")

page = st.sidebar.radio(
    "Navegación",
    [
        "Dashboard",
        "Nueva adopción",
        "Check-in"
    ]
)

# =========================
# HEADER
# =========================

st.title("🐶 Petto")
st.caption("Seguimiento post-adopción")

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.subheader("Adopciones registradas")

    rows = c.execute("""
        SELECT familia, mascota, fecha, estado
        FROM adopciones
        ORDER BY id DESC
    """).fetchall()

    if rows:

        for row in rows:

            with st.container(border=True):

                st.write(f"**Familia:** {row[0]}")
                st.write(f"**Mascota:** {row[1]}")
                st.write(f"**Fecha:** {row[2]}")
                st.write(f"**Estado:** {row[3]}")

    else:
        st.info("Todavía no hay adopciones registradas.")

# =========================
# NUEVA ADOPCIÓN
# =========================

if page == "Nueva adopción":

    st.subheader("Registrar nueva adopción")

    with st.form("adopcion_form"):

        familia = st.text_input("Nombre de la familia")

        mascota = st.text_input("Nombre de la mascota")

        fecha = st.date_input("Fecha de adopción")

        estado = st.selectbox(
            "Estado",
            [
                "Primeros 7 días",
                "Seguimiento 30 días",
                "Seguimiento 90 días"
            ]
        )

        submitted = st.form_submit_button(
            "Guardar adopción"
        )

        if submitted:

            c.execute("""
                INSERT INTO adopciones (
                    familia,
                    mascota,
                    fecha,
                    estado
                )
                VALUES (?, ?, ?, ?)
            """, (
                familia,
                mascota,
                str(fecha),
                estado
            ))

            conn.commit()

            st.success(
                "Adopción registrada correctamente"
            )

# =========================
# CHECK-IN
# =========================

if page == "Check-in":

    st.subheader("Registrar seguimiento")

    adopciones = c.execute("""
        SELECT id, familia, mascota
        FROM adopciones
        ORDER BY id DESC
    """).fetchall()

    if not adopciones:

        st.warning(
            "Primero debes crear una adopción"
        )

    else:

        options = {
            f"{a[1]} · {a[2]}": a[0]
            for a in adopciones
        }

        selected = st.selectbox(
            "Selecciona una adopción",
            list(options.keys())
        )

        adopcion_id = options[selected]

        with st.form("checkin_form"):

            bienestar = st.slider(
                "Nivel de bienestar",
                1,
                5,
                3
            )

            comportamiento = st.selectbox(
                "Comportamiento observado",
                [
                    "Adaptación positiva",
                    "Ansiedad",
                    "Miedo",
                    "Destrucción de objetos",
                    "Problemas de convivencia",
                    "Otro"
                ]
            )

            notas = st.text_area(
                "Notas del seguimiento"
            )

            submitted = st.form_submit_button(
                "Guardar check-in"
            )

            if submitted:

                c.execute("""
                    INSERT INTO checkins (
                        adopcion_id,
                        fecha,
                        bienestar,
                        comportamiento,
                        notas
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    adopcion_id,
                    str(datetime.now()),
                    bienestar,
                    comportamiento,
                    notas
                ))

                conn.commit()

                st.success(
                    "Check-in guardado"
                )

        st.divider()

        st.subheader("Historial")

        history = c.execute("""
            SELECT
                fecha,
                bienestar,
                comportamiento,
                notas
            FROM checkins
            WHERE adopcion_id = ?
            ORDER BY id DESC
        """, (adopcion_id,)).fetchall()

        if history:

            for h in history:

                with st.container(border=True):

                    st.write(f"**Fecha:** {h[0]}")
                    st.write(f"**Bienestar:** {h[1]}/5")
                    st.write(f"**Comportamiento:** {h[2]}")
                    st.write(f"**Notas:** {h[3]}")

        else:

            st.info(
                "Todavía no hay check-ins."
            )
```
