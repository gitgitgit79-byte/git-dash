import streamlit as st
from datetime import date
import random
import time

st.set_page_config(page_title="Algorithme de Justice · GIT-Dash", page_icon="🎲", layout="wide")

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

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #6C63FF15, #FF4D4F10);
            border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
            border: 1px solid #ECECF0;'>
    <div style='font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 6px;'>Impartialité totale · Transparence absolue</div>
    <h1 style='margin: 0; font-size: 28px; font-weight: 700; color: #1A1A2E;'>
        Algorithme de Justice ⚖️
    </h1>
    <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
        Personne n'échappe à l'algorithme.
    </p>
</div>
""", unsafe_allow_html=True)

etudiants = supabase.table("etudiants").select("*").eq("autorise", True).execute()
liste = [e["pseudo"] for e in etudiants.data]

if len(liste) == 0:
    st.error("Aucun étudiant enregistré !")
    st.stop()

# =====================
# MODE 1 : ELEVE MODELE
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Élève Modèle du Jour</div>
""", unsafe_allow_html=True)

modele_today = supabase.table("eleve_modele").select("*, etudiants(pseudo)")\
    .eq("date_tirage", str(date.today())).execute()

if modele_today.data:
    pseudo_modele = modele_today.data[0]["etudiants"]["pseudo"]

    with st.container(border=True):
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 16px; margin-bottom: 20px;'>
            <div style='background: linear-gradient(135deg, #6C63FF, #00C48C);
                        width: 52px; height: 52px; border-radius: 14px;
                        display: flex; align-items: center; justify-content: center; font-size: 24px;'>🏆</div>
            <div>
                <div style='font-size: 13px; color: #999;'>Tiré au sort aujourd'hui</div>
                <div style='font-size: 22px; font-weight: 700; color: #1A1A2E;'>{pseudo_modele}</div>
            </div>
            <div style='margin-left: auto; background: #00C48C22; color: #00C48C; 
                        font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 20px;'>
                ✓ Désigné
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.role in ["delegue", "moderateur"]:
            st.markdown("<div style='border-top: 1px solid #ECECF0; padding-top: 16px; margin-top: 4px;'></div>", unsafe_allow_html=True)
            st.markdown("<p style='font-weight: 600; color: #1A1A2E; font-size: 14px;'>Attribuer une note & valider les missions</p>", unsafe_allow_html=True)

            note = st.slider("Note /20", 0, 20, 10)
            col1, col2, col3 = st.columns(3)
            with col1:
                tableau = st.checkbox("🧹 A effacé le tableau")
            with col2:
                questions = st.checkbox("❓ A posé des questions")
            with col3:
                suivi = st.checkbox("📖 A bien suivi en classe")

            if st.button("💾 Enregistrer", use_container_width=True):
                supabase.table("eleve_modele").update({
                    "note": note,
                    "missions_completees": {
                        "tableau": tableau,
                        "questions": questions,
                        "suivi": suivi
                    }
                }).eq("date_tirage", str(date.today())).execute()
                st.success("Enregistré !")
                st.rerun()
