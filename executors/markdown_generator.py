"""
executors/markdown_generator.py — M15 NYATA v8
Algoritma: generate complete .md from manuscript components
"""
from datetime import datetime


def generate_section_with_fallback(section_name: str, content: str,
                                    citations: list, topic: str = "[topik]",
                                    field: str = "[bidang]") -> str:
    """Generate section markdown with M11 fallback if no citations."""
    md = f"## {section_name}\n\n{content}\n\n"

    if section_name.lower() == "conclusion":
        return md  # Conclusion exempt from citations

    if not citations or len(citations) == 0:
        # M11 fallback: 6 literature search questions
        md += f"### Suggested literature search questions (English)\n"
        md += f"_Tag: [CORE-DB][Tidak digunakan][Tidak ditemukan dalam dokumen]_\n\n"

        questions = _generate_section_questions(section_name, topic, field)
        for i, q in enumerate(questions, 1):
            md += f"{i}. {q}\n"
        md += "\n"
    else:
        md += f"**Citations in this section:** {', '.join(citations[:6])}\n\n"

    return md


def _generate_section_questions(section: str, topic: str, field: str) -> list:
    """Generate 6 fallback questions per section."""
    templates = {
        "Introduction": [
            f"What are the recent trends and challenges in {topic} as discussed in literature from the past 3 years?",
            f"How does {topic} address the existing knowledge gap identified in previous studies?",
            f"What theoretical frameworks have been most influential in recent {topic} research?",
            f"What empirical evidence supports the significance of studying {topic} in {field}?",
            f"How have prior researchers conceptualized the main problem in {topic}?",
            f"What is the global impact and policy relevance of {topic} according to recent publications?",
        ],
        "Methods": [
            f"What methodological approaches are most validated for {topic} in recent studies?",
            f"What datasets and benchmark protocols are standard for {topic} evaluation?",
            f"How do researchers ensure reproducibility and bias control in {topic} experiments?",
            f"What sample size and validation techniques are recommended for {topic}?",
            f"What statistical or analytical frameworks best fit the {topic} research design?",
            f"How have prior {topic} studies addressed methodological limitations?",
        ],
        "Results": [
            f"What benchmark performance metrics are typically reported in {topic} studies?",
            f"How do comparable {topic} studies present their quantitative findings?",
            f"What is the typical effect size or accuracy reported in recent {topic} experiments?",
            f"How do leading {topic} studies visualize and tabulate their results?",
            f"What statistical significance thresholds are conventional in {topic} reporting?",
            f"How are confidence intervals and uncertainty quantified in modern {topic} research?",
        ],
        "Discussion": [
            f"How do recent {topic} findings compare with theoretical predictions in the literature?",
            f"What practical implications of {topic} have been highlighted by recent reviews?",
            f"What limitations and confounding factors have been acknowledged in {topic} research?",
            f"How does this work extend or challenge existing {topic} paradigms?",
            f"What future research directions are recommended in recent {topic} discussions?",
            f"What ethical, societal, or policy considerations arise from advances in {topic}?",
        ],
    }
    return templates.get(section, templates["Introduction"])


def render_table_md(table_title: str, description: str, data_rows: list,
                     citations: list = None) -> str:
    """Render table in Markdown with title, 100-word description, data, citations."""
    md = f"**Table. {table_title}**\n\n"

    # Description (100 words guideline)
    md += f"{description}\n\n"

    # Data table
    if data_rows and len(data_rows) > 0:
        # Header
        headers = data_rows[0].keys() if isinstance(data_rows[0], dict) else range(len(data_rows[0]))
        md += "| " + " | ".join(str(h) for h in headers) + " |\n"
        md += "|" + "|".join(["---"] * len(list(headers))) + "|\n"
        for row in data_rows:
            if isinstance(row, dict):
                md += "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |\n"
            else:
                md += "| " + " | ".join(str(c) for c in row) + " |\n"
        md += "\n"

    if citations:
        md += f"_Citations: {', '.join(citations)}_\n\n"

    return md


def render_figure_md(figure_title: str, description: str,
                      quant_data: str = "", citations: list = None) -> str:
    """Render figure in Markdown with title, 100-word description, data, citations."""
    md = f"**Figure. {figure_title}**\n\n"
    md += f"{description}\n\n"
    if quant_data:
        md += f"**Quantitative data:** {quant_data}\n\n"
    if citations:
        md += f"_Citations: {', '.join(citations)}_\n\n"
    return md


