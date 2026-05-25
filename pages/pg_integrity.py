import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.data import INTEGRITY_RULES, CORE_MODULES

def render():
    st.title("🛡 Integritas Core — Aturan & Quality Score")

    # ── KPI ───────────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    blocks = sum(1 for r in INTEGRITY_RULES if r["type"] == "block")
    warns  = sum(1 for r in INTEGRITY_RULES if r["type"] == "warn")
    oks    = sum(1 for r in INTEGRITY_RULES if r["type"] == "ok")
    k1.metric("Aturan blokir",   str(blocks), "zero-tolerance")
    k2.metric("Aturan tandai",   str(warns),  "ditandai, tidak dihapus")
    k3.metric("Sinyal lolos",    str(oks),    "output tervalidasi")
    k4.metric("Gate wajib",      "1",         "naskah utama = kunci")

    st.divider()

    col1, col2 = st.columns([1.2, 1])

    # ── rules table ───────────────────────────────────────────────────────────
    with col1:
        st.subheader("Status aturan integritas")
        icons = {"block": "🚫", "warn": "⚠️", "ok": "✅"}
        colors = {"block": "#FCEBEB", "warn": "#FAEEDA", "ok": "#EAF3DE"}
        text_c = {"block": "#A32D2D", "warn": "#633806", "ok": "#27500A"}
        for rule in INTEGRITY_RULES:
            t = rule["type"]
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:10px;"
                f"padding:6px 10px;border-radius:6px;background:{colors[t]};margin-bottom:4px'>"
                f"<span>{icons[t]}</span>"
                f"<span style='flex:1;font-size:13px;color:{text_c[t]}'>{rule['label']}</span>"
                f"<span style='font-size:11px;font-weight:600;color:{text_c[t]}'>{rule['status']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── donut: rule distribution ──────────────────────────────────────────────
    with col2:
        st.subheader("Distribusi tipe aturan")
        fig = go.Figure(go.Pie(
            labels=["Blokir", "Tandai", "Lolos"],
            values=[blocks, warns, oks],
            marker_colors=["#E24B4A", "#BA7517", "#1D9E75"],
            hole=0.55,
            textinfo="label+percent",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=260,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sinyal yang dipantau Core")
        signal_data = {
            "Tipe": ["Blokir output", "Tandai & beri tahu", "Izinkan & teruskan", "Simpan ke Memory"],
            "Jumlah": [5, 4, 5, 5],
        }
        dfg = pd.DataFrame(signal_data)
        fig2 = px.bar(
            dfg, x="Jumlah", y="Tipe", orientation="h",
            color="Tipe",
            color_discrete_sequence=["#E24B4A", "#BA7517", "#1D9E75", "#534AB7"],
            text="Jumlah",
        )
        fig2.update_layout(
            showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=5, b=5, l=0, r=20), height=200,
            xaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── quality score comparison bar ──────────────────────────────────────────
    st.subheader("Core Quality Score — dampak kelengkapan dokumen")
    dims = ["Integritas data", "Referensi valid", "Konsistensi IMRAD", "Kesiapan submit"]
    with_doc  = [97, 92, 95, 89]
    without   = [60, 55, 65, 48]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name="Dokumen lengkap", x=dims, y=with_doc,
        marker_color="#1D9E75", marker_line_color="#0F6E56", marker_line_width=1.2,
        text=[f"{v}%" for v in with_doc], textposition="outside",
    ))
    fig3.add_trace(go.Bar(
        name="Tanpa dokumen / parsial", x=dims, y=without,
        marker_color="#BA7517", marker_line_color="#854F0B", marker_line_width=1.2,
        marker_pattern_shape="/",
        text=[f"{v}%" for v in without], textposition="outside",
    ))
    fig3.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10), height=280,
        yaxis=dict(range=[0, 110], gridcolor="rgba(128,128,128,0.15)", title="Skor (%)"),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(
        "Pola garis miring (///): dokumen parsial/tanpa dokumen — "
        "membedakan kategori tanpa bergantung pada warna (aksesibel buta warna)."
    )

    st.divider()

    # ── module activation heatmap ─────────────────────────────────────────────
    st.subheader("Aktivasi modul Core per tahap workflow")
    steps = ["A · Ekstraksi", "B · Literatur", "C · Gaya", "D · Draft", "E · Submit"]
    mods  = ["M1 Parser", "M2 Validator", "M3 Memory", "M4 Literature", "M5 Guard", "M6 Scorer"]
    matrix = [
        [3, 2, 0, 0, 3, 1],
        [0, 0, 2, 3, 1, 2],
        [2, 0, 3, 0, 0, 2],
        [3, 3, 3, 3, 3, 3],
        [0, 0, 2, 0, 0, 3],
    ]
    fig4 = go.Figure(go.Heatmap(
        z=matrix, x=mods, y=steps,
        colorscale=[[0,"#F1EFE8"],[0.5,"#85B7EB"],[1,"#0C447C"]],
        showscale=True,
        colorbar=dict(title="Intensitas", tickvals=[0,1,2,3], ticktext=["Off","Rendah","Sedang","Tinggi"]),
        text=[["Off","Rendah","Off","Off","Tinggi","Rendah"],
              ["Off","Off","Sedang","Tinggi","Rendah","Sedang"],
              ["Sedang","Off","Tinggi","Off","Off","Sedang"],
              ["Tinggi","Tinggi","Tinggi","Tinggi","Tinggi","Tinggi"],
              ["Off","Off","Sedang","Off","Off","Tinggi"]],
        texttemplate="%{text}", textfont_size=10,
    ))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10), height=250,
        xaxis_side="top",
    )
    st.plotly_chart(fig4, use_container_width=True)
