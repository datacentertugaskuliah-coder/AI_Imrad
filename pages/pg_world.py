"""
pg_world.py v17 — Peta Global Multi-Rank + Frekuensi Terbit + Realtime Links
Q1, Q2, Q3, Q4, SINTA 1, SINTA 2 + jurnal terbit 3-4x/tahun
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from core.data import (WORLD_REGIONS, JOURNAL_DB, ALL_RANKS,
                        get_rank_distribution, get_journals_by_frequency,
                        get_journals_by_rank, get_realtime_links)

ISO_MAP = {
    "Eropa Barat":   ["GBR","NLD","DEU","FRA","CHE","SWE","NOR","DNK","BEL","AUT","FIN","ESP","ITA"],
    "Amerika Utara": ["USA","CAN"],
    "Asia Timur":    ["CHN","JPN","KOR"],
    "Asia Selatan":  ["IND","PAK","BGD"],
    "Timur Tengah":  ["SAU","IRN","TUR","EGY","ISR"],
    "Amerika Latin": ["BRA","MEX","ARG","CHL","COL"],
    "Asia Tenggara": ["IDN","MYS","THA","PHL","VNM","SGP"],
    "Afrika":        ["ZAF","NGA","KEN","ETH","GHA"],
}

# Rank colors (colorblind-friendly)
RANK_COLORS = {
    "Q1": "#185FA5", "Q2": "#378ADD", "Q3": "#85B7EB", "Q4": "#B5D4F4",
    "SINTA1": "#1D9E75", "SINTA2": "#7FCBAE", "SINTA3": "#A9D9C5", "SINTA4": "#D4ECE2",
}


def render():
    st.title("🌍 Peta Global — Distribusi Jurnal Scopus Q1-Q4 & SINTA 1-4")
    st.caption("Multi-rank · Frekuensi terbit · Link akses realtime · Aksesibel buta warna")

    # ── KPI multi-rank ─────────────────────────────────────────────────────────
    dist = get_rank_distribution()
    st.subheader("📊 Distribusi Jurnal per Peringkat (Q1-Q4 + SINTA 1-4)")
    # 8 ranks in 2 rows of 4
    row1 = st.columns(4)
    for i, rank in enumerate(ALL_RANKS[:4]):
        row1[i].metric(rank, str(dist.get(rank, 0)), "jurnal")
    row2 = st.columns(4)
    for i, rank in enumerate(ALL_RANKS[4:]):
        label = rank.replace("SINTA", "SINTA ")
        row2[i].metric(label, str(dist.get(rank, 0)), "jurnal")

    st.divider()

    # ── Distribusi rank — bar chart ────────────────────────────────────────────
    st.subheader("Distribusi Peringkat Jurnal (Q1-Q4, SINTA 1-4)")
    rank_df = pd.DataFrame([
        {"Peringkat": r, "Jumlah": dist.get(r, 0), "Warna": RANK_COLORS[r]}
        for r in ALL_RANKS
    ])
    fig_rank = go.Figure()
    for _, row in rank_df.iterrows():
        fig_rank.add_trace(go.Bar(
            x=[row["Peringkat"]], y=[row["Jumlah"]],
            name=row["Peringkat"], marker_color=row["Warna"],
            text=[row["Jumlah"]], textposition="outside",
            showlegend=False,
        ))
    fig_rank.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="Jumlah jurnal", xaxis_title="Peringkat",
        font=dict(size=13),
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.divider()

    # ── World choropleth ───────────────────────────────────────────────────────
    st.subheader("Peta Intensitas Jurnal per Kawasan")
    df = pd.DataFrame(WORLD_REGIONS)
    rows = []
    for reg, isos in ISO_MAP.items():
        val = df.loc[df["region"] == reg, "journals"].values
        jc = int(val[0]) if len(val) else 0
        for iso in isos:
            rows.append({"iso": iso, "region": reg, "journals": jc})
    dfc = pd.DataFrame(rows)

    fig = px.choropleth(
        dfc, locations="iso", color="journals", hover_name="region",
        hover_data={"iso": False, "journals": ":,"},
        color_continuous_scale=[
            [0.0,"#F1EFE8"],[0.05,"#B5D4F4"],[0.2,"#85B7EB"],
            [0.5,"#378ADD"],[0.8,"#185FA5"],[1.0,"#042C53"],
        ],
        labels={"journals":"Jurnal"}, projection="natural earth",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", height=420,
        margin=dict(t=10,b=10,l=10,r=10),
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Frekuensi terbit 3-4x/tahun ────────────────────────────────────────────
    st.subheader("📅 Jurnal Terbit 3–4 Kali per Tahun")
    st.info(
        "Jurnal dengan frekuensi terbit 3-4 kali setahun (Quarterly/Triannual) "
        "memberikan peluang submit lebih sering dengan siklus review yang teratur.",
        icon="📅"
    )

    fc1, fc2 = st.columns([1, 3])
    with fc1:
        freq_min = st.select_slider("Min terbit/tahun", [1,2,3,4,6,12], value=3)
        freq_max = st.select_slider("Max terbit/tahun", [1,2,3,4,6,12], value=4)

    freq_journals = get_journals_by_frequency(freq_min, freq_max)

    with fc2:
        st.metric("Jurnal ditemukan", f"{len(freq_journals)} jurnal",
                  f"terbit {freq_min}-{freq_max}x/tahun")

    if freq_journals:
        for j in freq_journals:
            links = get_realtime_links(j)
            with st.expander(f"📕 {j['name']} · {j['rank']} · {j['frequency']} ({j['issues_per_year']}x/tahun)"):
                ic1, ic2 = st.columns([2, 1])
                with ic1:
                    st.markdown(f"**Publisher:** {j['publisher']}")
                    st.markdown(f"**Bidang:** {', '.join(j['fields'])}")
                    st.markdown(f"**ISSN:** {j['issn']} · **APC:** {j['apc_label']}")
                    st.markdown(f"**Scope:** {j['scope']}")
                with ic2:
                    st.markdown("**🔗 Link Akses Realtime:**")
                    st.markdown(f"[🌐 Jurnal Resmi]({links['Direct']})")
                    st.markdown(f"[📊 Scimago]({links['Scimago']})")
                    st.markdown(f"[📂 DOAJ]({links['DOAJ']})")
                    if "SINTA" in j["rank"]:
                        st.markdown(f"[🇮🇩 SINTA]({links['SINTA']})")

    st.divider()

    # ── Tabel lengkap semua jurnal per rank ───────────────────────────────────
    st.subheader("📋 Direktori Lengkap Jurnal per Peringkat")
    rank_filter = st.multiselect(
        "Filter peringkat", ALL_RANKS, default=ALL_RANKS,
        help="Pilih peringkat jurnal yang ingin ditampilkan")

    filtered = [j for j in JOURNAL_DB if j.get("rank") in rank_filter]
    if filtered:
        table_rows = []
        for j in filtered:
            table_rows.append({
                "Jurnal": j["name"][:40],
                "Rank": j["rank"],
                "Publisher": j["publisher"][:20],
                "Frekuensi": j.get("frequency", "—"),
                "x/Tahun": j.get("issues_per_year", "—"),
                "APC": j["apc_label"],
                "ISSN": j["issn"],
            })
        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True, height=400)
        st.caption(f"Menampilkan {len(filtered)} jurnal · Klik kolom untuk sort")

        # Download CSV
        csv = df_table.to_csv(index=False)
        st.download_button("⬇ Unduh direktori (.csv)", data=csv,
            file_name="direktori_jurnal_q1q4_sinta.csv", mime="text/csv")

    st.divider()

    # ── Sumber verifikasi realtime ─────────────────────────────────────────────
    st.subheader("🔗 Sumber Verifikasi Realtime")
    st.info(
        "Semua peringkat dan data jurnal dapat diverifikasi realtime melalui "
        "direktori resmi berikut. Data dalam sistem ini bersumber dari Scimago JR "
        "2023-2024, DOAJ, dan SINTA Kemdikbud.",
        icon="🔗"
    )
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("**Internasional (Scopus):**")
        st.markdown("[📊 Scimago Journal Rank](https://www.scimagojr.com/journalrank.php)")
        st.markdown("[🔍 Scopus Sources](https://www.scopus.com/sources)")
    with sc2:
        st.markdown("**Open Access:**")
        st.markdown("[📂 DOAJ](https://doaj.org)")
        st.markdown("[🔓 Sherpa Romeo](https://v2.sherpa.ac.uk/romeo/)")
    with sc3:
        st.markdown("**Indonesia (SINTA):**")
        st.markdown("[🇮🇩 SINTA Kemdikbud](https://sinta.kemdikbud.go.id/journals)")
        st.markdown("[📚 Garuda](https://garuda.kemdikbud.go.id)")

    st.caption(
        "⚠️ Peringkat jurnal dapat berubah setiap tahun. Selalu verifikasi "
        "status terkini melalui Scimago atau SINTA sebelum submit."
    )
