import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Emploi du Temps · GIT-Dash", page_icon="📅", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton > button {
        border-radius: 8px; font-weight: 500;
        border: 1px solid #E0E0E8; transition: all 0.2s ease;
        background-color: white; color: #1A1A2E;
    }
    .stButton > button:hover {
        background-color: #6C63FF; color: white; border-color: #6C63FF;
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(108,99,255,0.2);
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important; border: 1px solid #ECECF0 !important;
        background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
</style>
""", unsafe_allow_html=True)

if "pseudo" not in st.session_state or st.session_state.pseudo is None:
    st.warning("👈 Connecte-toi d'abord !")
    st.stop()

supabase = st.session_state["supabase"]
role = st.session_state.role

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #FFB80010, #6C63FF10);
            border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
            border: 1px solid #ECECF0;'>
    <div style='font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 6px;'>Mis à jour par le délégué</div>
    <h1 style='margin: 0; font-size: 28px; font-weight: 700; color: #1A1A2E;'>
        Emploi du Temps 📅
    </h1>
    <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
        Toujours la dernière version disponible ici.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================
# UPLOAD PDF (admin)
# =====================
if role in ["delegue", "moderateur"]:
    with st.expander("📤 Uploader l'emploi du temps de la semaine"):
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                semaine = st.date_input("Semaine du")
            with col2:
                fichier = st.file_uploader("Choisis le PDF", type=["pdf"])

            if st.button("📤 Uploader l'emploi du temps", use_container_width=True):
                if fichier is None:
                    st.error("Sélectionne un fichier PDF !")
                else:
                    nom_fichier = f"edt_{semaine}.pdf"
                    bytes_data = fichier.read()
                    try:
                        supabase.storage.from_("emploi-du-temps").remove([nom_fichier])
                    except:
                        pass
                    supabase.storage.from_("emploi-du-temps").upload(
                        nom_fichier, bytes_data, {"content-type": "application/pdf"}
                    )
                    supabase.table("emploi_du_temps").upsert({
                        "semaine": str(semaine),
                        "nom_fichier": nom_fichier
                    }).execute()
                    st.success("✅ Emploi du temps uploadé avec succès !")
                    st.rerun()

# =====================
# AFFICHER LES PDFs
# =====================
edts = supabase.table("emploi_du_temps").select("*")\
    .order("semaine", desc=True).execute()

if not edts.data:
    with st.container(border=True):
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <div style='font-size: 48px;'>📭</div>
            <p style='color: #666; font-weight: 500; margin-top: 12px;'>
                Aucun emploi du temps disponible pour l'instant
            </p>
            <p style='color: #999; font-size: 13px;'>
                Le délégué peut en uploader un via le bouton ci-dessus
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    edt_actuel = edts.data[0]
    url = supabase.storage.from_("emploi-du-temps").get_public_url(edt_actuel["nom_fichier"])

    # Badge semaine actuelle
    st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: space-between; 
                margin-bottom: 16px;'>
        <div>
            <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                        letter-spacing: 1px;'>Semaine en cours</div>
            <div style='font-size: 18px; font-weight: 700; color: #1A1A2E; margin-top: 4px;'>
                Semaine du {edt_actuel['semaine']}
            </div>
        </div>
        <a href="{url}" target="_blank" style='background: #6C63FF; color: white; 
                  text-decoration: none; padding: 10px 20px; border-radius: 8px;
                  font-weight: 600; font-size: 14px;'>
            📥 Télécharger
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Afficher le PDF
    st.markdown(f"""
    <div style='border: 1px solid #ECECF0; border-radius: 12px; overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);'>
        <iframe src="{url}" width="100%" height="820px" 
        style="border: none; display: block;"></iframe>
    </div>
    """, unsafe_allow_html=True)

    # Historique
    if len(edts.data) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                    letter-spacing: 1px; margin-bottom: 12px;'>Historique des semaines</div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            for i, edt in enumerate(edts.data[1:]):
                url_old = supabase.storage.from_("emploi-du-temps")\
                    .get_public_url(edt["nom_fichier"])
                border = "border-bottom: 1px solid #ECECF0;" if i < len(edts.data) - 2 else ""
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center;
                            padding: 12px 4px; {border}'>
                    <div style='color: #1A1A2E; font-weight: 500;'>
                        📅 Semaine du <strong>{edt['semaine']}</strong>
                    </div>
                    <a href="{url_old}" target="_blank" 
                       style='color: #6C63FF; font-size: 13px; font-weight: 600; text-decoration: none;
                              background: #6C63FF11; padding: 4px 12px; border-radius: 6px;'>
                        Voir PDF →
                    </a>
                </div>
                """, unsafe_allow_html=True)