"""
core/data.py — Core IMRAD Intelligence v14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+99% dari v13 — 27 modul (5 modul executor nyata baru + upgrade semua rules)
v14 KEY CHANGES:
  - Results: 40% tabel / 60% gambar dari file upload (M23 upgrade)
  - Discussion: WAJIB referensi judul Table/Figure dari Results
  - Target kata: 1950 per section (naik dari 1750)
  - Prompt D: SELALU canvas baru + APA setiap section
  - Conclusion: angka dari hasil + 250 kata
  - Abstract: 250 kata + 5 keyword dipisah ;
  - 10 judul Q1 otomatis
  - References/Daftar Pustaka APA + DOI valid dari CrossRef
  - Humanlike writing anti-AI-detector
"""
from datetime import datetime

FIELDS = ["Saintek", "Komputer / AI", "Sosial & Humaniora", "Umum"]

def get_valid_years():
    cy = datetime.now().year
    return list(range(cy - 2, cy + 1))

CITATION_CONFIG = {
    "min_total": 50,                # v15: base 50 sitasi umum
    "target_journal_count": 10,     # v15: +20% × 50 = 10 dari jurnal target
    "total_target": 60,             # v15: 50 + 10 = 60 sitasi total
    "max_year_old": 3, "style": "APA 7th edition",
    "target_journal_ratio": 0.20,   # v15: fixed 20% (bukan range)
    "deduplication": True, "doi_validation": "required",
    "blacklist_publishers": ["Frontiers", "Hindawi"],
    "mdpi_exception": "Sustainability (SDGs only)",
    "fallback_questions": 6, "conclusion_exempted": True,
    "words_per_section": 1950,
    "results_table_ratio": 0.40,
    "results_figure_ratio": 0.60,
}



SECTION_FALLBACK_TEMPLATES = {
    "Introduction": [
        "What are the recent trends and challenges in {topic} as reported in 2022–{year} literature?",
        "How does {topic} address the knowledge gap identified in prior {field} studies?",
        "What theoretical frameworks are most influential in recent {topic} research?",
        "What empirical evidence supports the significance of {topic} in {field}?",
        "How have researchers conceptualized the main problem in {topic} over the past three years?",
        "What policy relevance and global impact does {topic} hold according to recent publications?",
    ],
    "Methods": [
        "What validated methodological approaches are applied for {topic} in 2022–{year}?",
        "What datasets and benchmark protocols are standard for {topic} evaluation?",
        "How do researchers ensure reproducibility and bias control in {topic} experiments?",
        "What sample size and validation techniques are recommended for {topic} studies?",
        "Which statistical or analytical frameworks best fit the research design of {topic}?",
        "How have recent {topic} studies addressed methodological limitations?",
    ],
    "Results": [
        "What benchmark metrics are typically reported in {topic} studies (2022–{year})?",
        "How do comparable {topic} studies present quantitative findings in tables and figures?",
        "What effect sizes or accuracy ranges appear in recent {topic} experiments?",
        "How do leading {topic} studies structure result tables for comparison purposes?",
        "What statistical significance thresholds are conventional in {topic} reporting?",
        "How are confidence intervals and uncertainty bounds quantified in {topic} research?",
    ],
    "Discussion": [
        "How do recent {topic} findings compare with theoretical predictions in the literature?",
        "What practical implications of {topic} have been highlighted by systematic reviews?",
        "What consistent limitations are acknowledged across {topic} research articles?",
        "How does this work extend or challenge existing {topic} paradigms?",
        "What future research directions are most frequently recommended in {topic} discussions?",
        "What ethical or policy considerations arise from advances in {topic}?",
    ],
}

def generate_fallback_questions(section: str, topic: str="[topik]", field: str="[bidang]"):
    if section.lower() == "conclusion": return []
    cy = str(datetime.now().year)
    tpl = SECTION_FALLBACK_TEMPLATES.get(section, SECTION_FALLBACK_TEMPLATES["Introduction"])
    return [q.format(topic=topic, field=field, year=cy) for q in tpl]

