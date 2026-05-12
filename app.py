# Petto · MVP Integral · Streamlit Community Cloud

## Estructura del proyecto

```txt
/app.py
/requirements.txt
/runtime.txt
```

---

# /app.py

```python
import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Petto", layout="wide")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("petto.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS adopciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    familia TEXT,
    mascota TEXT,
    fecha TEXT,
    estado TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adopcion_id INTEGER,
    fecha TEXT,
    bienestar INTEGER,
    comportamiento TEXT,
    notas TEXT
)
''')

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
        "Check-in",
        "Alertas",
        "Biblioteca"
    ]
)

# =========================
# HEADER
# =========================
st.title("🐶 Petto · Seguimiento Post-Adopción")
st.caption("Acompañamiento para protectoras y familias adoptantes")

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":

    st.subheader("Resumen general")

    total = c.execute("SELECT COUNT(*) FROM adopciones").fetchone()[0]

    alertas = c.execute('''
    SELECT COUNT(*)
    FROM checkins
    WHERE bienestar <= 2
    ''').fetchone()[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Adopciones activas", total)
    col2.metric("Alertas de riesgo", alertas)
    col3.metric("Objetivo", "Reducir devoluciones")

    st.divider()

    st.subheader("Adopciones recientes")

    rows = c.execute('''
    SELECT id, familia, mascota, fecha, estado
    FROM adopciones
    ORDER BY id DESC
    ''').fetchall()

    if rows:
        for row in rows:
            with st.container(border=True):
                st.write(f"**Familia:** {row[1]}")
                st.write(f"**Mascota:** {row[2]}")
                st.write(f"**Fecha:** {row[3]}")
                st.write(f"**Estado:** {row[4]}")
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

        submitted = st.form_submit_button("Guardar adopción")

        if submitted:
            c.execute(
                '''
                INSERT INTO adopciones (familia, mascota, fecha, estado)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    familia,
                    mascota,
                    str(fecha),
                    estado
                )
            )

            conn.commit()

            st.success("Adopción registrada correctamente")

# =========================
# CHECK-IN
# =========================
if page == "Check-in":

    st.subheader("Registrar seguimiento")

    adopciones = c.execute('''
    SELECT id, familia, mascota
    FROM adopciones
    ORDER BY id DESC
    ''').fetchall()

    if not adopciones:
        st.warning("Primero debes crear una adopción")

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

            submitted = st.form_submit_button("Guardar check-in")

            if submitted:

                c.execute(
                    '''
                    INSERT INTO checkins (
                        adopcion_id,
                        fecha,
                        bienestar,
                        comportamiento,
                        notas
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (
                        adopcion_id,
                        str(datetime.now()),
                        bienestar,
                        comportamiento,
                        notas
                    )
                )

                conn.commit()

                st.success("Check-in guardado")

        st.divider()

        st.subheader("Historial")

        history = c.execute('''
        SELECT fecha, bienestar, comportamiento, notas
        FROM checkins
        WHERE adopcion_id = ?
        ORDER BY id DESC
        ''', (adopcion_id,)).fetchall()

        if history:
            for h in history:
                with st.container(border=True):
                    st.write(f"**Fecha:** {h[0]}")
                    st.write(f"**Bienestar:** {h[1]}/5")
                    st.write(f"**Comportamiento:** {h[2]}")
                    st.write(f"**Notas:** {h[3]}")

# =========================
# ALERTAS
# =========================
if page == "Alertas":

    st.subheader("⚠️ Casos con riesgo")

    alerts = c.execute('''
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
    ''').fetchall()

    if alerts:
        for a in alerts:
            with st.container(border=True):
                st.error(f"{a[1]} · Riesgo detectado")
                st.write(f"**Familia:** {a[0]}")
                st.write(f"**Bienestar:** {a[2]}/5")
                st.write(f"**Problema:** {a[3]}")
                st.write(f"**Notas:** {a[4]}")
    else:
        st.success("No hay alertas activas")

# =========================
# BIBLIOTECA
# =========================
if page == "Biblioteca":

    st.subheader("📚 Biblioteca de comportamiento")

    with st.container(border=True):
        st.markdown("### Ansiedad")
        st.write(
            "Mantener rutinas estables, paseos frecuentes y espacios seguros."
        )

    with st.container(border=True):
        st.markdown("### Miedo")
        st.write(
            "Evitar sobreestimulación y reforzar conductas positivas."
        )

    with st.container(border=True):
        st.markdown("### Destrucción de objetos")
        st.write(
            "Aumentar enriquecimiento ambiental y tiempo de actividad física."
        )

    with st.container(border=True):
        st.markdown("### Problemas de convivencia")
        st.write(
            "Introducciones graduales y acompañamiento supervisado."
        )
```

---

# /requirements.txt

```txt
streamlit==1.39.0
```

---

# /runtime.txt

```txt
python-3.11
```

---

# Deploy en Streamlit Community Cloud

1. Sube estos archivos a GitHub
2. Ve a share.streamlit.io
3. Conecta el repositorio
4. Selecciona app.py
5. Deploy

---

# Qué hace este MVP

✅ Registro de adopciones
✅ Seguimiento post-adopción
✅ Alertas tempranas
✅ Historial de bienestar
✅ Biblioteca básica de apoyo
✅ Persistencia local con SQLite
✅ Compatible con Streamlit Free Tier

---

# Qué NO hace todavía

❌ Login
❌ WhatsApp
❌ Emails automáticos
❌ IA
❌ Multi-protectora
❌ Subida de archivos
❌ Dashboard avanzado

Eso viene después. El foco aquí es validar seguimiento y reducción de devoluciones.
