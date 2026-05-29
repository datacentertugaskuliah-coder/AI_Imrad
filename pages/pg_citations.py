import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.data import (CITATION_CONFIG, get_valid_years, IMRAD_SECTIONS,
                        parse_journal_url, generate_fallback_questions,
                        SECTION_FALLBACK_TEMPLATES)

def render():
    st.title("📑 Citation Manager v7 · M10 + M11 Core Intelligence")
    st.caption("50+ sitasi unik · APA 7th · 3 tahun terakhir · Section Gating · 6 fallback questions EN")

    from core.data import get_valid_years
    vy = get_valid_years()
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Total sitasi", str(CITATION_CONFIG["total_target"]),
        f"{CITATION_CONFIG['min_total']}+{CITATION_CONFIG['target_journal_count']}")
    k2.metric("Tahun valid", f"{vy[0]}-{vy[-1]}", "≤ 3 thn")
    k3.metric("Style", "APA 7th", "")
    k4.metric("Target jurnal",
        f"{int(CITATION_CONFIG['target_journal_ratio']*100)}%",
        f"{CITATION_CONFIG['target_journal_count']} sitasi")
    k5.metric("Fallback Q (M11)", str(CITATION_CONFIG["fallback_questions"]),
        "EN, per bagian")

    st.divider()

    # M11 Section Gating (NEW v7)
    st.subheader("🚪 M11 Section Citation Gatekeeper (NEW v7)")
    st.info(
        "**Aturan v7:** Setiap bagian IMRAD WAJIB punya sitasi, **KECUALI Conclusion** "
        "(dibebaskan). Jika bagian tidak punya sitasi → tag "
        "`[CORE-DB][Tidak digunakan][Tidak ditemukan dalam dokumen]` dan sistem "
        "otomatis generate 6 pertanyaan literatur Bahasa Inggris di paragraf akhir bagian.",
        icon="🚪"
    )

    # Visualization: gating per section
    sections_lit = [
        {"Bagian": s["label"], "Sitasi": s["lit"],
         "Mandatory": "Wajib" if s["mandatory_lit"] else "Dibebaskan"}
        for s in IMRAD_SECTIONS
    ]
    df_g = pd.DataFrame(sections_lit)
    fig_g = px.bar(df_g, x="Bagian", y="Sitasi", color="Mandatory",
        color_discrete_map={"Wajib":"#1D9E75","Dibebaskan":"#888780"},
        text="Sitasi", barmode="group")
    fig_g.update_traces(textposition="outside", marker_line_width=1.2)
    fig_g.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=10), height=240,
        yaxis=dict(range=[0,25], gridcolor="rgba(128,128,128,0.15)"),
        legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig_g, use_container_width=True)

    st.divider()

    # M11 Fallback questions preview
    st.subheader("📝 Preview 6 pertanyaan literatur (M11 Fallback)")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sec = st.selectbox("Bagian IMRAD",
            ["Introduction","Methods","Results","Discussion"],
            key="fb_section")
    with fc2:
        topic = st.text_input("Topik penelitian", value="deep learning",
            key="fb_topic")
    with fc3:
        field = st.text_input("Bidang ilmu", value="Komputer / AI",
            key="fb_field")

    qs = generate_fallback_questions(sec, topic, field)
    st.markdown(f"**6 pertanyaan untuk bagian {sec}:**")
    for i, q in enumerate(qs, 1):
        st.markdown(f"**Q{i}.** {q}")

    st.caption(
        f"Pertanyaan ini akan ditampilkan di paragraf akhir bagian {sec} jika "
        f"M11 mendeteksi tidak ada sitasi yang relevan dari [CORE-DB]."
    )

    st.divider()

    # M10 Citation Pipeline
    st.subheader("🔄 M10 Citation Pipeline (5 langkah)")

    pipeline = [
        {"step":"1","name":"Identify Target","desc":"Parse URL jurnal user","color":"#378ADD"},
        {"step":"2","name":"User Refs","desc":"Priority dari BibTeX/RIS","color":"#1D9E75"},
        {"step":"3","name":"Target Citations","desc":"5-10 dari jurnal target","color":"#BA7517"},
        {"step":"4","name":"Core Database","desc":"Lengkapi ≥50 dari DB","color":"#534AB7"},
        {"step":"5","name":"IMRAD Mapping","desc":"+ M11 Gatekeeper","color":"#3B6D11"},
    ]
    cols = st.columns(5)
    for col, p in zip(cols, pipeline):
        with col:
            st.markdown(
                f"<div style='border:2px solid {p['color']};border-radius:10px;"
                f"padding:12px 10px;text-align:center;min-height:120px'>"
                f"<div style='font-size:18px;font-weight:500;color:{p['color']}'>{p['step']}</div>"
                f"<div style='font-size:12px;font-weight:500;margin-top:4px;color:{p['color']}'>{p['name']}</div>"
                f"<div style='font-size:10px;margin-top:6px;line-height:1.4'>{p['desc']}</div>"
                f"</div>",
                unsafe_allow_html=True)

    st.divider()

    # Citation distribution + sources
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi sitasi per bagian IMRAD")
        df_lit = pd.DataFrame([
            {"Bagian": s["label"], "Sitasi": s["lit"]}
            for s in IMRAD_SECTIONS if s["lit"] > 0
        ])
        fig = px.bar(df_lit, x="Bagian", y="Sitasi", color="Bagian",
            color_discrete_sequence=["#378ADD","#1D9E75","#BA7517","#534AB7"],
            text="Sitasi")
        fig.update_traces(textposition="outside", marker_line_width=1.2)
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10,b=10), height=260,
            yaxis=dict(range=[0,25], gridcolor="rgba(128,128,128,0.15)"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Komposisi sumber sitasi (target)")
        sources = ["User-Provided", "Target Journal", "Core Database"]
        amounts = [10, 7, 33]
        fig2 = go.Figure(go.Pie(
            labels=sources, values=amounts,
            marker_colors=["#1D9E75","#BA7517","#534AB7"],
            hole=0.55, textinfo="label+percent+value"))
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=10), height=260, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Sample APA format
    st.subheader("📋 Sample format sitasi APA 7th (v7)")
    st.code("""
[USER-PROVIDED] [TERVALIDASI]
Smith, J., Lee, K., & Brown, A. (2023). Deep learning approach for
crop disease detection. Computers and Electronics in Agriculture,
215, 108234. https://doi.org/10.1016/j.compag.2023.108234

[TARGET-JOURNAL] [TERVALIDASI]
Chen, W., & Park, S. (2024). Attention mechanisms in plant disease
classification. Expert Systems with Applications, 240, 122541.
https://doi.org/10.1016/j.eswa.2024.122541

[CORE-DB] [Perlu verifikasi manual]
Doe, R., Mitchell, P., & Garcia, L. (2022). CNN-based image
recognition for tropical fruit quality. Information Fusion, 87,
220-235. https://doi.org/10.1016/j.inffus.2022.06.012
    """, language="text")

    st.info(
        "**Integritas v7:**\n"
        "• Setiap sitasi WAJIB punya DOI + URL akses\n"
        "• Tag transparansi: [USER-PROVIDED]/[TARGET-JOURNAL]/[CORE-DB]\n"
        "• Tag validasi: [TERVALIDASI] atau [Perlu verifikasi manual]\n"
        "• M11 fallback aktif jika section tidak punya sitasi\n"
        "• Conclusion DIBEBASKAN dari sitasi wajib",
        icon="🛡"
    )
