import streamlit as st
from supabase import create_client
from datetime import datetime

# =========================
# CONFIG
# =========================

APP_TITLE = "Petto"
APP_SUBTITLE = "Seguimiento Post-Adopción"

ADOPTION_STAGES = [
    "Primeros 7 días",
    "Seguimiento 30 días",
    "Seguimiento 90 días"
]

BEHAVIOR_OPTIONS = [
    "Adaptación positiva",
    "Ansiedad",
    "Miedo",
    "Destrucción de objetos",
    "Problemas de convivencia",
    "Otro"
]

# =========================
# PAGE
# =========================

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

# =========================
# SUPABASE
# =========================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

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

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.subheader(
        "Adopciones registradas"
    )

    response = supabase.table(
        "adopciones"
    ).select("*").execute()

    rows = response.data

    if rows:

        for row in rows:

            with st.container(border=True):

                st.write(
                    f"**Familia:** {row['familia']}"
                )

                st.write(
                    f"**Mascota:** {row['mascota']}"
                )

                st.write(
                    f"**Fecha:** {row['fecha']}"
                )

                st.write(
                    f"**Estado:** {row['estado']}"
                )

    else:

        st.info(
            "Todavía no hay adopciones."
        )

# =========================
# NUEVA ADOPCIÓN
# =========================

if page == "Nueva adopción":

    st.subheader(
        "Registrar adopción"
    )

    with st.form("adoption_form"):

        familia = st.text_input(
            "Familia"
        )

        mascota = st.text_input(
            "Mascota"
        )

        fecha = st.date_input(
            "Fecha"
        )

        estado = st.selectbox(
            "Estado",
            ADOPTION_STAGES
        )

        submitted = st.form_submit_button(
            "Guardar adopción"
        )

        if submitted:

            supabase.table(
                "adopciones"
            ).insert({
                "familia": familia,
                "mascota": mascota,
                "fecha": str(fecha),
                "estado": estado
            }).execute()

            st.success(
                "Adopción guardada"
            )

# =========================
# CHECK-IN
# =========================

if page == "Check-in":

    st.subheader(
        "Registrar seguimiento"
    )

    response = supabase.table(
        "adopciones"
    ).select("*").execute()

    rows = response.data

    if not rows:

        st.warning(
            "Primero crea una adopción"
        )

    else:

        options = {
            f"{r['familia']} · {r['mascota']}":
            r["id"]
            for r in rows
        }

        selected = st.selectbox(
            "Selecciona adopción",
            list(options.keys())
        )

        adoption_id = options[selected]

        with st.form("checkin_form"):

            bienestar = st.slider(
                "Bienestar",
                1,
                5,
                3
            )

            comportamiento = st.selectbox(
                "Comportamiento",
                BEHAVIOR_OPTIONS
            )

            notas = st.text_area(
                "Notas"
            )

            submitted = st.form_submit_button(
                "Guardar check-in"
            )

            if submitted:

                supabase.table(
                    "checkins"
                ).insert({
                    "adopcion_id": adoption_id,
                    "fecha": str(datetime.now()),
                    "bienestar": bienestar,
                    "comportamiento": comportamiento,
                    "notas": notas
                }).execute()

                st.success(
                    "Check-in guardado"
                )

        st.divider()

        st.subheader("Historial")

        history_response = supabase.table(
            "checkins"
        ).select("*").eq(
            "adopcion_id",
            adoption_id
        ).execute()

        history = history_response.data

        if history:

            for item in history:

                with st.container(border=True):

                    st.write(
                        f"**Fecha:** {item['fecha']}"
                    )

                    st.write(
                        f"**Bienestar:** {item['bienestar']}/5"
                    )

                    st.write(
                        f"**Comportamiento:** {item['comportamiento']}"
                    )

                    st.write(
                        f"**Notas:** {item['notas']}"
                    )

        else:

            st.info(
                "Todavía no hay check-ins."
            )
