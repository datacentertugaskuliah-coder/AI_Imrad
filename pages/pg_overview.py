import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.data import (IMRAD_SECTIONS, WORKFLOW_STEPS, CORE_MODULES,
                        JOURNAL_DB, get_valid_years)

CB = ["#378ADD","#1D9E75","#BA7517","#534AB7","#888780","#B5D4F4"]

def render():
    st.title("📊 Overview · Research Workflow v8 · REAL Executor")
    st.caption(f"Core IMRAD v8 · 20 Modul (+5 REAL) · Tahun dinamis {get_valid_years()[0]}-{get_valid_years()[-1]}")

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("Modul Core", "20", "v7: 15 → v8: 20")
    k2.metric("REAL Executor", "5", "M16–M20 NEW")
    k3.metric("Bidang", "4")
    k4.metric("Tahap", "5")
    k5.metric("Sitasi min", "50")
    k6.metric("Jurnal DB", str(len(JOURNAL_DB)))

    st.divider()

    # Highlight v8 changes
    st.subheader("🚀 PERBEDAAN MENDASAR v7 → v8 (+80% kecerdasan)")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown(
            "<div style='border:2px solid #BA7517;border-radius:10px;padding:15px;"
            "background:rgba(186,117,23,0.05)'>"
            "<div style='font-size:14px;font-weight:500;color:#854F0B'>"
            "📜 v7 = Prompt Instruction Generator (PASIF)"
            "</div>"
            "<ul style='margin-top:8px;font-size:12px;color:#666;line-height:1.7'>"
            "<li>User upload PDF → tidak dibaca, hanya nama file dicatat</li>"
            "<li>Auto-extract = placeholder \"[M13 akan extract]\"</li>"
            "<li>Markdown export = instruksi ke AI, tidak generate file</li>"
            "<li>Google Drive = tidak didukung</li>"
            "<li>Tahun = hard-coded 2022-2024</li>"
            "</ul></div>",
            unsafe_allow_html=True)
    with cc2:
        st.markdown(
            "<div style='border:2px solid #1D9E75;border-radius:10px;padding:15px;"
            "background:rgba(29,158,117,0.05)'>"
            "<div style='font-size:14px;font-weight:500;color:#085041'>"
            "⚡ v8 = REAL Executor (AKTIF)"
            "</div>"
            "<ul style='margin-top:8px;font-size:12px;color:#666;line-height:1.7'>"
            "<li>User upload PDF → M16 BENAR-BENAR baca + detect sections</li>"
            "<li>Auto-extract = M17 EKSEKUSI regex + TF-IDF, isi 5 field</li>"
            "<li>Markdown export = M20 GENERATE .md actual + download</li>"
            "<li>Google Drive = M18 fetch via gdown</li>"
            "<li>Tahun = datetime.now().year - 2 (auto-update)</li>"
            "</ul></div>",
            unsafe_allow_html=True)

    st.divider()

    # 5 new executors
    st.subheader("✨ 5 REAL Executor v8 (M16–M20)")
    new_features = [
        {"id":"M16","name":"REAL Document Parser","icon":"⚙️","color":"#0C447C",
         "desc":"pypdf + python-docx. Baca PDF/DOCX nyata, deteksi sections IMRAD."},
        {"id":"M17","name":"REAL Auto-Extractor","icon":"🤖","color":"#534AB7",
         "desc":"Regex + TF-IDF + section detection. Ekstrak 5 field dengan confidence score."},
        {"id":"M18","name":"Google Drive Resolver","icon":"🌐","color":"#3B6D11",
         "desc":"gdown library. Parse shareable link → fetch file → add ke corpus."},
        {"id":"M19","name":"One-by-One File Manager","icon":"📋","color":"#BA7517",
         "desc":"session_state corpus. Add/remove individual. Upload + GDrive gabung."},
        {"id":"M20","name":"REAL MD Exporter","icon":"📤","color":"#1D9E75",
         "desc":"Generate .md actual content. Auto-download via st.download_button. Template tabel/figure 100 kata + fallback questions."},
    ]
    cols = st.columns(5)
    for col, f in zip(cols, new_features):
        with col:
            st.markdown(
                f"<div style='border:2px solid {f['color']};border-radius:10px;"
                f"padding:14px 12px;text-align:center;min-height:180px'>"
                f"<div style='font-size:26px'>{f['icon']}</div>"
                f"<div style='font-weight:500;color:{f['color']};font-size:12px;margin-top:5px'>{f['id']}</div>"
                f"<div style='font-size:11px;font-weight:500;margin-top:3px'>{f['name']}</div>"
                f"<div style='font-size:10px;color:#666;margin-top:6px;line-height:1.5'>{f['desc']}</div>"
                f"</div>", unsafe_allow_html=True)

    st.divider()

    # Two charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Kata per bagian IMRAD")
        df = pd.DataFrame(IMRAD_SECTIONS)
        fig = px.bar(df, x="label", y="words", color="label",
            color_discrete_sequence=CB, text="words")
        fig.update_traces(textposition="outside", marker_line_width=1.2)
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10), height=260,
            yaxis=dict(gridcolor="rgba(128,128,128,0.15)"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sitasi per bagian (M11 gating)")
        df_l = pd.DataFrame([{
            "Bagian":s["label"],"Sitasi":s["lit"],
            "M11":"Wajib" if s["mandatory_lit"] else "Dibebaskan"
        } for s in IMRAD_SECTIONS])
        fig2 = px.bar(df_l, x="Bagian", y="Sitasi", color="M11",
            color_discrete_map={"Wajib":"#1D9E75","Dibebaskan":"#888780"},
            text="Sitasi")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10), height=260,
            legend=dict(orientation="h",y=-0.25))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Pipeline
    st.subheader("Pipeline workflow A → E")
    cols = st.columns(len(WORKFLOW_STEPS))
    for col, step in zip(cols, WORKFLOW_STEPS):
        sc = step["color"]
        with col:
            st.markdown(
                f"<div style='text-align:center;padding:10px 4px;"
                f"border:2px solid {sc};border-radius:10px'>"
                f"<div style='font-size:22px;font-weight:500;color:{sc}'>{step['id']}</div>"
                f"<div style='font-size:10px;margin-top:4px'>{step['label'][:30]}</div>"
                f"</div>", unsafe_allow_html=True)

    st.divider()

    # All 20 modules
    st.subheader("20 Modul Core Intelligence v8")
    mc = st.columns(4)
    for i, mod in enumerate(CORE_MODULES):
        c = mod["color"]
        is_new = mod["id"] in ["M16","M17","M18","M19","M20"]
        badge = "<span style='background:#EAF3DE;color:#27500A;font-size:9px;padding:1px 5px;border-radius:3px;margin-left:4px'>REAL v8</span>" if is_new else ""
        with mc[i % 4]:
            st.markdown(
                f"<div style='border:0.5px solid {c};border-radius:8px;"
                f"padding:8px 10px;margin-bottom:6px;min-height:90px'>"
                f"<div style='font-weight:500;color:{c};font-size:11px'>"
                f"{mod['icon']} {mod['id']} · {mod['name']}{badge}</div>"
                f"<div style='font-size:10px;margin-top:4px;line-height:1.4'>{mod['desc'][:120]}</div>"
                f"</div>", unsafe_allow_html=True)
