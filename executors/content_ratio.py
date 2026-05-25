"""
executors/content_ratio.py — ContentRatioCalculator v14
Hitung target 40% tabel / 60% gambar dari file yang diunggah
"""
import re
from io import BytesIO


def count_tables_and_figures(text: str) -> dict:
    """
    Count existing tables and figures mentioned in document.
    Returns ratio-based targets for Results section.
    """
    # Patterns to detect tables
    tbl_patterns = [
        r'[Tt]able\s+\d+', r'[Tt]abel\s+\d+', r'\[TABLE\]',
        r'Tabel\s+\d+', r'Gambar\s+\d+', r'Figure\s+\d+',
    ]
    fig_patterns = [
        r'[Ff]igure\s+\d+', r'[Ff]ig\.\s*\d+', r'[Gg]ambar\s+\d+',
        r'[Gg]rafik\s+\d+', r'[Pp]lot\s+\d+',
    ]

    tables_found = set()
    figures_found = set()

    for p in tbl_patterns:
        for m in re.finditer(p, text):
            tables_found.add(m.group(0).strip().lower())

    for p in fig_patterns:
        for m in re.finditer(p, text):
            figures_found.add(m.group(0).strip().lower())

    n_tables = len(tables_found)
    n_figures = len(figures_found)
    total = n_tables + n_figures

    # Calculate targets based on 40/60 ratio
    if total == 0:
        target_tables = 2   # fallback minimum
        target_figures = 3  # fallback minimum
    else:
        target_tables = max(1, round(total * 0.40))
        target_figures = max(1, round(total * 0.60))

    return {
        "tables_in_doc":  n_tables,
        "figures_in_doc": n_figures,
        "total_found":    total,
        "target_tables":  target_tables,
        "target_figures": target_figures,
        "ratio_tables":   f"{target_tables/(target_tables+target_figures)*100:.0f}%",
        "ratio_figures":  f"{target_figures/(target_tables+target_figures)*100:.0f}%",
        "tables_list":    sorted(tables_found)[:target_tables],
        "figures_list":   sorted(figures_found)[:target_figures],
    }


def extract_table_figure_titles(text: str) -> dict:
    """
    Extract actual titles of tables and figures for Discussion references.
    Returns dict with numbered items.
    """
    result = {"tables": [], "figures": []}

    # Table title patterns (title usually follows "Table N.")
    tbl_title_patterns = [
        r'[Tt]able\s+(\d+)[.\s]+([^\n]{10,80})',
        r'[Tt]abel\s+(\d+)[.\s]+([^\n]{10,80})',
    ]
    fig_title_patterns = [
        r'[Ff]igure\s+(\d+)[.\s]+([^\n]{10,80})',
        r'[Ff]ig\.\s*(\d+)[.\s]+([^\n]{10,80})',
        r'[Gg]ambar\s+(\d+)[.\s]+([^\n]{10,80})',
    ]

    for p in tbl_title_patterns:
        for m in re.finditer(p, text):
            num = m.group(1)
            title = m.group(2).strip().rstrip('.')
            entry = {"number": num, "title": title, "ref": f"Table {num}"}
            if entry not in result["tables"]:
                result["tables"].append(entry)

    for p in fig_title_patterns:
        for m in re.finditer(p, text):
            num = m.group(1)
            title = m.group(2).strip().rstrip('.')
            entry = {"number": num, "title": title, "ref": f"Figure {num}"}
            if entry not in result["figures"]:
                result["figures"].append(entry)

    return result


def build_discussion_linker_text(tables: list, figures: list) -> str:
    """
    Build instruction text for Discussion linking to Results tables/figures.
    """
    lines = ["[M23 Discussion Linker — wajib referensi ke Results]"]
    lines.append("Setiap paragraf Discussion WAJIB menyebut judul Table/Figure dari Results:\n")

    if tables:
        lines.append("Tables yang tersedia di Results:")
        for t in tables:
            lines.append(f"  → {t['ref']}: \"{t['title']}\"")
            lines.append(f"     Contoh: \"The data in {t['ref']} ({t['title']}) "
                          "demonstrates that...\"")
    else:
        lines.append("  → Table 1: [Hasil utama penelitian]")
        lines.append("  → Table 2: [Comparison With Previous Research]")

    if figures:
        lines.append("Figures yang tersedia di Results:")
        for f in figures:
            lines.append(f"  → {f['ref']}: \"{f['title']}\"")
            lines.append(f"     Contoh: \"As illustrated in {f['ref']} ({f['title']}), "
                          "the pattern reveals...\"")
    else:
        lines.append("  → Figure 1: [Grafik performa model]")
        lines.append("  → Figure 2: [Confusion matrix / distribusi data]")

    return "\n".join(lines)
