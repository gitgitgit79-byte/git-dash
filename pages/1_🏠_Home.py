import streamlit as st
from datetime import date, datetime

st.set_page_config(page_title="Dashboard · GIT-Dash", page_icon="🏠", layout="wide")

# CSS
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
        background-color: #6C63FF; color: white;
        border-color: #6C63FF; transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108,99,255,0.2);
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important; border: 1px solid #ECECF0 !important;
        background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stMetric"] {
        background: #F7F7FB; border-radius: 10px;
        padding: 12px; border: 1px solid #ECECF0;
    }
</style>
""", unsafe_allow_html=True)

if "pseudo" not in st.session_state or st.session_state.pseudo is None:
    st.warning("👈 Connecte-toi d'abord avec ton pseudo !")
    st.stop()

supabase = st.session_state["supabase"]

# Header
st.markdown(f"""
<div style='background: linear-gradient(135deg, #6C63FF15, #00C48C10);
            border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
            border: 1px solid #ECECF0;'>
    <div style='font-size: 13px; color: #999; font-weight: 500; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 6px;'>Dashboard</div>
    <h1 style='margin: 0; font-size: 28px; font-weight: 700; color: #1A1A2E;'>
        Salut, {st.session_state.pseudo} 👋
    </h1>
    <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
        {date.today().strftime("%A %d %B %Y")}
    </p>
</div>
""", unsafe_allow_html=True)

# =====================
# MOOD DU JOUR
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Mood de la promo</div>
""", unsafe_allow_html=True)

moods_options = {"😴": "Endormi", "😤": "Stressé", "😎": "En forme", "💀": "Mort"}

deja_vote = False
if "etudiant_id" in st.session_state:
    res = supabase.table("moods").select("*")\
        .eq("etudiant_id", st.session_state.etudiant_id)\
        .eq("date_vote", str(date.today()))\
        .execute()
    deja_vote = len(res.data) > 0

