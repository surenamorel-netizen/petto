import streamlit as st
import sqlite3
from datetime import datetime

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    ADOPTION_STAGES,
    BEHAVIOR_OPTIONS,
    WELLBEING_MIN,
    WELLBEING_MAX
)

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

conn = sqlite3.connect(
    "/tmp/petto.db",
    check_same_thread=False
)

c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS adopciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    familia TEXT,
    mascota TEXT,
    fecha TEXT,
    estado TEXT
)
""")

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

st.sidebar.title("🐾 Petto")

page = st.sidebar.radio(
    "Navegación",
    [
        "Dashboard",
        "Nueva adopción",
        "Check-in",
        "Alertas",
        "Biblioteca"
    ]
)

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

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

        familia = st.text_input(
            "Nombre de la familia"
        )

        mascota = st.text_input(
            "Nombre de la mascota"
        )

        fecha = st.date_input(
            "Fecha de adopción"
        )

        estado = st.selectbox(
            "Estado",
            ADOPTION_STAGES
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
                WELLBEING_MIN,
                WELLBEING_MAX,
                3
            )

            comportamiento = st.selectbox(
                "Comportamiento observado",
                BEHAVIOR_OPTIONS
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

# =========================
# ALERTAS
# =========================

if page == "Alertas":

    st.subheader("⚠️ Casos con riesgo")

    alerts = c.execute("""
        SELECT
            adopciones.familia,
            adopciones.mascota,
            checkins.bienestar,
            checkins.comportamiento,
            checkins.notas
        FROM checkins
        JOIN adopciones
        ON adopciones.id = checkins.adopcion_id
        WHERE checkins.bienestar <= 2
        ORDER BY checkins.id DESC
    """).fetchall()

    if alerts:

        for a in alerts:

            with st.container(border=True):

                st.error(
                    f"{a[1]} requiere atención"
                )

                st.write(f"**Familia:** {a[0]}")
                st.write(f"**Bienestar:** {a[2]}/5")
                st.write(f"**Problema:** {a[3]}")
                st.write(f"**Notas:** {a[4]}")

    else:

        st.success(
            "No hay alertas activas"
        )

# =========================
# BIBLIOTECA
# =========================

if page == "Biblioteca":

    st.subheader(
        "Biblioteca de comportamiento"
    )

    library = {
        "Ansiedad":
        "Mantener rutinas y paseos.",

        "Miedo":
        "Evitar sobreestimulación.",

        "Destrucción":
        "Aumentar enriquecimiento.",

        "Convivencia":
        "Introducciones graduales."
    }

    for title, text in library.items():

        with st.container(border=True):

            st.markdown(f"### {title}")
            st.write(text)
