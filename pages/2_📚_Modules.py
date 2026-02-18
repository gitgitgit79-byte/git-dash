import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Modules · GIT-Dash", page_icon="📚", layout="wide")

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
    .stTextInput > div > div > input {
        border-radius: 8px; border: 1px solid #E0E0E8;
    }
    .stExpander {
        border: 1px solid #ECECF0 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

if "pseudo" not in st.session_state or st.session_state.pseudo is None:
    st.warning("👈 Connecte-toi d'abord !")
    st.stop()

supabase = st.session_state["supabase"]
role = st.session_state.role
est_admin = role in ["delegue", "moderateur"]

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #6C63FF15, #00C48C10);
            border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
            border: 1px solid #ECECF0;'>
    <div style='font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 6px;'>Gestion des matières</div>
    <h1 style='margin: 0; font-size: 28px; font-weight: 700; color: #1A1A2E;'>
        Modules & Matières 📚
    </h1>
    <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
        Tous les modules, examens et groupes de projet en un seul endroit.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================
# AJOUTER UN MODULE
# =====================
if est_admin:
    with st.expander("➕ Ajouter un nouveau module"):
        col1, col2 = st.columns(2)
        with col1:
            nom_module = st.text_input("Nom du module", placeholder="Ex: Réseaux Informatiques")
        with col2:
            prof_module = st.text_input("Professeur", placeholder="Ex: M. Diallo")
        if st.button("✅ Créer le module", use_container_width=True):
            if nom_module.strip() == "":
                st.error("Entre un nom de module !")
            else:
                supabase.table("modules").insert({
                    "nom": nom_module, "professeur": prof_module
                }).execute()
                st.success(f"Module **{nom_module}** créé !")
                st.rerun()

# =====================
# LISTE DES MODULES
# =====================
modules = supabase.table("modules").select("*").order("created_at", desc=False).execute()

if not modules.data:
    with st.container(border=True):
        st.markdown("""
        <div style='text-align: center; padding: 32px 0;'>
            <div style='font-size: 40px;'>📭</div>
            <p style='color: #666; margin-top: 12px;'>Aucun module pour l'instant</p>
            <p style='color: #999; font-size: 13px;'>Le délégué peut en ajouter via le bouton ci-dessus</p>
        </div>
        """, unsafe_allow_html=True)
else:
    en_cours = [m for m in modules.data if m["statut"] == "en_cours"]
    termines = [m for m in modules.data if m["statut"] == "termine"]

    # Stats rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background: #6C63FF0F; border: 1px solid #6C63FF33; border-radius: 10px; padding: 14px 18px;'>
            <div style='font-size: 22px; font-weight: 700; color: #6C63FF;'>{len(en_cours)}</div>
            <div style='font-size: 13px; color: #666;'>Modules en cours</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background: #00C48C0F; border: 1px solid #00C48C33; border-radius: 10px; padding: 14px 18px;'>
            <div style='font-size: 22px; font-weight: 700; color: #00C48C;'>{len(termines)}</div>
            <div style='font-size: 13px; color: #666;'>Modules terminés</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_examens = supabase.table("examens").select("id", count="exact").execute()
        nb_ex = total_examens.count if total_examens.count else 0
        st.markdown(f"""
        <div style='background: #FFB8000F; border: 1px solid #FFB80033; border-radius: 10px; padding: 14px 18px;'>
            <div style='font-size: 22px; font-weight: 700; color: #FFB800;'>{nb_ex}</div>
            <div style='font-size: 13px; color: #666;'>Examens programmés</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- MODULES EN COURS ----
    st.markdown(f"""
    <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 12px;'>
        Modules en cours
        <span style='background: #6C63FF22; color: #6C63FF; padding: 2px 8px; 
                     border-radius: 20px; font-size: 11px; margin-left: 6px;'>{len(en_cours)}</span>
    </div>
    """, unsafe_allow_html=True)

    for module in en_cours:
        examens_count = supabase.table("examens").select("id", count="exact")\
            .eq("module_id", module["id"]).execute()
        groupes_count = supabase.table("groupes").select("id", count="exact")\
            .eq("module_id", module["id"]).execute()
        nb_examens = examens_count.count if examens_count.count else 0
        nb_groupes = groupes_count.count if groupes_count.count else 0

        with st.expander(f"📘 {module['nom']}  ·  {module.get('professeur', 'Prof inconnu')}  ·  {nb_examens} examen(s)  ·  {nb_groupes} groupe(s)"):

            if est_admin:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ Marquer terminé", key=f"fin_{module['id']}", use_container_width=True):
                        supabase.table("modules").update({"statut": "termine"})\
                            .eq("id", module["id"]).execute()
                        st.rerun()
                with col2:
                    if st.button("🗑️ Supprimer le module", key=f"del_{module['id']}", use_container_width=True):
                        supabase.table("modules").delete()\
                            .eq("id", module["id"]).execute()
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # -- EXAMENS --
            st.markdown("""
            <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                        letter-spacing: 1px; margin-bottom: 10px;'>Examens / DS</div>
            """, unsafe_allow_html=True)

            examens = supabase.table("examens").select("*")\
                .eq("module_id", module["id"]).execute()

            if examens.data:
                for ex in examens.data:
                    date_ex = datetime.fromisoformat(ex["date_examen"])
                    jours = (date_ex - datetime.now()).days
                    if jours < 0:
                        accent, bg = "#999", "#F7F7FB"
                    elif jours <= 3:
                        accent, bg = "#FF4D4F", "#FF4D4F08"
                    elif jours <= 7:
                        accent, bg = "#FFB800", "#FFB80008"
                    else:
                        accent, bg = "#00C48C", "#00C48C08"

                    badge = f"J-{jours}" if jours >= 0 else "Passé"
                    col_a, col_b = st.columns([5, 1])
                    with col_a:
                        st.markdown(f"""
                        <div style='background: {bg}; border: 1px solid {accent}33;
                                    border-left: 3px solid {accent}; border-radius: 8px;
                                    padding: 10px 14px; margin-bottom: 6px;
                                    display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='font-weight: 600; color: #1A1A2E;'>{ex['titre']}</span>
                                <span style='color: #888; font-size: 13px; margin-left: 8px;'>
                                    {date_ex.strftime('%d/%m/%Y à %Hh%M')}
                                </span>
                            </div>
                            <span style='background: {accent}22; color: {accent}; font-weight: 700;
                                         font-size: 12px; padding: 3px 10px; border-radius: 20px;'>
                                {badge}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if est_admin:
                            if st.button("🗑️", key=f"delex_{ex['id']}", use_container_width=True):
                                supabase.table("examens").delete()\
                                    .eq("id", ex["id"]).execute()
                                st.rerun()
            else:
                st.markdown("<p style='color: #BBB; font-size: 13px; padding: 4px 0;'>Aucun examen programmé</p>", unsafe_allow_html=True)

            if est_admin:
                with st.container(border=True):
                    st.markdown("<p style='font-weight: 600; font-size: 13px; color: #1A1A2E; margin-bottom: 12px;'>➕ Ajouter un examen</p>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        titre_ex = st.text_input("Titre", placeholder="Ex: DS1", key=f"titre_{module['id']}")
                    with col2:
                        date_ex_input = st.date_input("Date", key=f"date_{module['id']}")
                    with col3:
                        heure_ex = st.time_input("Heure", key=f"heure_{module['id']}")
                    if st.button("➕ Ajouter l'examen", key=f"addex_{module['id']}", use_container_width=True):
                        dt = datetime.combine(date_ex_input, heure_ex)
                        supabase.table("examens").insert({
                            "module_id": module["id"],
                            "titre": titre_ex,
                            "date_examen": dt.isoformat()
                        }).execute()
                        st.success("Examen ajouté !")
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # -- GROUPES --
            st.markdown("""
            <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                        letter-spacing: 1px; margin-bottom: 10px;'>Groupes de projet</div>
            """, unsafe_allow_html=True)

            groupes = supabase.table("groupes").select("*")\
                .eq("module_id", module["id"]).execute()

            statut_config = {
                "pas_commence": ("⚪", "#999", "#F7F7FB", "Pas commencé"),
                "en_cours":     ("🟡", "#FFB800", "#FFB80008", "En cours"),
                "rendu":        ("✅", "#00C48C", "#00C48C08", "Rendu")
            }

            if groupes.data:
                for groupe in groupes.data:
                    ic, color, bg, label = statut_config.get(groupe["statut"], ("⚪", "#999", "#F7F7FB", groupe["statut"]))
                    with st.container(border=True):
                        col_g1, col_g2 = st.columns([3, 1])
                        with col_g1:
                            st.markdown(f"""
                            <div style='margin-bottom: 6px;'>
                                <span style='font-weight: 700; font-size: 15px; color: #1A1A2E;'>{groupe['nom']}</span>
                                <span style='background: {bg}; color: {color}; font-size: 11px; font-weight: 600;
                                             padding: 2px 8px; border-radius: 20px; margin-left: 8px;'>
                                    {ic} {label}
                                </span>
                            </div>
                            <div style='color: #666; font-size: 13px; margin-bottom: 8px;'>
                                {groupe.get('sujet') or 'Pas de sujet défini'}
                            </div>
                            """, unsafe_allow_html=True)
                            link_cols = st.columns(2)
                            with link_cols[0]:
                                if groupe.get("lien_github"):
                                    st.markdown(f"[🔗 GitHub]({groupe['lien_github']})")
                            with link_cols[1]:
                                if groupe.get("lien_drive"):
                                    st.markdown(f"[🔗 Drive]({groupe['lien_drive']})")

                        with col_g2:
                            if est_admin:
                                nouveau_statut = st.selectbox(
                                    "Statut",
                                    ["pas_commence", "en_cours", "rendu"],
                                    key=f"statut_{groupe['id']}",
                                    index=["pas_commence", "en_cours", "rendu"].index(groupe["statut"])
                                )
                                c1, c2 = st.columns(2)
                                with c1:
                                    if st.button("💾", key=f"saveg_{groupe['id']}", use_container_width=True):
                                        supabase.table("groupes").update({"statut": nouveau_statut})\
                                            .eq("id", groupe["id"]).execute()
                                        st.rerun()
                                with c2:
                                    if st.button("🗑️", key=f"delg_{groupe['id']}", use_container_width=True):
                                        supabase.table("groupes").delete()\
                                            .eq("id", groupe["id"]).execute()
                                        st.rerun()
            else:
                st.markdown("<p style='color: #BBB; font-size: 13px; padding: 4px 0;'>Aucun groupe pour ce module</p>", unsafe_allow_html=True)

            if est_admin:
                with st.container(border=True):
                    st.markdown("<p style='font-weight: 600; font-size: 13px; color: #1A1A2E; margin-bottom: 12px;'>➕ Créer un groupe</p>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        nom_g = st.text_input("Nom du groupe", key=f"nomg_{module['id']}")
                        sujet_g = st.text_input("Sujet", key=f"sujetg_{module['id']}")
                    with col2:
                        lien_gh = st.text_input("Lien GitHub", key=f"gh_{module['id']}")
                        lien_dr = st.text_input("Lien Drive", key=f"dr_{module['id']}")
                    if st.button("➕ Créer le groupe", key=f"creer_{module['id']}", use_container_width=True):
                        if nom_g.strip() == "":
                            st.error("Entre un nom de groupe !")
                        else:
                            supabase.table("groupes").insert({
                                "module_id": module["id"],
                                "nom": nom_g, "sujet": sujet_g,
                                "lien_github": lien_gh, "lien_drive": lien_dr
                            }).execute()
                            st.success("Groupe créé !")
                            st.rerun()

    # ---- MODULES TERMINES ----
    if termines:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
                    letter-spacing: 1px; margin-bottom: 12px;'>
            Modules terminés
            <span style='background: #00C48C22; color: #00C48C; padding: 2px 8px; 
                         border-radius: 20px; font-size: 11px; margin-left: 6px;'>{len(termines)}</span>
        </div>
        """, unsafe_allow_html=True)

        for module in termines:
            with st.expander(f"✅ {module['nom']}  ·  {module.get('professeur', '—')}"):
                st.markdown(f"<p style='color: #999; font-size: 13px;'>Ce module est marqué comme terminé.</p>", unsafe_allow_html=True)
                if est_admin:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Remettre en cours", key=f"reopen_{module['id']}", use_container_width=True):
                            supabase.table("modules").update({"statut": "en_cours"})\
                                .eq("id", module["id"]).execute()
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Supprimer définitivement", key=f"delterm_{module['id']}", use_container_width=True):
                            supabase.table("modules").delete()\
                                .eq("id", module["id"]).execute()
                            st.rerun()