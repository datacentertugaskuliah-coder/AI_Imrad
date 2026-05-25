"""pg_workflow.py v14 — Full rebuild dengan semua fitur baru"""
import streamlit as st
import pandas as pd
from datetime import datetime
from core.data import (WORKFLOW_STEPS, IMRAD_SECTIONS, FIELDS, IMRAD_STRUCTURE,
                        PLACEMENT_RULES, parse_journal_url, CITATION_CONFIG,
                        get_valid_years, get_equation_templates)
from executors.document_parser   import extract_text, detect_sections
from executors.auto_extractor    import auto_extract_all
from executors.gdrive_resolver   import (validate_gdrive_url, fetch_from_gdrive,
                                            fetch_folder_files, detect_gdrive_type)
from executors.file_manager      import (init_corpus, add_file, remove_file,
                                            get_corpus, get_corpus_summary)
from executors.markdown_generator import (generate_full_manuscript_md,
                                            generate_table_template,
                                            generate_figure_template)
from executors.crossref_api      import build_citation_pool
from executors.equation_selector import select_equations_by_context, explain_selection
from executors.data_reader       import read_datafile_inplace
from executors.content_ratio     import (count_tables_and_figures,
                                            extract_table_figure_titles,
                                            build_discussion_linker_text)
from executors.reference_builder import (build_reference_list,
                                            generate_10_titles_q1)

_DEFAULTS = {
    "v9_topic":"","v9_method":"","v9_novelty":"","v9_quant":"","v9_keywords":"",
    "v9_field":FIELDS[0],"v9_journal_url":"",
    "v9_main_text":"","v9_main_sections":{},"v9_main_filename":"",
    "v9_extracted_confidence":{},"v9_last_uploaded_name":"",
    "v9_citations":{},"v9_selected_eqs":[],
    "v11_ref_filename":"","v11_style_filename":"",
    "v13_corpus_quant":"",
    "v14_content_ratio":{},"v14_result_titles":{},"v14_10_titles":[],
}

def _init():
    for k,v in _DEFAULTS.items():
        if k not in st.session_state: st.session_state[k]=v

def _conf(f): return " ✅" if (st.session_state.get("v9_extracted_confidence") or {}).get(f,0)>0.5 else ""

def _on_main_upload(b,fn):
    t,_=extract_text(b,fn); s=detect_sections(t); ex=auto_extract_all(s)
    for k,f in [("v9_topic","topic"),("v9_method","method"),("v9_novelty","novelty"),("v9_quant","quant_data"),("v9_keywords","keywords")]:
        st.session_state[k]=ex[f]["value"]
    st.session_state.update({
        "v9_main_text":t,"v9_main_sections":s or {},"v9_main_filename":fn,
        "v9_extracted_confidence":{k:v["confidence"] for k,v in ex.items()},
        "v9_last_uploaded_name":fn,
    })
    # v14: analyse content ratio
    ratio = count_tables_and_figures(t)
    titles = extract_table_figure_titles(t)
    st.session_state["v14_content_ratio"] = ratio
    st.session_state["v14_result_titles"] = titles