with st.container(border=True):
    if not deja_vote:
        st.markdown("<p style='color:#444; font-size:15px; font-weight:500; margin-bottom:16px;'>Comment tu te sens aujourd'hui ?</p>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, (emoji, label) in enumerate(moods_options.items()):
            with cols[i]:
                if st.button(f"{emoji}  {label}", use_container_width=True, key=f"mood_{emoji}"):
                    supabase.table("moods").insert({
                        "etudiant_id": st.session_state.etudiant_id,
                        "emoji": emoji,
                        "date_vote": str(date.today())
                    }).execute()
                    st.rerun()
    else:
        st.markdown("<p style='color: #00C48C; font-weight: 500; font-size: 14px;'>✓ Tu as déjà voté aujourd'hui</p>", unsafe_allow_html=True)

    # Résultats
    tous_moods = supabase.table("moods").select("emoji")\
        .eq("date_vote", str(date.today())).execute()

    if tous_moods.data:
        comptage = {}
        for m in tous_moods.data:
            comptage[m["emoji"]] = comptage.get(m["emoji"], 0) + 1
        total = sum(comptage.values())

        st.markdown(f"<p style='color:#999; font-size:13px; margin-top:16px;'>{total} personne(s) ont voté aujourd'hui</p>", unsafe_allow_html=True)

        cols = st.columns(4)
        for i, (emoji, label) in enumerate(moods_options.items()):
            with cols[i]:
                count = comptage.get(emoji, 0)
                pct = int((count / total) * 100) if total > 0 else 0
                bar_width = pct
                st.markdown(f"""
                <div style='text-align:center; padding: 12px 8px;'>
                    <div style='font-size: 28px;'>{emoji}</div>
                    <div style='font-weight: 600; font-size: 18px; color: #1A1A2E; margin: 4px 0;'>{count}</div>
                    <div style='background: #ECECF0; border-radius: 4px; height: 6px; margin: 6px 0;'>
                        <div style='background: #6C63FF; width: {bar_width}%; height: 6px; border-radius: 4px;'></div>
                    </div>
                    <div style='color: #999; font-size: 12px;'>{pct}%</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# COUNTDOWN EXAMENS
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Countdown DS & Examens</div>
""", unsafe_allow_html=True)

examens = supabase.table("examens").select("*, modules(nom)").execute()

if not examens.data:
    with st.container(border=True):
        st.markdown("<p style='color: #999; text-align:center; padding: 20px 0;'>Aucun examen programmé pour l'instant</p>", unsafe_allow_html=True)
else:
    aujourd_hui = datetime.now()
    examens_tries = sorted(examens.data, key=lambda x: x["date_examen"])

    for examen in examens_tries:
        date_ex = datetime.fromisoformat(examen["date_examen"])
        jours = (date_ex - aujourd_hui).days

        if jours < 0:
            bg, accent, badge_bg, message = "#F7F7FB", "#999", "#99999922", "Terminé 🙏"
        elif jours == 0:
            bg, accent, badge_bg, message = "#FF4D4F08", "#FF4D4F", "#FF4D4F22", "C'EST AUJOURD'HUI ! Courage soldat 🫡"
        elif jours <= 2:
            bg, accent, badge_bg, message = "#FF4D4F08", "#FF4D4F", "#FF4D4F22", "C'est trop tard pour réviser, dors bien 💀"
        elif jours <= 5:
            bg, accent, badge_bg, message = "#FFB80008", "#FFB800", "#FFB80022", "T'as encore le temps... ou pas vraiment 😬"
        elif jours <= 10:
            bg, accent, badge_bg, message = "#FFB80008", "#FFB800", "#FFB80022", "Commence à y penser sérieusement 📚"
        else:
            bg, accent, badge_bg, message = "#00C48C08", "#00C48C", "#00C48C22", "T'as le temps, profite (mais révise quand même) 😎"

        module_nom = examen["modules"]["nom"] if examen.get("modules") else "Module inconnu"
        badge_text = f"J-{jours}" if jours >= 0 else f"il y a {abs(jours)}j"

        st.markdown(f"""
        <div style='background: {bg}; border: 1px solid {accent}33; border-left: 4px solid {accent};
                    border-radius: 10px; padding: 16px 20px; margin-bottom: 10px;
                    display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <div style='font-weight: 600; color: #1A1A2E; font-size: 15px;'>
                    {examen['titre']} 
                    <span style='font-weight: 400; color: #666; font-size: 13px;'>· {module_nom}</span>
                </div>
                <div style='color: #888; font-size: 13px; margin-top: 4px;'>
                    📅 {date_ex.strftime('%d/%m/%Y à %Hh%M')} — {message}
                </div>
            </div>
            <div style='background: {badge_bg}; color: {accent}; font-weight: 700; 
                        font-size: 16px; padding: 8px 16px; border-radius: 8px; white-space: nowrap;'>
                {badge_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# ELEVE MODELE DU JOUR
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Élève Modèle du Jour</div>
""", unsafe_allow_html=True)

modele_today = supabase.table("eleve_modele").select("*, etudiants(pseudo)")\
    .eq("date_tirage", str(date.today())).execute()

if modele_today.data:
    modele = modele_today.data[0]
    pseudo_modele = modele["etudiants"]["pseudo"]
    missions = modele["missions_completees"]

    with st.container(border=True):
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 20px;'>
            <div style='background: linear-gradient(135deg, #6C63FF, #00C48C); 
                        width: 48px; height: 48px; border-radius: 12px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 22px;'>🏆</div>
            <div>
                <div style='font-size: 13px; color: #999;'>Élève modèle aujourd'hui</div>
                <div style='font-size: 20px; font-weight: 700; color: #1A1A2E;'>{pseudo_modele}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        missions_info = [
            ("🧹", "Effacer le tableau", "tableau"),
            ("❓", "Poser des questions", "questions"),
            ("📖", "Suivre en classe", "suivi"),
        ]
        for i, (emoji, label, key) in enumerate(missions_info):
            done = missions.get(key, False)
            with cols[i]:
                st.markdown(f"""
                <div style='background: {"#00C48C0F" if done else "#F7F7FB"}; 
                            border: 1px solid {"#00C48C33" if done else "#ECECF0"};
                            border-radius: 10px; padding: 14px; text-align: center;'>
                    <div style='font-size: 22px;'>{emoji}</div>
                    <div style='font-size: 12px; color: #666; margin-top: 4px;'>{label}</div>
                    <div style='font-weight: 700; color: {"#00C48C" if done else "#CCC"}; 
                                font-size: 16px; margin-top: 6px;'>{"✓" if done else "⏳"}</div>
                </div>
                """, unsafe_allow_html=True)

        if modele.get("note"):
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #6C63FF15, #00C48C10);
                        border-radius: 10px; padding: 14px 20px; margin-top: 16px;
                        text-align: center; border: 1px solid #ECECF0;'>
                <span style='font-size: 13px; color: #666;'>Note du jour</span>
                <span style='font-size: 24px; font-weight: 700; color: #6C63FF; margin-left: 12px;'>
                    {modele['note']}/20
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#999; font-size:13px; margin-top:12px; text-align:center;'>Note pas encore attribuée</p>", unsafe_allow_html=True)
else:
    with st.container(border=True):
        st.markdown("""
        <div style='text-align: center; padding: 24px 0;'>
            <div style='font-size: 36px;'>🎲</div>
            <p style='color: #666; margin-top: 8px;'>Aucun élève modèle tiré au sort aujourd'hui</p>
            <p style='color: #999; font-size: 13px;'>👉 Va dans la page <strong>Justice</strong> pour lancer le tirage</p>
        </div>
        """, unsafe_allow_html=True)