else:
    with st.container(border=True):
        if st.session_state.role in ["delegue", "moderateur"]:
            st.markdown("""
            <div style='text-align: center; padding: 16px 0 20px 0;'>
                <div style='font-size: 40px;'>🎲</div>
                <p style='color: #444; font-weight: 500; margin: 8px 0 4px 0;'>Personne n'a encore été désigné aujourd'hui</p>
                <p style='color: #999; font-size: 13px;'>Clique pour lancer le tirage officiel</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🏆 Tirer l'élève modèle du jour !", use_container_width=True):
                with st.spinner("L'algorithme délibère..."):
                    time.sleep(2)
                elu = random.choice(etudiants.data)
                supabase.table("eleve_modele").insert({
                    "etudiant_id": elu["id"],
                    "date_tirage": str(date.today())
                }).execute()
                st.balloons()
                st.success(f"🎯 C'est **{elu['pseudo']}** qui est l'élève modèle aujourd'hui !")
                st.rerun()
        else:
            st.markdown("""
            <div style='text-align: center; padding: 24px 0;'>
                <div style='font-size: 36px;'>⏳</div>
                <p style='color: #666; margin-top: 8px;'>Le délégué n'a pas encore tiré l'élève modèle du jour</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# MODE 2 : VICTIME
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Désigner une Victime</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("""
    <p style='color: #444; font-size: 14px; margin-bottom: 16px;'>
        Qui devra répondre à la prochaine question difficile ? L'algorithme décide.
    </p>
    """, unsafe_allow_html=True)

    if "victime_result" not in st.session_state:
        st.session_state.victime_result = None

    if st.button("🎯 Désigner une victime au hasard !", use_container_width=True):
        with st.spinner("L'algorithme de justice délibère..."):
            time.sleep(2)
        st.session_state.victime_result = random.choice(liste)
        st.rerun()

    if st.session_state.victime_result:
        st.markdown(f"""
        <div style='background: #FF4D4F08; border: 2px solid #FF4D4F33; border-radius: 12px;
                    padding: 20px; text-align: center; margin-top: 12px;'>
            <div style='font-size: 13px; color: #FF4D4F; font-weight: 600; text-transform: uppercase;
                        letter-spacing: 1px;'>💀 La victime est</div>
            <div style='font-size: 32px; font-weight: 700; color: #1A1A2E; margin: 8px 0;'>
                {st.session_state.victime_result}
            </div>
            <div style='font-size: 12px; color: #999;'>L'algorithme a parlé. Aucun appel possible.</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# MODE 3 : ORDRE DE PASSAGE
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Ordre de Passage des Groupes</div>
""", unsafe_allow_html=True)

groupes_res = supabase.table("groupes").select("*, modules(nom)").execute()

with st.container(border=True):
    if groupes_res.data:
        if "ordre_passage" not in st.session_state:
            st.session_state.ordre_passage = None

        if st.button("🔀 Mélanger l'ordre de passage !", use_container_width=True):
            with st.spinner("Mélange en cours..."):
                time.sleep(1.5)
            groupes_liste = [g["nom"] for g in groupes_res.data]
            random.shuffle(groupes_liste)
            st.session_state.ordre_passage = groupes_liste
            st.rerun()

        if st.session_state.ordre_passage:
            st.markdown("<div style='margin-top: 16px;'>", unsafe_allow_html=True)
            for i, groupe in enumerate(st.session_state.ordre_passage):
                couleur = ["#6C63FF", "#00C48C", "#FFB800", "#FF4D4F", "#6C63FF"][i % 5]
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 12px; 
                            padding: 12px 16px; border-radius: 8px; 
                            background: #F7F7FB; margin-bottom: 8px;
                            border: 1px solid #ECECF0;'>
                    <div style='background: {couleur}; color: white; font-weight: 700;
                                width: 28px; height: 28px; border-radius: 8px;
                                display: flex; align-items: center; justify-content: center;
                                font-size: 13px; flex-shrink: 0;'>{i+1}</div>
                    <div style='font-weight: 500; color: #1A1A2E;'>{groupe}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 24px 0;'>
            <p style='color: #999; font-size: 14px;'>Aucun groupe créé pour l'instant</p>
            <p style='color: #BBB; font-size: 13px;'>Crée des groupes dans la page Modules</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# HISTORIQUE
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Historique des Élèves Modèles</div>
""", unsafe_allow_html=True)

historique = supabase.table("eleve_modele")\
    .select("*, etudiants(pseudo)")\
    .order("date_tirage", desc=True)\
    .limit(10)\
    .execute()

with st.container(border=True):
    if historique.data:
        for i, h in enumerate(historique.data):
            pseudo = h["etudiants"]["pseudo"]
            note = h.get("note")
            date_str = h["date_tirage"]
            border = "border-bottom: 1px solid #ECECF0;" if i < len(historique.data) - 1 else ""

            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center;
                        padding: 12px 4px; {border}'>
                <div>
                    <span style='font-weight: 600; color: #1A1A2E;'>{pseudo}</span>
                    <span style='color: #999; font-size: 13px; margin-left: 8px;'>· {date_str}</span>
                </div>
                <div style='background: {"#6C63FF22" if note else "#F7F7FB"}; 
                            color: {"#6C63FF" if note else "#999"};
                            font-weight: 600; font-size: 13px;
                            padding: 4px 12px; border-radius: 20px;'>
                    {f"{note}/20" if note else "Non noté"}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #999; text-align:center; padding: 20px 0;'>Pas encore d'historique</p>", unsafe_allow_html=True)