def render():
    _init(); st.title("🗂 Workflow A–F v14")
    st.caption(f"v14: 1950 kata/section · 40/60 tabel/gambar · Discussion←Results · Canvas baru per stage · Daftar Pustaka APA+DOI · Tahun {get_valid_years()}")
    init_corpus()

    # ── SECTION 1: UPLOAD ──────────────────────────────────────────────────
    st.subheader("1. Unggah Dokumen Penelitian")
    c1,c2=st.columns(2)
    with c1:
        main_doc=st.file_uploader("📄 Naskah utama ★ wajib",type=["pdf","docx","doc","txt"],key="v14_main")
        if main_doc: st.success(f"✅ {main_doc.name}")
        ref_doc=st.file_uploader("📚 Daftar referensi / sitasi (sangat dianjurkan)",type=["bib","txt","docx","pdf","ris"],key="v14_ref")
        if ref_doc:
            st.success(f"✅ {ref_doc.name}")
            st.session_state["v11_ref_filename"]=ref_doc.name
    with c2:
        style_doc=st.file_uploader("📰 Artikel acuan gaya (untuk Prompt C & F)",type=["pdf","docx"],key="v14_style")
        if style_doc:
            st.success(f"✅ {style_doc.name}")
            st.session_state["v11_style_filename"]=style_doc.name
            st.caption("✨ Prompt F akan aktif")

    if main_doc and main_doc.name!=st.session_state.get("v9_last_uploaded_name",""):
        with st.spinner(f"⚙️ M16+M17+M23 parsing {main_doc.name}..."): _on_main_upload(main_doc.read(),main_doc.name)
        st.rerun()

    if st.session_state["v9_main_text"]:
        ratio=st.session_state.get("v14_content_ratio",{})
        if ratio:
            c1r,c2r,c3r,c4r=st.columns(4)
            c1r.metric("Tabel di naskah",ratio.get("tables_in_doc",0))
            c2r.metric("Gambar di naskah",ratio.get("figures_in_doc",0))
            c3r.metric("Target tabel Results (40%)",ratio.get("target_tables",2))
            c4r.metric("Target gambar Results (60%)",ratio.get("target_figures",3))

    # File data
    st.markdown("**📊 File data penelitian** *(M25 baca in-memory, no download)*")
    dt1,dt2=st.tabs(["📤 Upload","🌐 Google Drive (File & Folder)"])
    with dt1:
        nf=st.file_uploader("Pilih file data",type=["xlsx","csv","txt","pdf","png","jpg","docx"],key="v14_data")
        if nf and st.button(f"➕ Tambahkan {nf.name}"):
            fbytes=nf.read()
            add_file(nf.name,fbytes,source="upload")
            dr=read_datafile_inplace(fbytes,nf.name)
            if dr.get("quant_extracted"):
                prev=st.session_state.get("v13_corpus_quant","")
                st.session_state["v13_corpus_quant"]=(prev+" | "+dr["quant_extracted"] if prev else dr["quant_extracted"])
                st.session_state["v9_quant"]=st.session_state["v13_corpus_quant"]
            st.rerun()
    with dt2:
        gurl=st.text_input("Link GDrive (file atau folder)",placeholder="drive.google.com/file/d/... atau drive.google.com/drive/folders/...")
        if gurl:
            ok,msg=validate_gdrive_url(gurl); url_type,_=detect_gdrive_type(gurl)
            if ok:
                st.success(f"{'📁' if url_type=='folder' else '📄'} {msg}")
                if st.button("📥 Download dari GDrive",type="primary"):
                    if url_type=="folder":
                        with st.spinner("Downloading folder..."):
                            fl,err=fetch_folder_files(gurl)
                            if fl:
                                for c,fn,_ in fl: add_file(fn,c,source="gdrive",source_url=gurl)
                                st.success(f"✅ {len(fl)} file"); st.rerun()
                            else: st.error(err)
                    else:
                        with st.spinner("Downloading..."):
                            c,fn,err=fetch_from_gdrive(gurl)
                            if c: add_file(fn,c,source="gdrive",source_url=gurl); st.rerun()
                            else: st.error(err)
            else:
                st.warning(msg)

    corpus=get_corpus()
    if corpus:
        sm=get_corpus_summary()
        ca,cb,cc=st.columns(3)
        ca.metric("File",sm["total"]); cb.metric("Upload/GDrive",f"{sm['upload']}/{sm['gdrive']}"); cc.metric("Size",f"{sm['total_size_kb']:.1f} KB")
        for i,f in enumerate(corpus):
            cols=st.columns([4,1])
            cols[0].caption(f"{'🌐' if f['source']=='gdrive' else '📤'} {f['filename']} · {f['size_kb']:.1f} KB")
            if cols[1].button("❌",key=f"rm_{i}"): remove_file(i); st.rerun()

    st.divider()

    # ── SECTION 2: INFO PENELITIAN ──────────────────────────────────────────
    st.subheader("2. Informasi Penelitian — Auto-filled M17 + M25")
    if not st.session_state["v9_main_text"]: st.warning("Upload naskah utama.",icon="⏳")
    else:
        conf_d=st.session_state.get("v9_extracted_confidence") or {}
        avg_c=sum(conf_d.values())/max(len(conf_d),1)
        st.success(f"⚡ M17 auto-filled · avg {avg_c*100:.0f}%")

    f1,f2=st.columns(2)
    with f1:
        cur_f=st.session_state.get("v9_field",FIELDS[0])
        st.session_state["v9_field"]=st.selectbox("Bidang ilmu",FIELDS,index=FIELDS.index(cur_f) if cur_f in FIELDS else 0)
        st.session_state["v9_topic"]=st.text_input(f"Topik/judul{_conf('topic')}",value=st.session_state["v9_topic"])
        st.session_state["v9_method"]=st.text_area(f"Metode/algoritma{_conf('method')}",value=st.session_state["v9_method"],height=80)
    with f2:
        st.session_state["v9_novelty"]=st.text_area(f"Novelty{_conf('novelty')}",value=st.session_state["v9_novelty"],height=80)
        st.session_state["v9_quant"]=st.text_area(f"Data kuantitatif (angka dari file){_conf('quant_data')}",value=st.session_state["v9_quant"],height=80,help="M25 auto-filled dari file yang diupload")
    st.session_state["v9_keywords"]=st.text_input(f"Kata kunci{_conf('keywords')}",value=st.session_state["v9_keywords"])
    if st.session_state.get("v13_corpus_quant"):
        st.info(f"📊 M25: {st.session_state['v13_corpus_quant'][:200]}",icon="📊")

    st.divider()

    # ── SECTION 3: JURNAL + CITATIONS ──────────────────────────────────────
    st.subheader("3. Jurnal Target + REAL Citations + Daftar Pustaka")
    st.session_state["v9_journal_url"]=st.text_input("Link/ISSN/DOI prefix jurnal target",value=st.session_state.get("v9_journal_url",""),placeholder="https://www.sciencedirect.com/journal/...")
    matched=None
    if st.session_state["v9_journal_url"]:
        matched=parse_journal_url(st.session_state["v9_journal_url"])
        if matched:
            st.markdown(f"<div style='border:0.5px solid #1D9E75;border-radius:8px;padding:10px 14px;background:#E1F5EE'><b style='color:#085041'>🎯 {matched['name']}</b><br><span style='font-size:11px;color:#0F6E56'>{matched['rank']} · IF {matched['if'] or 'N/A'} · ISSN {matched['issn']}</span></div>",unsafe_allow_html=True)

    cit_pool=st.session_state.get("v9_citations") or {}
    if st.session_state["v9_topic"] and matched:
        if st.button("🔍 Fetch REAL Citations + Build Daftar Pustaka",type="primary"):
            with st.spinner("CrossRef API + build APA references..."):
                pool=build_citation_pool(st.session_state["v9_topic"],matched["issn"],CITATION_CONFIG["min_total"])
                st.session_state["v9_citations"]=pool; cit_pool=pool

    if cit_pool.get("total",0)>0:
        all_c=cit_pool.get("target_journal",[])+cit_pool.get("general",[])
        st.success(f"✅ {cit_pool['total']} citations · DOI valid dari CrossRef")
        c1,c2=st.columns(2)
        with c1:
            apa_text="\n\n".join(f"{i+1}. {c['apa']}\n    https://doi.org/{c['doi']}" for i,c in enumerate(all_c) if c.get("doi"))
            st.download_button("⬇ Sitasi APA + DOI (.txt)",data=apa_text,file_name=f"citations_apa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",mime="text/plain",use_container_width=True)
        with c2:
            ref_md=build_reference_list(all_c)
            st.download_button("⬇ Daftar Pustaka lengkap (.md)",data=ref_md,file_name=f"daftar_pustaka_{datetime.now().strftime('%Y%m%d_%H%M')}.md",mime="text/markdown",use_container_width=True)

    st.divider()

    # ── SECTION 4: PROMPTS ─────────────────────────────────────────────────
    st.subheader("4. Generate Prompt per Tahap")
    has_main=bool(st.session_state["v9_main_text"])
    has_style=bool(st.session_state.get("v11_style_filename"))

    tabs=st.tabs([f"Prompt {s['id']} · {s['label'][:20]}" for s in WORKFLOW_STEPS])
    for tab,step in zip(tabs,WORKFLOW_STEPS):
        with tab:
            locked=step["id"]!="A" and not has_main
            if step["id"]=="F" and not has_style:
                st.info("Prompt F aktif hanya jika artikel acuan gaya diunggah.",icon="📰"); continue

            rc1,rc2=st.columns([2,1])
            with rc1:
                st.markdown(f"**Output:** {step['output']}")
                st.markdown(f"**Modul:** {', '.join(step['core_modules'])}")
            with rc2:
                if step.get("words"): st.metric("Target kata/section",f"{step['words']:,}")

            with st.expander("Detail"): st.markdown(step["detail"])

            if locked:
                st.warning("⚠️ Terkunci.",icon="🔒")
            else:
                try: prompt=_build_prompt(step,matched)
                except Exception as e: st.error(f"Error: {e}"); prompt=f"[Error: {e}]"

                with st.expander("Preview prompt",expanded=(step["id"]=="D")):
                    st.code(prompt,language="text")

                c1d,c2d=st.columns(2)
                with c1d:
                    st.download_button(f"⬇ Prompt {step['id']}",data=prompt,file_name=f"prompt_{step['id'].lower()}_v14.txt",mime="text/plain",use_container_width=True)
                if step["id"]=="D":
                    with c2d:
                        try: md_c,md_fn=_generate_md()
                        except Exception as e: md_c,md_fn=f"# Error\n{e}","error.md"
                        st.download_button("📥 Template .md (M20)",data=md_c,file_name=md_fn,mime="text/markdown",type="primary",use_container_width=True)

    st.divider()
    st.subheader("5. Progres IMRAD + Distribusi Konten")
    prog_rows=[]
    for s in IMRAD_SECTIONS:
        extra=""
        if s["label"]=="Results":
            ratio=st.session_state.get("v14_content_ratio",{})
            t=ratio.get("target_tables",2); g=ratio.get("target_figures",3)
            extra=f" | {t} tabel (40%) + {g} gambar (60%)"
        prog_rows.append({"Bagian":s["label"],"Kata":s["words"],"Sitasi":s["lit"],"M11":"Wajib" if s["mandatory_lit"] else "Dibebaskan","Konten":extra.strip("| ")})
    st.dataframe(pd.DataFrame(prog_rows),use_container_width=True,hide_index=True)


