"""
pages/pg_reviewer.py — M27 Manuscript Reviewer
Upload IMRAD → Q1 reviewer assessment
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from executors.manuscript_reviewer import review_manuscript


def render():
    st.title("🧑‍⚖️ Manuscript Reviewer — M27 Core Intelligence v13")
    st.caption("Upload manuskrip IMRAD → penilaian reviewer Scopus Q1 lengkap")

    st.info(
        "**M27 Manuscript Reviewer** berperan sebagai **reviewer jurnal bereputasi Q1**. "
        "Upload manuskrip Anda → sistem mengevaluasi setiap bagian IMRAD → "
        "memberikan komentar, skor, dan rekomendasi perbaikan yang komprehensif.",
        icon="🧑‍⚖️"
    )

    st.divider()

    # Upload
    imrad_file = st.file_uploader(
        "📄 Upload manuskrip IMRAD (PDF/DOCX/TXT)",
        type=["pdf","docx","doc","txt"],
        key="reviewer_upload",
        help="Upload draft manuskrip yang ingin diulas sebagai reviewer Q1"
    )

    if not imrad_file:
        st.markdown("""
**Cara menggunakan Manuscript Reviewer:**
1. Upload draft manuskrip dalam format PDF, DOCX, atau TXT
2. Sistem akan menganalisis setiap bagian IMRAD
3. Dapatkan skor per section (0–10) dan overall acceptance probability
4. Tinjau major revisions dan minor revisions yang harus diperbaiki
5. Gunakan rekomendasi untuk meningkatkan kualitas sebelum submit

**Kriteria evaluasi:**
- Kejelasan gap penelitian dan novelty
- Kelengkapan metodologi (reproducibility)
- Kualitas dan kuantitas data hasil
- Keterkaitan Discussion dengan Results
- Kelengkapan pustaka (2022–2024)
        """)
        return

    if st.button("🔍 Mulai Review Q1", type="primary", use_container_width=True):
        with st.spinner("M27 menganalisis manuskrip sebagai reviewer Q1..."):
            result = review_manuscript(imrad_file.read(), imrad_file.name)

        if "error" in result:
            st.error(f"Error: {result['error']}")
            return

        st.session_state["v13_review"] = result
        st.rerun()

    # Display results if available
    if "v13_review" in st.session_state:
        _display_review(st.session_state["v13_review"])


def _display_review(r: dict):
    st.divider()
    st.subheader("📋 Hasil Review Q1")

    # Verdict banner
    verdict = r["verdict"]
    if "✅" in verdict:
        st.success(verdict, icon="✅")
    elif "⚠️" in verdict:
        st.warning(verdict, icon="⚠️")
    else:
        st.error(verdict, icon="❌")

    # KPI row
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Overall Score", f"{r['overall_score']}/10")
    k2.metric("Accept Probability", r["accept_probability"])
    k3.metric("Total Words", f"{r['word_count_total']:,}")
    k4.metric("Reviewed", r["reviewed_at"])

    st.divider()

    # Section scores radar
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("Skor per Bagian IMRAD")
        sec_revs = r.get("section_reviews", {})
        labels = list(sec_revs.keys())
        scores = [sec_revs[s]["score"] for s in labels]

        fig = go.Figure(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=labels + [labels[0]],
            fill="toself",
            line_color="#378ADD",
            fillcolor="rgba(55,138,221,0.15)",
            name="Score"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(range=[0,10],gridcolor="rgba(128,128,128,0.2)")),
            showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=10), height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Detail per Section")
        rows = []
        for sec, rev in sec_revs.items():
            rows.append({
                "Section": sec,
                "Score": f"{rev['score']}/10",
                "Words": rev["word_count"],
                "Target": rev["word_target"],
                "Passed": len(rev["checks_passed"]),
                "Failed": len(rev["checks_failed"]),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # Editor comment
    st.subheader("📝 Editor-in-Chief Comment")
    st.info(r["editor_comment"], icon="📝")

    st.divider()

    # Major & Minor revisions
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("❌ Major Revisions Required")
        if r["major_revisions"]:
            for rev in r["major_revisions"]:
                st.markdown(f"• {rev}")
        else:
            st.success("Tidak ada major revision.", icon="✅")

    with col4:
        st.subheader("⚠️ Minor Revisions Suggested")
        if r["minor_revisions"]:
            for rev in r["minor_revisions"]:
                st.markdown(f"• {rev}")
        else:
            st.success("Tidak ada minor revision.", icon="✅")

    st.divider()

    # Per-section detailed review
    st.subheader("🔍 Detailed Section-by-Section Review")
    for sec, rev in sec_revs.items():
        score = rev["score"]
        color = "#1D9E75" if score >= 7 else "#BA7517" if score >= 5 else "#E24B4A"
        with st.expander(f"{sec} — Score: {score}/10", expanded=(score < 6)):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Checks Passed:**")
                for p in rev["checks_passed"]:
                    st.markdown(f"  ✓ {p}")
            with c2:
                st.markdown("**❌ Checks Failed:**")
                for f in rev["checks_failed"]:
                    st.markdown(f"  ✗ {f}")

            if rev["comments"]:
                st.markdown("**📝 Reviewer Comments:**")
                for c in rev["comments"]:
                    st.warning(c, icon="💬")

            if rev["recommendations"]:
                st.markdown("**🔧 Recommendations:**")
                for rec in rev["recommendations"]:
                    st.info(rec, icon="💡")

    st.divider()

    # Download review
    review_text = _format_review_text(r)
    st.download_button(
        "⬇ Unduh Review Lengkap (.txt)",
        data=review_text,
        file_name=f"review_{r['filename']}_{r['reviewed_at'].replace(':','').replace(' ','_')}.txt",
        mime="text/plain",
        use_container_width=True
    )


def _format_review_text(r: dict) -> str:
    lines = [
        "═" * 60,
        "MANUSCRIPT REVIEW REPORT — Scopus Q1 Standard",
        f"File: {r['filename']}",
        f"Date: {r['reviewed_at']}",
        "═" * 60,
        f"\nVERDICT: {r['verdict']}",
        f"Overall Score: {r['overall_score']}/10",
        f"Acceptance Probability: {r['accept_probability']}",
        f"\nEDITOR COMMENT:\n{r['editor_comment']}",
        "\n" + "─" * 40,
        "MAJOR REVISIONS REQUIRED:",
    ]
    for rev in r["major_revisions"]:
        lines.append(f"  • {rev}")
    lines.append("\nMINOR REVISIONS SUGGESTED:")
    for rev in r["minor_revisions"]:
        lines.append(f"  • {rev}")
    lines.append("\n" + "─" * 40)
    lines.append("SECTION-BY-SECTION REVIEW:")
    for sec, rev in r.get("section_reviews", {}).items():
        lines.append(f"\n[{sec}] Score: {rev['score']}/10 | Words: {rev['word_count']}")
        lines.append("  Passed: " + ", ".join(rev["checks_passed"]))
        if rev["checks_failed"]:
            lines.append("  Failed: " + ", ".join(rev["checks_failed"]))
        for rec in rev["recommendations"]:
            lines.append(f"  → {rec}")
    return "\n".join(lines)