EQUATION_TEMPLATES = {
    "Saintek": [
        {"name":"Linear Regression","latex":r"y=\beta_0+\beta_1 x+\varepsilon","desc":"Regresi linear"},
        {"name":"Standard Deviation","latex":r"\sigma=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i-\mu)^2}","desc":"Simpangan baku"},
        {"name":"Energy Efficiency","latex":r"\eta=\frac{W_{out}}{Q_{in}}\times 100\%","desc":"Efisiensi energi"},
    ],
    "Komputer / AI": [
        {"name":"Cross-Entropy Loss","latex":r"L=-\sum_{i=1}^{N}y_i\log(\hat{y}_i)","desc":"Loss function"},
        {"name":"F1-Score","latex":r"F_1=2\cdot\frac{P\cdot R}{P+R}","desc":"Harmonic mean P & R"},
        {"name":"Sigmoid","latex":r"\sigma(x)=\frac{1}{1+e^{-x}}","desc":"Fungsi aktivasi"},
        {"name":"Gradient Descent","latex":r"\theta_{t+1}=\theta_t-\alpha\nabla L(\theta_t)","desc":"Update parameter"},
    ],
    "Sosial & Humaniora": [
        {"name":"Cronbach Alpha","latex":r"\alpha=\frac{K}{K-1}\left(1-\frac{\sum\sigma_i^2}{\sigma_T^2}\right)","desc":"Reliabilitas"},
        {"name":"Pearson r","latex":r"r=\frac{\sum(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum(x_i-\bar{x})^2\sum(y_i-\bar{y})^2}}","desc":"Korelasi Pearson"},
        {"name":"Chi-Square","latex":r"\chi^2=\sum_{i=1}^{k}\frac{(O_i-E_i)^2}{E_i}","desc":"Uji chi-kuadrat"},
    ],
    "Umum": [
        {"name":"Sample Mean","latex":r"\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i","desc":"Rata-rata"},
        {"name":"Z-Score","latex":r"z=\frac{x-\mu}{\sigma}","desc":"Standardisasi"},
    ],
}

def get_equation_templates(field: str):
    return EQUATION_TEMPLATES.get(field, EQUATION_TEMPLATES["Umum"])

AUTO_EXTRACT_FIELDS = {
    "topic":     {"label":"Topik/judul","hint":"Dari halaman judul/abstrak"},
    "method":    {"label":"Metode utama","hint":"Dari Methods section"},
    "novelty":   {"label":"Novelty","hint":"Dari pernyataan kebaruan"},
    "quant_data":{"label":"Data kuantitatif","hint":"Dari Results/file data (angka)"},
    "keywords":  {"label":"Keywords","hint":"Dari section Keywords atau TF-IDF"},
}

PLACEMENT_RULES = {
    "Introduction": {"equations":False,"tables":False,"figures":False,
                     "note":"Tidak ada equation, tabel, gambar."},
    "Methods":      {"equations":False,"tables":False,"figures":True,
                     "figure_type":"research_design_only",
                     "note":"HANYA gambar desain/kerangka penelitian."},
    "Results":      {"equations":True,"tables":True,"figures":True,
                     "table_ratio":0.40,"figure_ratio":0.60,
                     "note":"SEMUA formula. Tabel 40% + Gambar 60% dari file upload. 100 kata/deskripsi + data + sitasi."},
    "Discussion":   {"equations":False,"tables":False,"figures":False,
                     "must_ref_results":True,
                     "note":"WAJIB referensi ke judul Table/Figure dari Results. Tidak ada eq/tabel/gambar baru."},
    "Conclusion":   {"equations":False,"tables":False,"figures":False,
                     "must_have_numbers":True,
                     "note":"Tidak ada eq/tabel/gambar. WAJIB angka dari hasil. 250 kata."},
}

