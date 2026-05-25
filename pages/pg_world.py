import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from core.data import WORLD_REGIONS

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

def render():
    st.title("🌍 Peta Global — Distribusi Jurnal Scopus Q1")
    st.caption("Skala ukuran + warna + angka — aksesibel untuk pengguna buta warna")

    df = pd.DataFrame(WORLD_REGIONS)

    # ── KPI ───────────────────────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    k1.metric("Total kawasan", str(len(df)), "dipetakan")
    k2.metric("Kawasan tertinggi", "Eropa Barat", f"~{df.loc[df['region']=='Eropa Barat','journals'].values[0]:,} jurnal")
    k3.metric("Kawasan terendah", "Afrika", f"~{df.loc[df['region']=='Afrika','journals'].values[0]:,} jurnal")

    st.divider()

    # ── choropleth world map ──────────────────────────────────────────────────
    st.subheader("Peta intensitas jurnal Scopus Q1 per kawasan")

    rows = []
    for reg, isos in ISO_MAP.items():
        val = df.loc[df["region"] == reg, "journals"].values
        journal_count = int(val[0]) if len(val) else 0
        for iso in isos:
            rows.append({"iso": iso, "region": reg, "journals": journal_count})
    dfc = pd.DataFrame(rows)

    fig = px.choropleth(
        dfc, locations="iso",
        color="journals",
        hover_name="region",
        hover_data={"iso": False, "journals": ":,"},
        color_continuous_scale=[
            [0.0,  "#F1EFE8"],
            [0.05, "#B5D4F4"],
            [0.2,  "#85B7EB"],
            [0.5,  "#378ADD"],
            [0.8,  "#185FA5"],
            [1.0,  "#042C53"],
        ],
        labels={"journals": "Jurnal Q1"},
        projection="natural earth",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="rgba(128,128,128,0.3)",
            bgcolor="rgba(0,0,0,0)",
            showland=True, landcolor="#F8F7F2",
            showocean=True, oceancolor="#EBF4FB",
        ),
        margin=dict(t=0, b=0, l=0, r=0), height=380,
        coloraxis_colorbar=dict(title="Jurnal Q1", tickformat=","),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Sumber data: estimasi berdasarkan Scimago Journal Rank & Scopus 2023–2024.")

    st.divider()

    col1, col2 = st.columns([1.2, 1])

    # ── horizontal bar ────────────────────────────────────────────────────────
    with col1:
        st.subheader("Volume jurnal per kawasan")
        df_sorted = df.sort_values("journals")
        colors = []
        patterns = []
        for v in df_sorted["journals"]:
            if v >= 10000:
                colors.append("#0C447C"); patterns.append("")
            elif v >= 3000:
                colors.append("#378ADD"); patterns.append("/")
            else:
                colors.append("#85B7EB"); patterns.append("x")

        fig2 = go.Figure()
        for i, (_, row) in enumerate(df_sorted.iterrows()):
            fig2.add_trace(go.Bar(
                x=[row["journals"]], y=[row["region"]],
                orientation="h",
                marker_color=colors[i],
                marker_pattern_shape=patterns[i],
                marker_line_color="#fff", marker_line_width=0.5,
                name=row["region"],
                text=f"  {row['journals']:,}",
                textposition="outside",
                showlegend=False,
            ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=5, b=5, l=0, r=60), height=300,
            barmode="overlay",
            xaxis=dict(gridcolor="rgba(128,128,128,0.15)", title="Jurnal Scopus Q1"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Pola: kosong=sangat tinggi · /// = tinggi · xxx = sedang–rendah")

    # ── accessibility score bar ───────────────────────────────────────────────
    with col2:
        st.subheader("Aksesibilitas Open Access (%)")
        df_acc = df.sort_values("access", ascending=True)
        fig3 = px.bar(
            df_acc, x="access", y="region", orientation="h",
            text="access",
            color="access",
            color_continuous_scale=["#85B7EB", "#378ADD", "#0C447C"],
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=5, b=5, l=0, r=20), height=300,
            xaxis=dict(range=[0, 105], gridcolor="rgba(128,128,128,0.15)"),
            coloraxis_showscale=False,
        )
        fig3.update_traces(texttemplate="%{text}%", textposition="outside", textfont_size=11)
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── data table ────────────────────────────────────────────────────────────
    st.subheader("Tabel distribusi jurnal Scopus Q1 per kawasan")
    df_display = df.rename(columns={
        "region": "Kawasan", "countries": "Contoh negara",
        "journals": "Est. jurnal Q1", "access": "Aksesibilitas (%)",
    })
    df_display["Est. jurnal Q1"] = df_display["Est. jurnal Q1"].apply(lambda x: f"~{x:,}")
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Aksesibilitas (%)": st.column_config.ProgressColumn(
                "Aksesibilitas (%)", min_value=0, max_value=100, format="%d%%"
            ),
        },
    )