def generate_full_manuscript_md(
    title: str,
    abstract: str,
    keywords: list,
    sections: dict,
    tables: list = None,
    figures: list = None,
    references: list = None,
    equations: list = None,
    topic: str = "research topic",
    field: str = "general",
) -> tuple[str, str]:
    """
    Generate complete manuscript Markdown.
    Returns (markdown_content, suggested_filename).
    """
    md = f"# {title}\n\n"

    # Metadata
    md += f"_Generated by Research Workflow v8 · {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
    md += "---\n\n"

    # Abstract & Keywords
    md += "## Abstract\n\n"
    md += abstract + "\n\n"
    md += f"**Keywords:** {'; '.join(keywords)}\n\n"
    md += "---\n\n"

    # IMRAD sections
    section_order = ["Introduction", "Methods", "Results", "Discussion",
                     "Conclusion"]
    for sec_name in section_order:
        content = sections.get(sec_name, {}).get("content", "")
        citations = sections.get(sec_name, {}).get("citations", [])
        md += generate_section_with_fallback(sec_name, content, citations,
                                              topic, field)

        # Tables for this section
        if tables:
            for tbl in [t for t in tables if t.get("section") == sec_name]:
                md += render_table_md(
                    tbl.get("title", "Untitled"),
                    tbl.get("description", "")[:600],
                    tbl.get("data", []),
                    tbl.get("citations", [])
                )

        # Figures for this section
        if figures:
            for fig in [f for f in figures if f.get("section") == sec_name]:
                md += render_figure_md(
                    fig.get("title", "Untitled"),
                    fig.get("description", "")[:600],
                    fig.get("quant_data", ""),
                    fig.get("citations", [])
                )

    # Equations section
    if equations:
        md += "## Equations\n\n"
        for i, eq in enumerate(equations, 1):
            md += f"**Equation {i}. {eq.get('name', 'Unnamed')}**\n\n"
            md += f"$${eq.get('latex', '')}$$\n\n"
            md += f"{eq.get('desc', '')}\n\n"

    # References
    md += "## References\n\n"
    if references:
        for i, ref in enumerate(references, 1):
            md += f"{i}. {ref}\n"
    else:
        md += "_No references provided yet._\n"

    md += "\n---\n\n"
    md += "_End of manuscript. Core IMRAD Intelligence v8._\n"

    # Filename
    safe_title = "".join(c if c.isalnum() else "_" for c in title[:40]).strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"manuscript_{safe_title}_{timestamp}.md"

    return md, filename


def generate_table_template(num_tables: int = 2) -> list:
    """Generate empty table templates user can fill."""
    return [
        {
            "section": "Results",
            "title": f"Table {i+1}: [Judul tabel sesuai pembahasan]",
            "description": "[Deskripsi 100 kata sesuai pembahasan dokumen. "
                           "Jelaskan apa yang ditampilkan tabel, metode pengumpulan "
                           "data, dan signifikansi temuan. Tuliskan konteks dari "
                           "naskah utama yang mendasari tabel ini. Pastikan data "
                           "kuantitatif yang ditampilkan sesuai dengan file data "
                           "yang diunggah, tanpa modifikasi atau interpolasi.]",
            "data": [
                {"Variable": "Var1", "Value": "[data]", "Unit": "[unit]"},
                {"Variable": "Var2", "Value": "[data]", "Unit": "[unit]"},
            ],
            "citations": ["[Author1, Year]", "[Author2, Year]"],
        }
        for i in range(num_tables)
    ]


def generate_figure_template(num_figures: int = 2) -> list:
    """Generate empty figure templates user can fill."""
    return [
        {
            "section": "Results",
            "title": f"Figure {i+1}: [Judul gambar sesuai pembahasan]",
            "description": "[Deskripsi 100 kata sesuai pembahasan dokumen. "
                           "Jelaskan apa yang ditampilkan gambar, sumbu, legenda, "
                           "dan pola yang dapat diobservasi. Konteks dari naskah "
                           "utama yang mendasari gambar. Pastikan data kuantitatif "
                           "yang ditampilkan sesuai dengan file data yang diunggah, "
                           "tanpa modifikasi atau interpolasi nilai.]",
            "quant_data": "[Angka kunci dari naskah/file data]",
            "citations": ["[Author1, Year]", "[Author2, Year]"],
        }
        for i in range(num_figures)
    ]