IMRAD_STRUCTURE = {
    "Introduction": {
        "target_words": 1950,
        "sub_sections": [
            "1. Background and Motivation",
            "2. Literature Review and Knowledge Gap",
            "3. Research Objectives and Contributions",
            "4. Paper Organization",
        ],
        "note": "Tidak ada equation, tabel, gambar.",
    },
    "Methods": {
        "target_words": 1950,
        "sub_sections": [
            "2.1 Research Design and Framework",
            "2.2 Data Collection and Dataset Description",
            "2.3 Proposed Method [NOVELTY — sub-heading wajib]",
            "    2.3.1 Algorithm / Model Architecture",
            "    2.3.2 Implementation Details",
            "2.4 Evaluation Protocol and Metrics",
        ],
        "note": "SATU gambar desain/kerangka penelitian. Tidak ada equation. Tidak ada tabel data.",
    },
    "Results": {
        "target_words": 1950,
        "sub_sections": [
            "3.1 Dataset Characteristics",
            "3.2 Main Performance Results",
            "    3.2.1 Primary Metric Analysis",
            "    3.2.2 Ablation Study / Sensitivity Analysis",
            "3.3 Comparison With Previous Research",
            "3.4 Statistical Significance",
        ],
        "note": "40% tabel + 60% gambar dari file. SEMUA formula. 100 kata deskripsi + data + sitasi.",
    },
    "Discussion": {
        "target_words": 1950,
        "sub_sections": [
            "4.1 Interpretation of Key Findings [WAJIB ref Table/Figure]",
            "4.2 Comparison With State-of-the-Art",
            "4.3 Novelty and Theoretical Contribution",
            "4.4 Practical Implications",
            "4.5 Limitations and Future Directions",
        ],
        "note": "WAJIB referensi ke judul Table/Figure Results. Tidak ada eq/tabel/gambar baru.",
    },
    "Conclusion": {
        "target_words": 250,
        "sub_sections": [],
        "note": "WAJIB angka kuantitatif dari Results. 250 kata. Tidak ada eq/tabel/gambar.",
    },
}

