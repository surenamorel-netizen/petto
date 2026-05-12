# =========================
# SUPABASE SECRETS
# =========================

SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    ""
)

if not SUPABASE_URL or not SUPABASE_KEY:

    st.error(
        """
        Faltan las credenciales de Supabase.

        Configúralas en:
        Streamlit Cloud → Settings → Secrets
        """
    )

    st.code(
        '''
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU_SUPABASE_ANON_KEY"
        '''
    )

    st.stop()

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
