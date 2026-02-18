import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Confessions · GIT-Dash", page_icon="💬", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
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
    .stTextArea textarea {
        border-radius: 8px; border: 1px solid #E0E0E8; font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea:focus {
        border-color: #6C63FF; box-shadow: 0 0 0 3px rgba(108,99,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

if "pseudo" not in st.session_state or st.session_state.pseudo is None:
    st.warning("👈 Connecte-toi d'abord !")
    st.stop()

supabase = st.session_state["supabase"]

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #1A1A2E0A, #6C63FF10);
            border-radius: 16px; padding: 28px 32px; margin-bottom: 28px;
            border: 1px solid #ECECF0;'>
    <div style='font-size: 11px; color: #999; font-weight: 600; text-transform: uppercase; 
                letter-spacing: 1px; margin-bottom: 6px;'>Espace anonyme · Safe zone</div>
    <h1 style='margin: 0; font-size: 28px; font-weight: 700; color: #1A1A2E;'>
        Confessions Anonymes 🤫
    </h1>
    <p style='color: #666; margin: 6px 0 0 0; font-size: 14px;'>
        Dis ce que tu penses. Personne ne saura que c'est toi.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================
# POSTER UNE CONFESSION
# =====================
st.markdown("""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>Nouvelle confession</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    contenu = st.text_area(
        "Ce que tu as sur le cœur...",
        placeholder="Ex: j'ai rien compris au TP d'hier 😭  •  Qui a les notes du cours de vendredi ?  •  Le prof arrive toujours en retard mais nous on peut pas...",
        max_chars=300,
        height=100,
        label_visibility="collapsed"
    )

    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        chars = len(contenu)
        st.markdown(f"<p style='color: {'#FF4D4F' if chars > 280 else '#999'}; font-size: 12px; text-align:right; margin-top: 8px;'>{chars}/300</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Poster 🤫", use_container_width=True):
            if contenu.strip() == "":
                st.error("Écris quelque chose !")
            else:
                supabase.table("confessions").insert({"contenu": contenu}).execute()
                st.success("Confession postée ! 👻")
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# LIRE LES CONFESSIONS
# =====================
confessions = supabase.table("confessions")\
    .select("*")\
    .order("created_at", desc=True)\
    .execute()

total = len(confessions.data) if confessions.data else 0

st.markdown(f"""
<div style='font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px;'>
    Confessions de la promo 
    <span style='background: #6C63FF22; color: #6C63FF; padding: 2px 8px; 
                 border-radius: 20px; font-size: 11px; margin-left: 6px;'>{total}</span>
</div>
""", unsafe_allow_html=True)

if not confessions.data:
    with st.container(border=True):
        st.markdown("""
        <div style='text-align: center; padding: 32px 0;'>
            <div style='font-size: 40px;'>🫣</div>
            <p style='color: #666; margin-top: 12px; font-weight: 500;'>Aucune confession pour l'instant</p>
            <p style='color: #999; font-size: 13px;'>Soyez le premier à briser le silence</p>
        </div>
        """, unsafe_allow_html=True)
else:
    for confession in confessions.data:
        reactions = confession.get("reactions", {"😂": 0, "👀": 0, "💀": 0})
        total_reactions = sum(reactions.values())
        date_str = datetime.fromisoformat(confession['created_at']).strftime("%d/%m · %Hh%M")

        with st.container(border=True):
            # Contenu
            st.markdown(f"""
            <div style='display: flex; gap: 14px; align-items: flex-start;'>
                <div style='background: #F7F7FB; border-radius: 10px; width: 36px; height: 36px;
                            display: flex; align-items: center; justify-content: center;
                            font-size: 18px; flex-shrink: 0; border: 1px solid #ECECF0;'>👻</div>
                <div style='flex: 1;'>
                    <p style='color: #1A1A2E; font-size: 15px; margin: 0 0 6px 0; line-height: 1.5;'>
                        {confession['contenu']}
                    </p>
                    <span style='color: #BBB; font-size: 12px;'>{date_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Réactions
            st.markdown("<div style='border-top: 1px solid #F0F0F0; margin-top: 12px; padding-top: 10px;'>", unsafe_allow_html=True)
            cols = st.columns([1, 1, 1, 4])
            emoji_list = list(reactions.items())
            for i, (emoji, count) in enumerate(emoji_list):
                with cols[i]:
                    if st.button(f"{emoji} {count}", key=f"{emoji}_{confession['id']}", use_container_width=True):
                        reactions[emoji] += 1
                        supabase.table("confessions").update({
                            "reactions": reactions
                        }).eq("id", confession["id"]).execute()
                        st.rerun()

            # Suppression admin
            if st.session_state.role in ["delegue", "moderateur"]:
                with cols[3]:
                    col_a, col_b = st.columns([3, 1])
                    with col_b:
                        if st.button("🗑️", key=f"del_{confession['id']}", use_container_width=True):
                            supabase.table("confessions").delete()\
                                .eq("id", confession["id"]).execute()
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)