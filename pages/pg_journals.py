import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from core.data import JOURNAL_DB, FIELDS, get_journals, check_apc_ratio, PUBLISHER_BLACKLIST

RANK_ORDER  = {"Q1":0,"Q2":1,"Q3":2,"Q4":3,"SINTA1":4,"SINTA2":5}
RANK_COLOR  = {"Q1":"#0C447C","Q2":"#378ADD","Q3":"#85B7EB",
               "Q4":"#B5D4F4","SINTA1":"#534AB7","SINTA2":"#AFA9EC"}
RANK_BG     = {"Q1":"#042C53","Q2":"#0C447C","Q3":"#185FA5",
               "Q4":"#378ADD","SINTA1":"#3C3489","SINTA2":"#534AB7"}

def render():
    st.title("🎯 Journal Matcher — M7 · M9 Core Intelligence v5")

    col_info, col_warn = st.columns([2,1])
    with col_info:
        st.info(
            "Database **62 jurnal terverifikasi** · Scimago JR 2023 · DOAJ · Sherpa Romeo\n\n"
            "Frontiers, MDPI (kecuali Sustainability/SDGs), dan Hindawi "
            "**tidak ada** dalam database ini.",
            icon="🛡"
        )
    with col_warn:
        st.warning(
            "M9 Field Linearity Checker aktif.\n"
            "Jurnal hanya ditampilkan jika linear dengan bidang dipilih.",
            icon="🔗"
        )

    st.divider()

    # ── Filter ────────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4, fc5 = st.columns([2,2,1.5,1.5,1.5])
    with fc1:
        sel_field = st.selectbox("Bidang ilmu (M9 linearitas)", ["Semua"] + FIELDS)
    with fc2:
        sel_ranks = st.multiselect("Peringkat",
            ["Q1","Q2","Q3","Q4","SINTA1","SINTA2"], default=["Q1","Q2"])
    with fc3:
        sel_apc = st.selectbox("APC", ["Semua","No APC","APC saja"])
    with fc4:
        max_apc = st.number_input("Batas APC (USD)", 0, 7000, 3000, 500)
    with fc5:
        sort_by = st.selectbox("Urutkan", ["Rank → IF","IF tertinggi","No-APC dulu"])

    # Apply
    filtered = JOURNAL_DB[:]
    if sel_field != "Semua":
        filtered = [j for j in filtered if sel_field in j["fields"]]
    if sel_ranks:
        filtered = [j for j in filtered if j["rank"] in sel_ranks]
    if sel_apc == "No APC":
        filtered = [j for j in filtered if not j["apc"]]
    elif sel_apc == "APC saja":
        filtered = [j for j in filtered if j["apc"] and j["apc_usd"] <= max_apc]

    # Sort
    if sort_by == "IF tertinggi":
        filtered.sort(key=lambda j: -(j["if"] or 0))
    elif sort_by == "No-APC dulu":
        filtered.sort(key=lambda j: (j["apc"], RANK_ORDER.get(j["rank"],9), -(j["if"] or 0)))
    else:
        filtered.sort(key=lambda j: (RANK_ORDER.get(j["rank"],9), -(j["if"] or 0)))

    no_apc_n, apc_n, on_target = check_apc_ratio(filtered)
    total_n = len(filtered)

    st.caption(f"**{total_n}** jurnal ditemukan · No-APC: {no_apc_n} · APC: {apc_n}")
    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        st.subheader("Rasio No-APC / APC")
        if total_n > 0:
            fig_d = go.Figure(go.Pie(
                labels=["No APC","APC"],
                values=[no_apc_n, apc_n],
                marker_colors=["#1D9E75","#BA7517"],
                hole=0.58, textinfo="label+percent+value",
                textfont_size=11))
            fig_d.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10,b=10,l=0,r=0),height=200,showlegend=False)
            st.plotly_chart(fig_d, use_container_width=True)
            if on_target:
                st.success("Target 60/40 tercapai", icon="✅")
            else:
                target_na = round(total_n * 0.6)
                st.info(f"Target 60/40 = {target_na} No-APC / {total_n-target_na} APC")

    with ch2:
        st.subheader("Distribusi rank")
        ranks_all = ["Q1","Q2","Q3","Q4","SINTA1","SINTA2"]
        rank_counts = [len([j for j in filtered if j["rank"]==r]) for r in ranks_all]
        r_colors = [RANK_COLOR[r] for r in ranks_all]
        fig_r = go.Figure(go.Bar(
            x=ranks_all, y=rank_counts,
            marker_color=r_colors,
            marker_line_color="#fff", marker_line_width=1.5,
            text=rank_counts, textposition="outside"))
        fig_r.update_layout(paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=10,l=0,r=0),height=200,
            yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),showlegend=False)
        st.plotly_chart(fig_r, use_container_width=True)

    with ch3:
        st.subheader("IF per jurnal")
        df_if = pd.DataFrame([
            {"J": (j["name"][:28]+"…" if len(j["name"])>28 else j["name"]),
             "IF": round(j["if"],1), "Rank": j["rank"],
             "APC": "APC" if j["apc"] else "No APC"}
            for j in filtered if j["if"]
        ])
        if not df_if.empty:
            fig_if = px.bar(df_if, x="IF", y="J", orientation="h",
                color="Rank", color_discrete_map=RANK_COLOR,
                pattern_shape="APC",
                pattern_shape_map={"No APC":"","APC":"/"},
                text="IF", labels={"J":"","IF":"IF"})
            fig_if.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=5,b=5,l=0,r=5),height=200,
                legend=dict(orientation="h",y=-0.5,font_size=9))
            fig_if.update_traces(textposition="outside",textfont_size=9)
            st.plotly_chart(fig_if, use_container_width=True)
        else:
            st.caption("Tidak ada data IF untuk filter ini.")

    st.divider()

    # ── Journal cards ─────────────────────────────────────────────────────────
    st.subheader(f"Daftar jurnal ({total_n})")
    if not filtered:
        st.warning("Tidak ada jurnal yang sesuai filter. Ubah pilihan di atas.", icon="⚠️")
        return

    for j in filtered:
        rk_col = RANK_COLOR.get(j["rank"],"#888")
        rk_bg  = RANK_BG.get(j["rank"],"#444")
        apc_bg = "#FAEEDA" if j["apc"] else "#EAF3DE"
        apc_fg = "#633806" if j["apc"] else "#27500A"
        if_str = f"IF {j['if']:.1f}" if j["if"] else "IF tidak tersedia"
        fields_str = " · ".join(j["fields"])
        note_color = "#999"

        is_exception = "MDPI" in j["publisher"] and "Sustainability" in j["name"]
        exception_badge = (
            "<span style='background:#FAEEDA;color:#633806;font-size:10px;"
            "padding:2px 6px;border-radius:4px;margin-left:6px'>Pengecualian SDGs</span>"
            if is_exception else ""
        )

        st.markdown(
            f"<div style='border:0.5px solid {rk_col};border-radius:10px;"
            f"padding:12px 16px;margin-bottom:8px'>"
            f"<div style='display:flex;align-items:flex-start;"
            f"justify-content:space-between;gap:10px;flex-wrap:wrap'>"
            f"<div style='flex:1;min-width:200px'>"
            f"<div style='font-size:14px;font-weight:500;margin-bottom:3px'>"
            f"{j['name']}{exception_badge}</div>"
            f"<div style='font-size:12px;color:#666;margin-bottom:3px'>"
            f"{j['publisher']} &nbsp;·&nbsp; {fields_str}</div>"
            f"<div style='font-size:11px;color:{note_color}'>"
            f"📋 Scope: {j['scope']}</div>"
            f"<div style='font-size:11px;color:{note_color};margin-top:2px'>"
            f"ℹ️ {j['note']}</div>"
            f"</div>"
            f"<div style='display:flex;flex-direction:column;gap:4px;"
            f"align-items:flex-end;flex-shrink:0'>"
            f"<span style='background:{rk_bg};color:#fff;padding:3px 10px;"
            f"border-radius:5px;font-size:11px;font-weight:500'>"
            f"{j['rank']} · {if_str}</span>"
            f"<span style='background:{apc_bg};color:{apc_fg};padding:3px 10px;"
            f"border-radius:5px;font-size:11px;font-weight:500'>{j['apc_label']}</span>"
            f"<span style='font-size:10px;color:#888'>ISSN: {j['issn']}</span>"
            f"</div></div>"
            f"<div style='margin-top:8px'>"
            f"<a href='{j['url']}' target='_blank' "
            f"style='font-size:11px;color:{rk_col};text-decoration:none'>"
            f"🔗 {j['url']}</a>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Summary table + download ───────────────────────────────────────────────
    st.subheader("Tabel ringkasan")
    df_tbl = pd.DataFrame([{
        "Jurnal":     j["name"],
        "Publisher":  j["publisher"],
        "Rank":       j["rank"],
        "IF":         j["if"] if j["if"] else None,
        "APC":        j["apc_label"],
        "Bidang":     " / ".join(j["fields"]),
        "ISSN":       j["issn"],
        "URL":        j["url"],
    } for j in filtered])

    st.dataframe(df_tbl, use_container_width=True, hide_index=True,
        column_config={
            "IF": st.column_config.NumberColumn("IF", format="%.1f"),
            "URL": st.column_config.LinkColumn("URL"),
        })

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇ Unduh CSV",
            data=df_tbl.to_csv(index=False),
            file_name="journal_recommendations_v5.csv", mime="text/csv",
            use_container_width=True)
    with c2:
        # Recommended 60/40 subset
        no_apc_rec = [j for j in filtered if not j["apc"]][:max(1, round(total_n*0.6))]
        apc_rec    = [j for j in filtered if j["apc"]][:max(1, round(total_n*0.4))]
        rec_list   = no_apc_rec + apc_rec
        df_rec = pd.DataFrame([{
            "Jurnal":j["name"],"Rank":j["rank"],"IF":j["if"],"APC":j["apc_label"]
        } for j in rec_list])
        st.download_button("⬇ Unduh rekomendasi 60/40",
            data=df_rec.to_csv(index=False),
            file_name="journal_recommended_60_40.csv", mime="text/csv",
            use_container_width=True)