def _generate_md():
    cit_pool=st.session_state.get("v9_citations") or {}
    all_c=cit_pool.get("target_journal",[])+cit_pool.get("general",[])
    field=st.session_state.get("v9_field",FIELDS[0])
    kw_list=[k.strip() for k in (st.session_state.get("v9_keywords","")).split(",") if k.strip()]
    eqs_raw=st.session_state.get("v9_selected_eqs") or get_equation_templates(field)[:3]
    return generate_full_manuscript_md(
        title=st.session_state.get("v9_topic") or "Manuscript Title",
        abstract=f"This research focuses on {st.session_state.get('v9_topic','')}. Method: {st.session_state.get('v9_method','')}. Results: {st.session_state.get('v9_quant','')}.",
        keywords=kw_list,
        sections={sec:{"content":f"[{IMRAD_STRUCTURE.get(sec,{}).get('target_words',1950)} kata]","citations":[]} for sec in ["Introduction","Methods","Results","Discussion","Conclusion"]},
        tables=generate_table_template(2),figures=generate_figure_template(3),
        references=[c["apa"] for c in all_c[:50]],equations=eqs_raw[:5],
        topic=st.session_state.get("v9_topic") or "research",field=field)


def _build_prompt(step, matched):
    s=st.session_state
    vy=get_valid_years()
    main_fn=s.get("v9_main_filename") or "[belum]"
    ref_fn=s.get("v11_ref_filename") or "[tidak ada]"
    style_fn=s.get("v11_style_filename") or "[tidak ada]"
    corpus=get_corpus()
    corpus_s=(f"{len(corpus)} file: "+", ".join(f['filename'] for f in corpus)) if corpus else "[kosong]"
    cit_pool=(s.get("v9_citations") or {})
    cit_count=cit_pool.get("total",0)
    quant=s.get("v9_quant","")
    jn=matched["name"] if matched else "belum ditentukan"
    ji=(f"\n  Nama: {matched['name']}\n  Rank: {matched['rank']} · IF {matched.get('if','N/A')}\n  ISSN: {matched['issn']}\n") if matched else ""

    # v14: content ratio + discussion linker
    ratio=s.get("v14_content_ratio",{})
    t_tgt=ratio.get("target_tables",2); g_tgt=ratio.get("target_figures",3)
    titles=s.get("v14_result_titles",{})
    disc_linker=build_discussion_linker_text(titles.get("tables",[]),titles.get("figures",[]))

    # 10 titles
    titles_10=generate_10_titles_q1(
        s.get("v9_topic","topic"), s.get("v9_method","method"),
        s.get("v9_novelty","novelty"), s.get("v9_field","field"))

    base=(
        f"════════════════════════════════════════════\n"
        f"PROMPT {step['id']} v14 — {step['label'].upper()}\n"
        f"Bidang: {s.get('v9_field','[pilih]')} | Tahun sitasi: {vy}\n"
        f"════════════════════════════════════════════\n"
        f"⚠️ CANVAS BARU: Tulis di canvas BARU. JANGAN timpa canvas lama.\n\n"
        f"[DOKUMEN TERLAMPIR]\n"
        f"- Naskah utama       : {main_fn}\n"
        f"- Referensi eksisting: {ref_fn}\n"
        f"- Artikel acuan gaya : {style_fn}\n"
        f"- File data corpus   : {corpus_s}\n"
        f"- Jurnal target      : {s.get('v9_journal_url','[belum]')}{ji}\n\n"
        f"[INFO PENELITIAN — M17+M25]\n"
        f"- Topik   : {s.get('v9_topic','')}\n"
        f"- Metode  : {s.get('v9_method','')}\n"
        f"- Novelty : {s.get('v9_novelty','')}\n"
        f"- Data    : {quant}\n"
        f"- Keywords: {s.get('v9_keywords','')}\n\n"
        f"[SITASI] CrossRef: {cit_count} citations tersedia\n\n"
    )

    if step["id"]=="A":
        return base+(
            "INSTRUKSI A — CANVAS BARU:\n"
            "1. Baca seluruh naskah + corpus file data.\n"
            "2. Ekstrak substansi 1950 kata per bagian IMRAD.\n"
            "3. Setiap paragraf WAJIB ada angka/data kuantitatif.\n"
            "4. Jika data tidak ada → [Tidak ditemukan dalam dokumen].\n"
            "5. Prioritas referensi dari file yang diunggah.\n"
            "6. [M24] Tulis seperti akademisi: variasi kalimat, hedging, aktif 60%.\n"
            "7. Jawab di canvas BARU.")

    if step["id"]=="B":
        return base+(
            f"INSTRUKSI B — CANVAS BARU:\n"
            f"1. Paragraf 250 kata per bagian.\n"
            f"2. {cit_count} sitasi CrossRef tersedia. Prioritas dari '{ref_fn}'.\n"
            f"3. Tahun {vy}. APA 7th per kalimat klaim. DOI valid.\n"
            f"4. [M11] Wajib sitasi setiap section (kecuali Conclusion).\n"
            f"5. Jawab di canvas BARU.")

    if step["id"]=="C":
        style_note=(f"Analisis '{style_fn}': panjang kalimat, rasio aktif/pasif, heading, kepadatan sitasi." if style_fn!="[tidak ada]" else "Standar IMRaD jurnal target.")
        return base+(f"INSTRUKSI C — CANVAS BARU:\n1. {style_note}\n2. Style guide 1 halaman.\n3. Canvas BARU.")

    if step["id"]=="D":
        ref_list="\n".join(f"  {i+1}. {t}" for i,t in enumerate(titles_10)) if titles_10 else "  [Generate berdasarkan topik penelitian]"
        return base+(
            f"════ PROMPT D v14 — BERTAHAP Y/N, CANVAS BARU TIAP STAGE ════\n\n"
            f"⚠️ ATURAN CANVAS BARU:\n"
            f"• Setiap STAGE ditulis di canvas BARU yang terpisah\n"
            f"• JANGAN timpa, JANGAN gabungkan dengan canvas sebelumnya\n"
            f"• Ini karena ada batas penulisan — canvas baru = output bersih\n\n"
            f"═══ STAGE 1 — INTRODUCTION (1950 kata + 12 sitasi) — CANVAS BARU ═══\n"
            f"Sub-heading: 1. Background | 2. Literature Gap | 3. Objectives | 4. Organization\n"
            f"Sitasi APA per kalimat: (Author, Year). Setiap paragraf ada angka.\n"
            f"[M24] Humanlike: variasi kalimat, hedging ('appears to', 'suggests'), aktif 60%.\n"
            f"Setelah selesai: '✅ Introduction selesai — total kata + sitasi. Ketik Y lanjut Methods.'\n\n"
            f"═══ STAGE 2 — METHODS (1950 kata + 10 sitasi) — CANVAS BARU ═══\n"
            f"Sub-heading: 2.1 Design | 2.2 Data | 2.3 Method [NOVELTY] | 2.3.1 Arch | 2.3.2 Impl | 2.4 Evaluation\n"
            f"✅ SATU gambar: desain penelitian / kerangka / flowchart\n"
            f"❌ Tidak ada equation. ❌ Tidak ada tabel data.\n"
            f"Setiap klaim → (Author, Year).\n"
            f"Setelah selesai: '✅ Methods selesai. Ketik Y lanjut Results.'\n\n"
            f"═══ STAGE 3 — RESULTS (1950 kata + 8 sitasi) — CANVAS BARU ═══\n"
            f"Sub-heading: 3.1 Dataset | 3.2 Main Results | 3.2.1 Performance | 3.3 Comparison | 3.4 Statistics\n"
            f"✅ Target: {t_tgt} tabel (40%) + {g_tgt} gambar (60%) dari file upload\n"
            f"✅ SEMUA formula/rumus di sini, urut pembahasan, dengan nama + variabel\n"
            f"✅ Setiap tabel: judul + deskripsi 100 kata + data kuantitatif + sitasi APA\n"
            f"✅ Setiap gambar: judul + deskripsi 100 kata + data kuantitatif + sitasi APA\n"
            f"✅ Table Comparison: Author/Year | Method | Dataset | Metric | Value | Limitation\n"
            f"Setelah selesai: '✅ Results selesai. Ketik Y lanjut Discussion.'\n\n"
            f"═══ STAGE 4 — DISCUSSION (1950 kata + 20 sitasi) — CANVAS BARU ═══\n"
            f"Sub-heading: 4.1 Key Findings | 4.2 SOTA Comparison | 4.3 Novelty | 4.4 Implications | 4.5 Limitations\n"
            f"{disc_linker}\n"
            f"❌ Tidak ada equation, tabel, gambar baru.\n"
            f"Setelah selesai: '✅ Discussion selesai. Ketik Y lanjut Conclusion.'\n\n"
            f"═══ STAGE 5 — CONCLUSION (250 kata) + ABSTRACT + Keywords — CANVAS BARU ═══\n"
            f"CONCLUSION (250 kata TEPAT):\n"
            f"  ✅ WAJIB angka kuantitatif dari Results\n"
            f"  Contoh: 'This study achieves {quant[:60] if quant else 'X% accuracy, Y% F1-score'}.'\n"
            f"  ❌ Tidak ada sitasi. ❌ Tidak ada eq/tabel/gambar.\n\n"
            f"ABSTRACT (250 kata TEPAT):\n"
            f"  Struktur: [1 kalimat background] [2 kalimat methods] [2 kalimat results + angka] [1 kalimat conclusion]\n"
            f"  WAJIB ada angka dari Results.\n\n"
            f"KEYWORDS: 5 kata/frasa dipisah ; (contoh: deep learning; CNN; crop disease; accuracy; classification)\n\n"
            f"Setelah selesai: '✅ Conclusion + Abstract selesai. Generating 10 judul Q1...'\n\n"
            f"═══ STAGE 6 — 10 JUDUL SCOPUS Q1 — CANVAS BARU ═══\n"
            f"Generate 10 judul artikel berbeda, standar Scopus Q1:\n"
            f"Berdasarkan: topik='{s.get('v9_topic','')}', metode='{s.get('v9_method','')}'\n"
            f"Kriteria: ≤18 kata, kata kunci high-impact, bukan pertanyaan, noun phrase akademik\n"
            f"Rekomendasi awal (dapat dimodifikasi):\n{ref_list}\n\n"
            f"═══ STAGE 7 — DAFTAR PUSTAKA / REFERENCES — CANVAS BARU ═══\n"
            f"Susun SEMUA {cit_count} referensi dalam format APA 7th LENGKAP:\n"
            f"Format per entri:\n"
            f"  Author, A., & Author, B. (Year). Title. *Journal*, *Vol*(Issue), Pages.\n"
            f"  https://doi.org/XX.XXXX/XXXXXX  [TERVALIDASI]\n\n"
            f"Aturan:\n"
            f"✓ Urutkan alfabetis berdasarkan nama belakang penulis pertama\n"
            f"✓ Setiap entri WAJIB ada DOI https://doi.org/... yang valid\n"
            f"✓ DOI dari CrossRef API yang sudah di-fetch — JANGAN karang\n"
            f"✓ Jika DOI tidak ada → tandai [Perlu verifikasi manual]\n"
            f"✓ Tahun {vy} — tidak ada referensi di luar rentang ini\n\n"
            f"Setelah selesai: '✅ Semua tahap selesai! Draft manuskrip lengkap.'\n\n"
            f"[M10 CITATION] ≥50 sitasi. 10-20% dari {jn}.\n"
            f"[M11] Section kosong → 6 pertanyaan EN di paragraf akhir.\n"
            f"[M24] Seluruh tulisan humanlike, tidak terdeteksi AI detector.\n"
            f"Tanda baca: . , ; : - ? ! \" \" ' ' ( ) [ ] / ...\n"
            f"Tampilkan [CORE QUALITY SCORE v14] di akhir Stage 7.")

    if step["id"]=="E":
        return base+"INSTRUKSI E — CANVAS BARU:\n1. Graphical abstract.\n2. Cover letter spesifik jurnal.\n3. Checklist + CRediT.\n4. Canvas BARU."

    if step["id"]=="F":
        return base+(f"INSTRUKSI F — CANVAS BARU:\nBerdasarkan style guide '{style_fn}':\n1. Sesuaikan format heading jurnal {jn}.\n2. Sesuaikan konvensi tabel/gambar.\n3. Cover letter dengan gaya jurnal target.\n4. Canvas BARU.")

    return base+"Jalankan. Canvas BARU."
