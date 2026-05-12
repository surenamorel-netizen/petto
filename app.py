import streamlit as st

from datetime import datetime

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    ADOPTION_STAGES,
    BEHAVIOR_OPTIONS
)

from data.adoption_repository import (
    create_adoption,
    get_adoptions
)

from data.checkin_repository import (
    create_checkin,
    get_checkins
)

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

page = st.sidebar.radio(
    "Navegación",
    [
        "Dashboard",
        "Nueva adopción",
        "Check-in"
    ]
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.subheader(
        "Adopciones registradas"
    )

    rows = get_adoptions()

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

            create_adoption(
                familia,
                mascota,
                str(fecha),
                estado
            )

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

    rows = get_adoptions()

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

                create_checkin(
                    adoption_id,
                    str(datetime.now()),
                    bienestar,
                    comportamiento,
                    notas
                )

                st.success(
                    "Check-in guardado"
                )

        st.divider()

        st.subheader("Historial")

        history = get_checkins(
            adoption_id
        )

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