JOURNAL_DB = [
    {"name":"Computers and Electronics in Agriculture","publisher":"Elsevier","rank":"Q1","if":8.3,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek"],"issn":"0168-1699","url":"https://www.sciencedirect.com/journal/computers-and-electronics-in-agriculture","scope":"Teknologi pertanian","doi_prefix":"10.1016/j.compag","note":"SJR Q1"},
    {"name":"Bioresource Technology","publisher":"Elsevier","rank":"Q1","if":11.4,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek"],"issn":"0960-8524","url":"https://www.sciencedirect.com/journal/bioresource-technology","scope":"Bioenergi","doi_prefix":"10.1016/j.biortech","note":"SJR Q1"},
    {"name":"Journal of Cleaner Production","publisher":"Elsevier","rank":"Q1","if":11.1,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek","Umum"],"issn":"0959-6526","url":"https://www.sciencedirect.com/journal/journal-of-cleaner-production","scope":"Keberlanjutan","doi_prefix":"10.1016/j.jclepro","note":"SJR Q1"},
    {"name":"Renewable and Sustainable Energy Reviews","publisher":"Elsevier","rank":"Q1","if":16.8,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek"],"issn":"1364-0321","url":"https://www.sciencedirect.com/journal/renewable-and-sustainable-energy-reviews","scope":"Energi terbarukan","doi_prefix":"10.1016/j.rser","note":"SJR Q1"},
    {"name":"Expert Systems with Applications","publisher":"Elsevier","rank":"Q1","if":8.5,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"0957-4174","url":"https://www.sciencedirect.com/journal/expert-systems-with-applications","scope":"Sistem pakar AI","doi_prefix":"10.1016/j.eswa","note":"SJR Q1"},
    {"name":"Pattern Recognition","publisher":"Elsevier","rank":"Q1","if":8.0,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"0031-3203","url":"https://www.sciencedirect.com/journal/pattern-recognition","scope":"Computer vision","doi_prefix":"10.1016/j.patcog","note":"SJR Q1"},
    {"name":"Information Fusion","publisher":"Elsevier","rank":"Q1","if":18.6,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"1566-2535","url":"https://www.sciencedirect.com/journal/information-fusion","scope":"Fusi data","doi_prefix":"10.1016/j.inffus","note":"SJR Q1"},
    {"name":"IEEE Transactions on Neural Networks","publisher":"IEEE","rank":"Q1","if":14.3,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"2162-237X","url":"https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5962385","scope":"Neural network","doi_prefix":"10.1109/TNNLS","note":"SJR Q1"},
    {"name":"Knowledge-Based Systems","publisher":"Elsevier","rank":"Q1","if":8.8,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"0950-7051","url":"https://www.sciencedirect.com/journal/knowledge-based-systems","scope":"Knowledge engineering","doi_prefix":"10.1016/j.knosys","note":"SJR Q1"},
    {"name":"Applied Soft Computing","publisher":"Elsevier","rank":"Q1","if":8.7,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI"],"issn":"1568-4946","url":"https://www.sciencedirect.com/journal/applied-soft-computing","scope":"Soft computing","doi_prefix":"10.1016/j.asoc","note":"SJR Q1"},
    {"name":"IEEE Access","publisher":"IEEE","rank":"Q1","if":3.9,"apc":True,"apc_usd":1950,"apc_label":"APC $1,950","fields":["Komputer / AI","Saintek"],"issn":"2169-3536","url":"https://ieeeaccess.ieee.org","scope":"Multidisiplin","doi_prefix":"10.1109/ACCESS","note":"Diamond OA"},
    {"name":"Computers in Human Behavior","publisher":"Elsevier","rank":"Q1","if":9.9,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Sosial & Humaniora"],"issn":"0747-5632","url":"https://www.sciencedirect.com/journal/computers-in-human-behavior","scope":"Teknologi perilaku","doi_prefix":"10.1016/j.chb","note":"SJR Q1"},
    {"name":"International Journal of Information Management","publisher":"Elsevier","rank":"Q1","if":21.0,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Sosial & Humaniora"],"issn":"0268-4012","url":"https://www.sciencedirect.com/journal/international-journal-of-information-management","scope":"Manajemen informasi","doi_prefix":"10.1016/j.ijinfomgt","note":"SJR Q1"},
    {"name":"Heliyon","publisher":"Cell Press / Elsevier","rank":"Q1","if":4.0,"apc":True,"apc_usd":2100,"apc_label":"APC $2,100","fields":["Sosial & Humaniora","Saintek","Umum"],"issn":"2405-8440","url":"https://www.cell.com/heliyon","scope":"Multidisiplin","doi_prefix":"10.1016/j.heliyon","note":"Diamond OA"},
    {"name":"PLOS ONE","publisher":"PLOS","rank":"Q1","if":3.7,"apc":True,"apc_usd":1931,"apc_label":"APC $1,931","fields":["Sosial & Humaniora","Saintek","Umum"],"issn":"1932-6203","url":"https://journals.plos.org/plosone","scope":"Multidisiplin","doi_prefix":"10.1371/journal.pone","note":"OA"},
    {"name":"Nature Communications","publisher":"Nature Portfolio","rank":"Q1","if":16.6,"apc":True,"apc_usd":6290,"apc_label":"APC $6,290","fields":["Umum"],"issn":"2041-1723","url":"https://www.nature.com/ncomms","scope":"Sains","doi_prefix":"10.1038/s41467","note":"Diamond OA"},
    {"name":"Science of the Total Environment","publisher":"Elsevier","rank":"Q1","if":9.8,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Umum","Saintek"],"issn":"0048-9697","url":"https://www.sciencedirect.com/journal/science-of-the-total-environment","scope":"Lingkungan","doi_prefix":"10.1016/j.scitotenv","note":"SJR Q1"},
    {"name":"Indonesian Journal of Electrical Engineering and Computer Science","publisher":"IAES","rank":"Q3","if":None,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek","Komputer / AI"],"issn":"2502-4752","url":"https://ijeecs.iaescore.com","scope":"Teknik elektro","doi_prefix":"10.11591/ijeecs","note":"Scopus Q3"},
    {"name":"JNTETI","publisher":"UGM","rank":"SINTA1","if":None,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Saintek","Komputer / AI"],"issn":"2301-4156","url":"https://jnteti.te.ugm.ac.id","scope":"Teknik elektro TI","doi_prefix":"10.22146/jnteti","note":"SINTA 1"},
    {"name":"Jurnal RESTI","publisher":"IAII","rank":"SINTA2","if":None,"apc":False,"apc_usd":0,"apc_label":"No APC","fields":["Komputer / AI","Saintek"],"issn":"2580-0760","url":"https://jurnal.iaii.or.id/index.php/RESTI","scope":"Sistem informasi","doi_prefix":"10.29207/resti","note":"SINTA 2"},
]

PUBLISHER_BLACKLIST = ["Frontiers","Hindawi"]

def get_journals(ranks=None, fields=None, apc=None, max_apc_usd=None, enforce_blacklist=True):
    r = JOURNAL_DB[:]
    if enforce_blacklist: r=[j for j in r if not any(b in j["publisher"] for b in PUBLISHER_BLACKLIST)]
    if ranks:  r=[j for j in r if j["rank"] in ranks]
    if fields: r=[j for j in r if any(f in j["fields"] for f in fields)]
    if apc is not None: r=[j for j in r if j["apc"]==apc]
    if max_apc_usd is not None: r=[j for j in r if j["apc_usd"]<=max_apc_usd]
    return r

def apc_split(j): return [x for x in j if not x["apc"]], [x for x in j if x["apc"]]
def check_apc_ratio(j):
    t=len(j)
    if t==0: return 0,0,False
    n=len([x for x in j if not x["apc"]])
    return n,t-n,abs(n/t-0.6)<=0.1

def parse_journal_url(url):
    if not url: return None
    ul=url.lower().strip()
    for j in JOURNAL_DB:
        if (j.get("issn","") in url or j["url"].lower() in ul or
            ul in j["url"].lower() or
            (j.get("doi_prefix","") and j["doi_prefix"].lower() in ul)):
            return j
    return None

WORKFLOW_STEPS = [
    {"id":"A","label":"Ekstraksi substansi naskah","color":"#378ADD","words":1950,
     "requires":["Naskah utama ★"],"optional":["File data","Referensi"],
     "core_modules":["M1","M2","M5","M9","M13","M16","M17","M25"],
     "output":"Substansi 1950 kata + data kuantitatif dari file",
     "detail":"M25 baca file in-memory. M17 zero-click auto-fill. M16 parse naskah."},
    {"id":"B","label":"Pencarian & strukturisasi literatur","color":"#1D9E75","words":0,
     "requires":["Naskah utama ★"],"optional":["Daftar referensi"],
     "core_modules":["M3","M4","M6","M9","M10","M21"],
     "output":"50+ referensi APA + CrossRef REAL + DOI valid",
     "detail":"M10+M21 citation pipeline. CrossRef API. DOI valid + URL aksesibel."},
    {"id":"C","label":"Personalisasi gaya penulisan","color":"#BA7517","words":0,
     "requires":["Naskah utama ★"],"optional":["Artikel jurnal acuan"],
     "core_modules":["M1","M3","M6","M8","M24"],
     "output":"Style guide + M24 humanlike rules",
     "detail":"M8 template per bidang. M24 anti-AI-detector rules."},
    {"id":"D","label":"Draft IMRAD bertahap (Y/N) + 10 judul + Referensi","color":"#639922","words":1950,
     "requires":["Naskah utama ★","Jurnal target ★"],
     "optional":["File data","Referensi"],
     "core_modules":["M1–M27 semua aktif"],
     "output":"IMRAD canvas baru + konfirmasi Y + 10 judul Q1 + Daftar Pustaka APA",
     "detail":"Canvas baru per stage. 1950 kata/section. 40/60 tabel/gambar. Discussion←Results."},
    {"id":"E","label":"Persiapan submit jurnal","color":"#534AB7","words":0,
     "requires":["Draft D ★"],"optional":[],
     "core_modules":["M3","M6","M7","M9"],
     "output":"Cover letter + checklist + CRediT",
     "detail":"M7 cover letter spesifik jurnal."},
    {"id":"F","label":"Personalisasi format jurnal (opsional)","color":"#993556","words":0,
     "requires":["Artikel acuan ★","Draft D ★"],"optional":[],
     "core_modules":["M3","M6","M8","M24"],
     "output":"Format manuskrip sesuai style jurnal",
     "detail":"Aktif HANYA jika artikel acuan diunggah."},
]

IMRAD_SECTIONS = [
    {"label":"Introduction","words":1950,"lit":12,"color":"#378ADD","mandatory_lit":True},
    {"label":"Methods","words":1950,"lit":10,"color":"#1D9E75","mandatory_lit":True},
    {"label":"Results","words":1950,"lit":8,"color":"#BA7517","mandatory_lit":True},
    {"label":"Discussion","words":1950,"lit":20,"color":"#534AB7","mandatory_lit":True},
    {"label":"Conclusion","words":250,"lit":0,"color":"#888780","mandatory_lit":False},
    {"label":"Abstract","words":250,"lit":0,"color":"#B4B2A9","mandatory_lit":False},
]

CORE_MODULES = [
    {"id":"M1","name":"Document Parser","icon":"🔍","color":"#378ADD","desc":"Indeks SELURUH dokumen."},
    {"id":"M2","name":"Integrity Validator","icon":"✅","color":"#1D9E75","desc":"Fakta dilacak. Inkonsistensi → BLOKIR."},
    {"id":"M3","name":"Context Memory","icon":"🧠","color":"#534AB7","desc":"Wariskan antar tahap A→F."},
    {"id":"M4","name":"Literature Engine","icon":"📚","color":"#BA7517","desc":"Evaluasi referensi Scopus/SINTA, DOI valid."},
    {"id":"M5","name":"Anti-Hallucination Guard","icon":"🚫","color":"#E24B4A","desc":"Blokir angka tanpa sumber."},
    {"id":"M6","name":"Quality Scorer","icon":"📊","color":"#639922","desc":"Skor multi-dimensi per section."},
    {"id":"M7","name":"Journal Matcher","icon":"🎯","color":"#0C447C","desc":"60/40 No-APC/APC. No Frontiers/MDPI/Hindawi."},
    {"id":"M8","name":"Adaptive Field Engine","icon":"🔬","color":"#854F0B","desc":"Template per bidang ilmu."},
    {"id":"M9","name":"Field Linearity Checker","icon":"🔗","color":"#993556","desc":"Validasi linearitas topik-metode-jurnal."},
    {"id":"M10","name":"Citation Manager","icon":"📑","color":"#3B6D11","desc":"Pipeline 50+ sitasi APA 7th tahun dinamis."},
    {"id":"M11","name":"Section Citation Gatekeeper","icon":"🚪","color":"#A32D2D","desc":"Wajib sitasi per section. Fallback 6 EN questions."},
    {"id":"M12","name":"Equation Builder LaTeX","icon":"📐","color":"#BA7517","desc":"LaTeX Word-compatible. HANYA di Results."},
    {"id":"M13","name":"Document Auto-Extractor","icon":"⚡","color":"#534AB7","desc":"Auto-extract 5 field dengan confidence."},
    {"id":"M14","name":"Multi-Document Aggregator","icon":"📂","color":"#0C447C","desc":"Multi-file corpus + GDrive folder."},
    {"id":"M15","name":"Markdown Export Engine","icon":"📥","color":"#1D9E75","desc":"Auto-generate .md setelah Prompt D."},
    {"id":"M16","name":"REAL Document Parser","icon":"⚙️","color":"#0C447C","desc":"pypdf + python-docx. Parse PDF/DOCX nyata."},
    {"id":"M17","name":"REAL Auto-Extractor","icon":"🤖","color":"#534AB7","desc":"Regex + TF-IDF. Zero-click auto-fill."},
    {"id":"M18","name":"Google Drive Resolver","icon":"🌐","color":"#3B6D11","desc":"File + Folder URL. Dual fallback."},
    {"id":"M19","name":"One-by-One File Manager","icon":"📋","color":"#BA7517","desc":"Session corpus. Add/remove per file."},
    {"id":"M20","name":"REAL MD Exporter","icon":"📤","color":"#1D9E75","desc":"Generate .md actual + auto-download."},
    {"id":"M21","name":"CrossRef Citation API","icon":"🔗","color":"#A32D2D","desc":"DOI valid nyata. APA 7th otomatis."},
    {"id":"M22","name":"Context-Aware Equation","icon":"🧮","color":"#534AB7","desc":"Keyword scan → equation relevan."},
    {"id":"M23","name":"IMRAD Structure Engine","icon":"📋","color":"#185FA5","desc":"Sub-heading 4 level. 40/60 tabel/gambar Results. Discussion←Results wajib."},
    {"id":"M24","name":"Humanlike Writer","icon":"✍️","color":"#27500A","desc":"Anti-AI-detector. Sentence variety. Active 60%. Hedging. Tanda baca terkontrol."},
    {"id":"M25","name":"Data File Reader","icon":"📊","color":"#633806","desc":"CSV/Excel/PDF in-memory. Extract angka → quant field."},
    {"id":"M26","name":"Staged Prompt Engine","icon":"🔄","color":"#072F5F","desc":"Canvas baru TIAP stage. Y/N confirm. 10 judul Q1. Daftar Pustaka APA+DOI."},
    {"id":"M27","name":"Manuscript Reviewer","icon":"🧑‍⚖️","color":"#6B0000","desc":"Upload IMRAD → Q1 reviewer: score, major/minor, recommendations."},
    {"id":"M28","name":"Session Persistence","icon":"💾","color":"#185FA5",
     "desc":"NEW v15. Export/import JSON untuk backup sesi saat disconnect Streamlit Cloud. 5 info penelitian + jurnal target tersimpan."},
    {"id":"M29","name":"CRediT Form Builder","icon":"👥","color":"#27500A",
     "desc":"NEW v15. Input n_authors + 14 CRediT roles per author. Auto-generate CRediT Statement dengan First Author + Co-Authors untuk Prompt E."},
    {"id":"M30","name":"GDrive Auto-Reader","icon":"🌐","color":"#A32D2D",
     "desc":"NEW v15. Setelah fetch GDrive → otomatis parse + extract quant + auto-assign sebagai naskah utama jika belum ada."},
]

INTEGRITY_RULES = [
    {"type":"block","label":"Angka tanpa sumber dokumen","status":"Blokir"},
    {"type":"block","label":"Referensi / DOI dikarang","status":"Blokir"},
    {"type":"block","label":"Metode diasumsikan tanpa naskah","status":"Blokir"},
    {"type":"block","label":"Inkonsistensi angka antar bagian","status":"Blokir"},
    {"type":"block","label":"Konten generik AI (clichés)","status":"Blokir"},
    {"type":"block","label":"Frontiers / MDPI (non-SDGs) / Hindawi","status":"Blokir"},
    {"type":"block","label":"Sitasi duplikat","status":"Blokir"},
    {"type":"block","label":"Sitasi > 3 tahun dari sekarang","status":"Blokir"},
    {"type":"block","label":"Tabel/Gambar tanpa sumber naskah/data","status":"Blokir"},
    {"type":"block","label":"Discussion tanpa referensi ke Results","status":"Blokir"},
    {"type":"block","label":"Conclusion tanpa angka kuantitatif","status":"Blokir"},
    {"type":"warn","label":"DOI belum diverifikasi","status":"Tandai"},
    {"type":"warn","label":"Confidence auto-extract < 50%","status":"Tandai"},
    {"type":"warn","label":"Kata < 1900 per section","status":"Tandai"},
    {"type":"warn","label":"Tidak ada angka di section","status":"Tandai"},
    {"type":"warn","label":"Ratio tabel/gambar tidak 40/60","status":"Tandai"},
    {"type":"ok","label":"M24 Humanlike writing aktif","status":"Lolos"},
    {"type":"ok","label":"M25 Data kuantitatif dari file","status":"Lolos"},
    {"type":"ok","label":"M26 Canvas baru per stage","status":"Lolos"},
    {"type":"ok","label":"50+ sitasi unik dengan DOI valid","status":"Lolos"},
    {"type":"ok","label":"Daftar Pustaka APA lengkap","status":"Lolos"},
]

SCORES = {"Saintek":[92,88,85,80,75],"Komputer / AI":[90,95,70,82,90],
           "Sosial & Humaniora":[75,65,88,85,70],"Umum":[70,60,72,75,65]}
DIMS = ["Data integrity","Metode kuant.","Statistik","Literatur","Novelty"]

FIELD_MATRIX = {
    "Komponen":["Flowchart","Tabel kuant.","Tabel perbandingan","Uji statistik",
                "Kode/algo","Teori/konsep","Data kualitatif","Etika",
                "Linearitas(M9)","Citation(M10/21)","Gating(M11)","Equation(M12/22)",
                "Auto-Extract(M13/17)","DataFile(M25)","Staged(M26)","Reviewer(M27)"],
    "Saintek":            ["Wajib","Wajib","Wajib","Wajib","Tidak wajib","Parsial","Jarang","Parsial","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib"],
    "Komputer / AI":      ["Wajib","Wajib","Wajib","Opsional","Wajib","Parsial","Jarang","Parsial","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib","Wajib"],
    "Sosial & Humaniora": ["Adaptif","Parsial","Wajib","Wajib","Tidak wajib","Wajib","Dominan","Wajib","Wajib","Wajib","Wajib","Parsial","Wajib","Wajib","Wajib","Wajib"],
    "Umum":               ["Adaptif","Parsial","Wajib","Adaptif","Tidak wajib","Wajib","Adaptif","Adaptif","Wajib","Wajib","Wajib","Adaptif","Wajib","Wajib","Wajib","Wajib"],
}

WORLD_REGIONS = [
    {"region":"Eropa Barat","countries":"UK, Belanda, Jerman","journals":18000,"access":90},
    {"region":"Amerika Utara","countries":"USA, Kanada","journals":15000,"access":88},
    {"region":"Asia Timur","countries":"Cina, Jepang, Korea","journals":12000,"access":80},
    {"region":"Asia Selatan","countries":"India, Pakistan","journals":4500,"access":65},
    {"region":"Timur Tengah","countries":"Arab Saudi, Iran","journals":1800,"access":62},
    {"region":"Amerika Latin","countries":"Brasil, Meksiko","journals":2000,"access":58},
    {"region":"Asia Tenggara","countries":"Indonesia, Malaysia, Thai.","journals":1200,"access":55},
    {"region":"Afrika","countries":"Afrika Selatan, Nigeria","journals":600,"access":38},
]

# Hidden from UI — active in backend
CORE_PROMPT_TEXT = """[Core IMRAD Intelligence v14 — Active in backend]"""
