import streamlit as st

st.set_page_config(page_title="Admin", page_icon="🔐", layout="wide")

if "pseudo" not in st.session_state or st.session_state.pseudo is None:
    st.warning("👈 Connecte-toi d'abord !")
    st.stop()

if st.session_state.role != "delegue":
    st.error("🔐 Accès réservé au délégué uniquement !")
    st.stop()

supabase = st.session_state["supabase"]

st.title("🔐 Panel Admin — Délégué")
st.markdown("---")

# =====================
# AJOUTER UN ETUDIANT
# =====================
st.subheader("➕ Ajouter un étudiant")

with st.container(border=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nouveau_pseudo = st.text_input("Pseudo", placeholder="Ex: moussa_diallo")
    with col2:
        nouveau_role = st.selectbox("Rôle", ["etudiant", "moderateur", "delegue"])
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Ajouter", use_container_width=True):
            if nouveau_pseudo.strip() == "":
                st.error("Entre un pseudo !")
            else:
                # Vérifier si existe déjà
                check = supabase.table("etudiants").select("*").eq("pseudo", nouveau_pseudo).execute()
                if len(check.data) > 0:
                    st.error(f"❌ Le pseudo **{nouveau_pseudo}** existe déjà !")
                else:
                    supabase.table("etudiants").insert({
                        "pseudo": nouveau_pseudo,
                        "role": nouveau_role,
                        "autorise": True
                    }).execute()
                    st.success(f"✅ **{nouveau_pseudo}** ajouté avec le rôle {nouveau_role} !")
                    st.rerun()

st.markdown("---")

# =====================
# LISTE DES ETUDIANTS
# =====================
st.subheader("👥 Liste de la promo")

etudiants = supabase.table("etudiants").select("*").order("pseudo").execute()

total = len(etudiants.data)
actifs = len([e for e in etudiants.data if e.get("autorise")])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total inscrits", total)
with col2:
    st.metric("Comptes actifs", actifs)
with col3:
    st.metric("Places restantes", max(0, 25 - actifs))

st.markdown("<br>", unsafe_allow_html=True)

if not etudiants.data:
    st.info("Aucun étudiant enregistré.")
else:
    role_colors = {
        "delegue": "#6C63FF",
        "moderateur": "#00C48C",
        "etudiant": "#FFB800"
    }

    for etudiant in etudiants.data:
        role_color = role_colors.get(etudiant["role"], "#999")
        autorise = etudiant.get("autorise", False)

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <div style='font-weight: 600; color: #1A1A2E;'>{etudiant['pseudo']}</div>
                    <span style='background: {role_color}22; color: {role_color}; 
                                 font-size: 11px; font-weight: 600; padding: 2px 8px; 
                                 border-radius: 20px;'>
                        {etudiant['role'].upper()}
                    </span>
                    {"<span style='background: #00C48C22; color: #00C48C; font-size: 11px; padding: 2px 8px; border-radius: 20px;'>✓ Actif</span>" if autorise else "<span style='background: #FF4D4F22; color: #FF4D4F; font-size: 11px; padding: 2px 8px; border-radius: 20px;'>✗ Inactif</span>"}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Changer le rôle
                nouveaux_roles = ["etudiant", "moderateur", "delegue"]
                idx = nouveaux_roles.index(etudiant["role"]) if etudiant["role"] in nouveaux_roles else 0
                new_role = st.selectbox("", nouveaux_roles, index=idx, key=f"role_{etudiant['id']}", label_visibility="collapsed")

            with col3:
                if st.button("💾 Sauver", key=f"save_{etudiant['id']}", use_container_width=True):
                    supabase.table("etudiants").update({
                        "role": new_role
                    }).eq("id", etudiant["id"]).execute()
                    st.success("Rôle mis à jour !")
                    st.rerun()

            with col4:
                # Activer / Désactiver
                if autorise:
                    if st.button("🚫 Désactiver", key=f"deact_{etudiant['id']}", use_container_width=True):
                        supabase.table("etudiants").update({"autorise": False})\
                            .eq("id", etudiant["id"]).execute()
                        st.rerun()
                else:
                    if st.button("✅ Activer", key=f"act_{etudiant['id']}", use_container_width=True):
                        supabase.table("etudiants").update({"autorise": True})\
                            .eq("id", etudiant["id"]).execute()
                        st.rerun()

st.markdown("---")

# =====================
# AJOUT EN MASSE
# =====================
st.subheader("📋 Ajout en masse")
st.caption("Entre un pseudo par ligne pour ajouter plusieurs étudiants d'un coup")

with st.container(border=True):
    pseudos_masse = st.text_area(
        "Pseudos (un par ligne)",
        placeholder="moussa_diallo\nfatou_sow\nibrahima_ndiaye",
        height=150
    )

    if st.button("➕ Ajouter tous", use_container_width=True):
        lignes = [p.strip() for p in pseudos_masse.split("\n") if p.strip() != ""]
        if not lignes:
            st.error("Entre au moins un pseudo !")
        else:
            ajoutes = 0
            ignores = 0
            for p in lignes:
                check = supabase.table("etudiants").select("id").eq("pseudo", p).execute()
                if len(check.data) == 0:
                    supabase.table("etudiants").insert({
                        "pseudo": p,
                        "role": "etudiant",
                        "autorise": True
                    }).execute()
                    ajoutes += 1
                else:
                    ignores += 1

            st.success(f"✅ {ajoutes} étudiant(s) ajouté(s) — {ignores} ignoré(s) (déjà existants)")
            st.rerun()