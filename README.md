# Research Workflow Dashboard v9
**Core IMRAD Intelligence v9 · 22 Modules · 7 REAL Executors · ZERO-CLICK Auto-Fill**

## What's new in v9 (HONEST CHANGES vs v8)
1. **ZERO-CLICK auto-fill**: upload PDF → 5 field langsung terisi, tanpa klik tombol "Extract"
2. **M21 CrossRef API**: sitasi dari `api.crossref.org` — DOI nyata + APA 7th, bukan placeholder
3. **M22 Context-Aware Equation**: scan keyword di naskah → pilih equation RELEVAN dengan skor
4. **REAL MD generator**: `.md` berisi sitasi aktual dari CrossRef (jika di-fetch)
5. **Dynamic year**: `datetime.now().year - 2` (auto-update tiap tahun)

## Deploy
```
unzip research_workflow_streamlit_v9.zip
cd research_workflow
rm .streamlit/secrets.toml   # JANGAN push ke GitHub
git init && git add . && git commit -m "v9 ZERO-CLICK + CrossRef"
git remote add origin <your-repo>
git push -u origin main
```
Di share.streamlit.io → Settings → Secrets → set `ACCESS_KEY = "your_password"`

## Test ZERO-CLICK
1. Upload naskah PDF/DOCX/TXT
2. Lihat 5 field "Informasi Penelitian" — LANGSUNG TERISI
3. Set Link jurnal target → klik "Fetch REAL Citations"
4. Sistem query CrossRef API → daftar DOI valid
5. Buka tab Prompt D → klik "Template .md" → file ter-download dengan sitasi nyata
