import streamlit as st, hashlib, hmac

st.set_page_config(page_title="Research Workflow · Core IMRAD v17",page_icon="🔬",layout="wide",initial_sidebar_state="expanded")

def _check():
    if st.session_state.get("authenticated"): return True
    st.markdown("## 🔬 Research Workflow Dashboard v17")
    st.markdown("*30 Modul · Humanlike · Staged · Q1 Reviewer · Canvas Baru*")
    st.divider()
    pwd=st.text_input("Access key",type="password",key="li")
    if st.button("Login"):
        exp=st.secrets.get("ACCESS_KEY","demo1234")
        if hmac.compare_digest(hashlib.sha256(pwd.encode()).hexdigest(),hashlib.sha256(exp.encode()).hexdigest()):
            st.session_state.authenticated=True; st.rerun()
        else: st.error("Access key salah.")
    st.stop()

_check()

from pages import (pg_overview,pg_workflow,pg_fields,pg_integrity,
                    pg_world,pg_prompt,pg_journals,pg_citations,
                    pg_equations,pg_reviewer)

PAGES = {
    "📊 Overview":         pg_overview.render,
    "🗂 Workflow A–F":     pg_workflow.render,
    "🧑‍⚖️ Reviewer Q1":    pg_reviewer.render,
    "📑 Citation Manager": pg_citations.render,
    "📐 Equation Builder": pg_equations.render,
    "🎯 Journal Matcher":  pg_journals.render,
    "🔬 Bidang ilmu":      pg_fields.render,
    "🛡 Integritas":       pg_integrity.render,
    "🌍 Peta Global":      pg_world.render,
    "ℹ️ Tentang Sistem":   pg_prompt.render,
}

with st.sidebar:
    st.markdown("### Research Workflow v17")
    st.markdown("*30 Modul · +99% kecerdasan*")
    st.divider()
    choice=st.radio("Navigasi",list(PAGES.keys()),label_visibility="collapsed")
    st.divider()
    st.caption("v17: Canvas baru · 40/60 ratio · Daftar Pustaka APA+DOI · Humanlike")
    if st.button("Logout",use_container_width=True):
        st.session_state.authenticated=False; st.rerun()

PAGES[choice]()
