import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.data import FIELD_MATRIX, FIELDS, SCORES, DIMS

CB = ["#378ADD", "#1D9E75", "#BA7517", "#534AB7"]
BADGE = {
    "Wajib":        ("#EAF3DE", "#27500A"),
    "Dominan":      ("#EAF3DE", "#27500A"),
    "Adaptif":      ("#FAEEDA", "#633806"),
    "Parsial":      ("#FAEEDA", "#633806"),
    "Opsional":     ("#E6F1FB", "#0C447C"),
    "Tidak wajib":  ("#F1EFE8", "#5F5E5A"),
    "Jarang":       ("#F1EFE8", "#888780"),
}

def _badge(val):
    bg, fg = BADGE.get(val, ("#F1EFE8", "#555"))
    return (f"<span style='background:{bg};color:{fg};padding:2px 8px;"
            f"border-radius:5px;font-size:11px;font-weight:500'>{val}</span>")

def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def render():
    st.title("🔬 Bidang Ilmu — Adaptasi Workflow")
    sel = st.selectbox("Filter tampilan bidang", ["Semua"] + FIELDS)
    fields_to_show = FIELDS if sel == "Semua" else [sel]
    st.divider()

    # Radar
    st.subheader("Profil metodologi per bidang ilmu")
    fig = go.Figure()
    for i, f in enumerate(fields_to_show):
        sc = SCORES[f]
        ci = FIELDS.index(f)
        rgb = _hex2rgb(CB[ci])
        fig.add_trace(go.Scatterpolar(
            r=sc + [sc[0]], theta=DIMS + [DIMS[0]],
            fill="toself", name=f, line_color=CB[ci],
            fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.12)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0,100],gridcolor="rgba(128,128,128,0.2)")),
        showlegend=True, paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20,b=20), height=320,
        legend=dict(orientation="h",y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # Bar
    st.subheader("Kompleksitas dimensi per bidang")
    rows = []
    for f in fields_to_show:
        for dim, val in zip(DIMS, SCORES[f]):
            rows.append({"Bidang": f, "Dimensi": dim, "Skor": val})
    dfc = pd.DataFrame(rows)
    colors = [CB[FIELDS.index(f)] for f in fields_to_show]
    fig2 = px.bar(dfc, x="Dimensi", y="Skor", color="Bidang",
        barmode="group", color_discrete_sequence=colors,
        labels={"Skor":"Skor (0-100)"}, text_auto=True)
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=10),height=280,
        yaxis=dict(range=[0,105],gridcolor="rgba(128,128,128,0.15)"),
        legend=dict(orientation="h",y=-0.25))
    fig2.update_traces(textposition="outside", textfont_size=10)
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # Matrix table
    st.subheader("Matriks adaptasi komponen workflow")
    cols_full  = ["Komponen"] + (fields_to_show if sel != "Semua" else FIELDS)
    n_rows = len(FIELD_MATRIX["Komponen"])
    html = ("<table style='width:100%;border-collapse:collapse;font-size:12px'>"
            "<thead><tr>")
    for c in cols_full:
        html += (f"<th style='padding:8px 10px;background:var(--secondary-background-color);"
                 f"text-align:left;border-bottom:1px solid #ddd'>{c}</th>")
    html += "</tr></thead><tbody>"
    for i in range(n_rows):
        html += "<tr>"
        for c in cols_full:
            val = FIELD_MATRIX[c][i] if c in FIELD_MATRIX else "—"
            if c == "Komponen":
                html += (f"<td style='padding:7px 10px;border-bottom:0.5px solid #eee;"
                         f"font-weight:500'>{val}</td>")
            else:
                html += (f"<td style='padding:7px 10px;"
                         f"border-bottom:0.5px solid #eee'>{_badge(val)}</td>")
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)
    st.divider()

    st.caption("Keterangan badge:")
    lc = st.columns(4)
    for i, (k,(bg,fg)) in enumerate(BADGE.items()):
        lc[i%4].markdown(
            f"<span style='background:{bg};color:{fg};padding:2px 8px;"
            f"border-radius:5px;font-size:11px;font-weight:500'>{k}</span>",
            unsafe_allow_html=True)
