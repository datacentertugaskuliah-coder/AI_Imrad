"""pg_prompt.py v14 — Development Info (Core Prompt HIDDEN)"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from core.data import CORE_MODULES, WORKFLOW_STEPS, get_valid_years, JOURNAL_DB, CITATION_CONFIG

def render():
    st.title("ℹ️ Tentang Research Workflow Dashboard")
    st.caption("Core IMRAD Intelligence v14 · 27 Modul · +99% dari v13")

    st.info(
        "**Research Workflow Dashboard** adalah sistem kecerdasan akademik untuk penyusunan "
        "manuskrip penelitian berstandar Scopus Q1–Q4 dan SINTA 1–2. "
        "Core Layer aktif di backend — isi prompt tidak ditampilkan.",
        icon="🔬"
    )
    st.divider()

    # KPI
    k1,k2,k3,k4,k5,k6=st.columns(6)
    k1.metric("Versi","v14","Latest")
    k2.metric("Modul Core",str(len(CORE_MODULES)),"+5 v14")
    k3.metric("Tahap Workflow","6","A → F")
    k4.metric("Jurnal DB",str(len(JOURNAL_DB)),"Terverifikasi")
    k5.metric("Sitasi Min","50","Unik APA 7th")
    k6.metric("Tahun Sitasi",f"{get_valid_years()[0]}-{get_valid_years()[-1]}","Dinamis")

    st.divider()
    st.subheader("🚀 Fitur yang Dikembangkan v14")

    features = [
        ("📊 Content Ratio v14","Results section: 40% tabel + 60% gambar dihitung dari file yang diunggah. Tidak ditentukan manual — sistem hitung otomatis dari naskah."),
        ("🔗 Discussion Linker v14","Discussion wajib referensi ke judul Table/Figure yang dibuat di Results. Sistem ekstrak judul tabel/gambar dari naskah dan inject ke instruksi Discussion."),
        ("📝 1950 Kata per Section","Target kata per section naik dari 1750 → 1950. Setiap paragraf wajib ada angka kuantitatif."),
        ("🔄 Canvas Baru per Stage","Prompt D dibagi 7 stage. Setiap stage ditulis di canvas BARU terpisah. JANGAN timpa canvas lama. Konfirmasi Y untuk lanjut."),
        ("📑 APA per Kalimat","Setiap kalimat klaim di IMRAD wajib disertai (Author, Year). Style APA 7th konsisten di semua section."),
        ("📊 Conclusion dengan Angka","Conclusion 250 kata WAJIB ada angka kuantitatif dari Results. Abstract 250 kata + 5 keyword dipisah ;"),
        ("🏷️ 10 Judul Scopus Q1","Generate otomatis 10 judul artikel standar Scopus Q1 di Stage 6 Prompt D."),
        ("📚 Daftar Pustaka APA+DOI","Stage 7: Daftar Pustaka lengkap APA 7th, diurutkan alfabetis, setiap entri ada https://doi.org/... yang valid dari CrossRef."),
        ("✍️ Humanlike Writing (M24)","Anti-AI-detector. Variasi kalimat pendek-panjang. Aktif:pasif 60:40. Hedging language. Tanda baca: . , ; : - ? ! \" \" ' ' ( ) [ ] / ..."),
        ("🧑‍⚖️ Q1 Reviewer (M27)","Upload manuskrip IMRAD → penilaian reviewer Q1 per section: score 0-10, major/minor revisions, editor comment, rekomendasi perbaikan."),
        ("🌐 GDrive Folder Support","URL folder drive.google.com/drive/folders/ID kini didukung. Download semua file di folder sekaligus."),
        ("📊 M25 Data File Reader","Baca CSV/Excel/TXT/PDF in-memory (tanpa download). Extract angka otomatis → auto-fill Data Kuantitatif."),
    ]

    cols=st.columns(2)
    for i,(title,desc) in enumerate(features):
        with cols[i%2]:
            with st.expander(title):
                st.write(desc)

    st.divider()
    st.subheader("📅 Riwayat Pengembangan")
    hist=pd.DataFrame([
        {"Versi":"v1-v5","Deskripsi":"Prototipe, jurnal database, blacklist enforcement"},
        {"Versi":"v6","Deskripsi":"M10 Citation Manager, 50+ sitasi, journal URL parser"},
        {"Versi":"v7","Deskripsi":"M11-M15: Section Gating, LaTeX, Auto-Extract spec"},
        {"Versi":"v8","Deskripsi":"M16-M20 REAL Executors: pypdf, regex extract, gdown, session corpus"},
        {"Versi":"v9","Deskripsi":"Zero-click auto-fill, CrossRef API REAL, context-aware equation"},
        {"Versi":"v10","Deskripsi":"Bug fix AttributeError semua tab, session state safe patterns"},
        {"Versi":"v11","Deskripsi":"ref_file + style_file dikembalikan, placement rules, GDrive fix"},
        {"Versi":"v12","Deskripsi":"GDrive FOLDER support, merge Section 3 → Section 1"},
        {"Versi":"v13","Deskripsi":"M23-M27: Sub-heading, Humanlike, DataReader, Staged, Reviewer"},
        {"Versi":"v14","Deskripsi":"40/60 tabel/gambar, Discussion←Results, 1950 kata, canvas baru per stage, 10 judul, Daftar Pustaka APA+DOI"},
    ])
    st.dataframe(hist,use_container_width=True,hide_index=True)

    st.divider()
    st.subheader("📖 Cara Penggunaan")
    st.markdown("""
**Alur kerja Prompt D (bertahap, canvas baru tiap stage):**
1. **Section 1** — Upload: naskah utama + referensi + artikel acuan gaya + file data
2. **Section 2** — Cek 5 field auto-filled. Edit jika perlu
3. **Section 3** — Input jurnal target → Fetch Citations CrossRef
4. **Section 4, Prompt D** — Copy prompt → jalankan di AI Anda
5. **Stage 1** (Introduction) → **Y** → **Stage 2** (Methods) → ... → **Stage 7** (Daftar Pustaka)
6. **Download .md** — kerangka manuskrip lengkap dengan sitasi
7. **Reviewer Q1** — upload draft → dapatkan review komprehensif
    """)

    st.divider()
    st.warning("Semua output harus diverifikasi peneliti sebelum submit. DOI [Perlu verifikasi manual] wajib dicek mandiri.",icon="⚠️")
    st.info("Publisher dilarang: Frontiers, Hindawi, MDPI (kecuali Sustainability SDGs).",icon="🚫")
