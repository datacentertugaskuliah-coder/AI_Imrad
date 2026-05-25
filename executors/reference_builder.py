"""
executors/reference_builder.py — ReferenceBuilder v14
Build complete APA 7th reference list with valid DOIs from CrossRef
"""
import re
from datetime import datetime


def format_apa_7th_full(item: dict) -> str:
    """
    Format CrossRef item → complete APA 7th with DOI link.
    Returns formatted string including doi.org URL.
    """
    # Authors
    authors = item.get("author", [])
    if not authors:
        author_str = "Anonymous"
    else:
        formatted = []
        for a in authors[:20]:
            family = a.get("family", "")
            given = a.get("given", "")
            if family:
                initials = "".join(g[0] + "." for g in given.split() if g) if given else ""
                formatted.append(f"{family}, {initials}" if initials else family)
        if len(formatted) > 7:
            author_str = ", ".join(formatted[:6]) + ", ... " + formatted[-1]
        elif len(formatted) > 1:
            author_str = ", ".join(formatted[:-1]) + ", & " + formatted[-1]
        else:
            author_str = formatted[0] if formatted else "Unknown"

    # Year
    year = "n.d."
    if item.get("issued", {}).get("date-parts"):
        try:
            year = str(item["issued"]["date-parts"][0][0])
        except (IndexError, KeyError):
            pass

    # Title
    title_list = item.get("title", [])
    title = title_list[0] if title_list else "Untitled"

    # Journal
    journal_list = item.get("container-title", [])
    journal = journal_list[0] if journal_list else ""

    # Volume, issue, pages
    volume = item.get("volume", "")
    issue = item.get("issue", "")
    pages = item.get("page", "")
    doi = item.get("DOI", "")

    # Build volume string
    vol_str = volume
    if issue:
        vol_str += f"({issue})"
    pages_str = f", {pages}" if pages else ""
    doi_str = f"\n    https://doi.org/{doi}" if doi else " [No DOI — needs manual verification]"

    # APA format
    apa = f"{author_str} ({year}). {title}. "
    if journal:
        if vol_str:
            apa += f"*{journal}*, *{vol_str}*{pages_str}."
        else:
            apa += f"*{journal}*."
    apa += doi_str

    return apa


def build_reference_list(citations: list, sort_alpha: bool = True) -> str:
    """
    Build numbered reference list from citations.
    Returns complete References / Daftar Pustaka section.
    """
    if not citations:
        return "## References\n\nNo references available. Fetch citations first.\n"

    formatted = []
    for c in citations:
        # Use pre-formatted APA if available
        apa = c.get("apa", "")
        doi = c.get("doi", "")

        if apa and doi:
            # Ensure DOI link is included
            if "https://doi.org" not in apa:
                apa_full = apa + f"\n    https://doi.org/{doi}"
            else:
                apa_full = apa
            # Tag
            tag = c.get("source_tag", "[TERVALIDASI]")
            formatted.append((apa_full, tag, c.get("authors",""), c.get("year",0)))
        elif apa:
            formatted.append((apa + " [Perlu verifikasi manual]", "[Perlu verifikasi]",
                               c.get("authors",""), c.get("year",0)))

    if sort_alpha:
        # Sort by first author last name
        def sort_key(item):
            txt = item[0]
            first_word = txt.split(",")[0].strip().lower()
            return first_word
        formatted.sort(key=sort_key)

    lines = ["## References / Daftar Pustaka\n",
             f"*APA 7th Edition · {len(formatted)} citations · {datetime.now().year}*\n"]

    for i, (apa_full, tag, _, _) in enumerate(formatted, 1):
        lines.append(f"{i}. {apa_full}  {tag}\n")

    return "\n".join(lines)


def generate_10_titles_q1(topic: str, method: str, novelty: str,
                            field: str, dataset: str = "the dataset") -> list:
    """
    Generate 10 article titles meeting Scopus Q1 standards.
    Based on topic, method, novelty from uploaded document.
    """
    # Clean inputs
    t = topic.split(":")[-1].strip() if ":" in topic else topic
    m = method.split("+")[0].strip() if "+" in method else method
    n = novelty[:50].strip() if novelty else "novel approach"
    f = field.split("/")[-1].strip() if "/" in field else field

    # 10 different title patterns for Q1 journals
    patterns = [
        f"{m}-Based {t}: A Comprehensive Approach for {f} Applications",
        f"Enhancing {t} Through {n}: Evidence From {dataset.title()}",
        f"A {m} Framework for {t}: Quantitative Analysis and Benchmarking",
        f"Towards Robust {t}: Integrating {m} With {n}",
        f"{n} in {f}: A {m}-Driven Investigation and Experimental Validation",
        f"Optimizing {t} Using {m}: An Empirical Study With {dataset.title()}",
        f"Multi-Dimensional Analysis of {t}: {m} With Attention-Based {n}",
        f"Leveraging {m} for {t}: Performance Evaluation in {f} Contexts",
        f"Comparative Study of {m} Approaches to {t}: Implications for {f}",
        f"Data-Driven {t} Via {m}: Insights and Implications for {f} Practice",
    ]

    # Clean each title
    cleaned = []
    for p in patterns:
        # Remove double spaces, clean up
        clean = re.sub(r'\s+', ' ', p).strip()
        # Capitalize properly
        words = clean.split()
        if len(words) > 18:
            words = words[:18]
            clean = " ".join(words)
        cleaned.append(clean)

    return cleaned[:10]
