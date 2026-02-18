import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="GIT-Dash",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# CSS GLOBAL
# =====================
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #F7F7FB;
        border-right: 1px solid #ECECF0;
    }

    /* Style des boutons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid #E0E0E8;
        transition: all 0.2s ease;
        background-color: white;
        color: #1A1A2E;
    }

    .stButton > button:hover {
        background-color: #6C63FF;
        color: white;
        border-color: #6C63FF;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.2);
    }

    /* Cartes et blocs */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid #ECECF0 !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E0E0E8;
        padding: 10px 14px;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #F7F7FB;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #ECECF0;
    }

    /* --- FIX POUR LA BARRE LATÉRALE --- */
    
    /* On cache le menu Streamlit et le footer mais PAS le header entier */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* On s'assure que le bouton de la sidebar est visible et coloré */
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        color: #6C63FF !important;
        background-color: rgba(108, 99, 255, 0.1) !important;
        border-radius: 50% !important;
    }

    /* Correction pour mobile : rendre la flèche de déploiement très visible */
    button[kind="headerNoPadding"] {
        visibility: visible !important;
        color: #6C63FF !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# SUPABASE
# =====================
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

if "supabase" not in st.session_state:
    st.session_state["supabase"] = supabase
if "pseudo" not in st.session_state:
    st.session_state.pseudo = None
if "role" not in st.session_state:
    st.session_state.role = "anonyme"
if "etudiant_id" not in st.session_state:
    st.session_state.etudiant_id = None

# =====================
# SIDEBAR
# =====================
st.sidebar.markdown("""
<div style='text-align:center; padding: 20px 0 10px 0;'>
    <div style='font-size: 40px;'>🎓</div>
    <div style='font-size: 20px; font-weight: 700; color: #1A1A2E;'>GIT-Dash</div>
    <div style='font-size: 12px; color: #999; margin-top: 4px;'>Hub de Survie · Promo GIT</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

if st.session_state.pseudo is None:
    st.sidebar.markdown("**Connexion**")
    pseudo = st.sidebar.text_input("Ton pseudo", placeholder="Entre ton pseudo...")

    if st.sidebar.button("Se connecter", use_container_width=True):
        if pseudo.strip() == "":
            st.sidebar.error("Entre un pseudo !")
        else:
            res = supabase.table("etudiants").select("*").eq("pseudo", pseudo).execute()
            if len(res.data) == 0:
                st.sidebar.error("❌ Pseudo introuvable. Contacte le délégué.")
            elif not res.data[0].get("autorise", False):
                st.sidebar.error("❌ Compte pas encore activé.")
            else:
                st.session_state.pseudo = pseudo
                st.session_state.role = res.data[0]["role"]
                st.session_state.etudiant_id = res.data[0]["id"]
                st.session_state["supabase"] = supabase
                st.rerun()
else:
    role_colors = {
        "delegue": "#6C63FF",
        "moderateur": "#00C48C",
        "etudiant": "#FFB800"
    }
    role_color = role_colors.get(st.session_state.role, "#999")

    st.sidebar.markdown(f"""
    <div style='background: white; border-radius: 10px; padding: 12px 16px; 
                border: 1px solid #ECECF0; margin-bottom: 12px;'>
        <div style='font-weight: 600; color: #1A1A2E; font-size: 14px;'>
            {st.session_state.pseudo}
        </div>
        <div style='margin-top: 4px;'>
            <span style='background: {role_color}22; color: {role_color}; 
                         font-size: 11px; font-weight: 600; padding: 2px 8px; 
                         border-radius: 20px;'>
                {st.session_state.role.upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.role == "etudiant":
        with st.sidebar.expander("🔐 Accès Admin"):
            pwd = st.text_input("Mot de passe", type="password", key="pwd_input")
            if st.button("Valider", key="btn_pwd", use_container_width=True):
                if pwd == os.getenv("DELEGUE_PASSWORD"):
                    supabase.table("etudiants").update({"role": "delegue"}).eq("pseudo", st.session_state.pseudo).execute()
                    st.session_state.role = "delegue"
                    st.rerun()
                elif pwd == os.getenv("MODERATEUR_PASSWORD"):
                    supabase.table("etudiants").update({"role": "moderateur"}).eq("pseudo", st.session_state.pseudo).execute()
                    st.session_state.role = "moderateur"
                    st.rerun()
                else:
                    st.error("Mauvais mot de passe !")

    if st.sidebar.button("Se déconnecter", use_container_width=True):
        for key in ["pseudo", "role", "etudiant_id"]:
            st.session_state[key] = None
        st.session_state.role = "anonyme"
        st.rerun()

# =====================
# PAGE PRINCIPALE
# =====================
if st.session_state.pseudo is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 60px 0 40px 0;'>
            <div style='font-size: 64px; margin-bottom: 16px;'>🎓</div>
            <h1 style='font-size: 36px; font-weight: 700; color: #1A1A2E;'>GIT-Dash</h1>
            <p style='color: #666; font-size: 16px; margin-top: 8px;'>
                Le Hub de Survie de la Promo GIT · EPT
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px;'>
            <div style='background: #F7F7FB; border-radius: 12px; padding: 20px; border: 1px solid #ECECF0;'>
                <div style='font-size: 24px;'>🏠</div>
                <div style='font-weight: 600; margin-top: 8px;'>Dashboard</div>
                <div style='color: #888; font-size: 13px;'>Mood, Countdown DS</div>
            </div>
            <div style='background: #F7F7FB; border-radius: 12px; padding: 20px; border: 1px solid #ECECF0;'>
                <div style='font-size: 24px;'>📚</div>
                <div style='font-weight: 600; margin-top: 8px;'>Modules & Groupes</div>
                <div style='color: #888; font-size: 13px;'>Tout en un endroit</div>
            </div>
            <div style='background: #F7F7FB; border-radius: 12px; padding: 20px; border: 1px solid #ECECF0;'>
                <div style='font-size: 24px;'>🎲</div>
                <div style='font-weight: 600; margin-top: 8px;'>Algorithme de Justice</div>
                <div style='color: #888; font-size: 13px;'>Impartial & redouté</div>
            </div>
            <div style='background: #F7F7FB; border-radius: 12px; padding: 20px; border: 1px solid #ECECF0;'>
                <div style='font-size: 24px;'>💬</div>
                <div style='font-weight: 600; margin-top: 8px;'>Confessions anonymes</div>
                <div style='color: #888; font-size: 13px;'>Dis ce que tu penses</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("👈 Connecte-toi avec ton pseudo dans la barre latérale !")
else:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #6C63FF15, #00C48C10); 
                border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
                border: 1px solid #ECECF0;'>
        <h2 style='margin: 0; font-size: 24px;'>Bon retour, {st.session_state.pseudo} 👋</h2>
        <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
            Promo GIT · EPT — Navigue depuis le menu de gauche
        </p>
    </div>
    """, unsafe_allow_html=True)