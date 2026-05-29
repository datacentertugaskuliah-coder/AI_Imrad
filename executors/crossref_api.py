"""
executors/crossref_api.py — REAL citation fetcher v9
Algoritma: query CrossRef public API → DOI valid + APA 7th
"""
import re
from datetime import datetime


def _format_authors_apa(author_list: list) -> str:
    """Format authors in APA 7th."""
    if not author_list:
        return "Unknown"
    formatted = []
    for a in author_list[:20]:
        family = a.get("family", "")
        given = a.get("given", "")
        if family:
            initials = ".".join([g[0] for g in given.split() if g]) + "." if given else ""
            formatted.append(f"{family}, {initials}")
    if len(formatted) > 7:
        return ", ".join(formatted[:6]) + ", ... " + formatted[-1]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def _format_apa(item: dict) -> str:
    """Format CrossRef item → APA 7th citation string."""
    authors = _format_authors_apa(item.get("author", []))
    year = ""
    if "issued" in item and item["issued"].get("date-parts"):
        try:
            year = str(item["issued"]["date-parts"][0][0])
        except (IndexError, KeyError):
            year = "n.d."
    title = item.get("title", [""])[0] if item.get("title") else ""
    journal = item.get("container-title", [""])[0] if item.get("container-title") else ""
    volume = item.get("volume", "")
    issue = item.get("issue", "")
    pages = item.get("page", "")
    doi = item.get("DOI", "")

    vol_str = volume
    if issue: vol_str += f"({issue})"
    pages_str = f", {pages}" if pages else ""
    doi_str = f". https://doi.org/{doi}" if doi else ""

    return f"{authors} ({year}). {title}. {journal}, {vol_str}{pages_str}{doi_str}"


def fetch_citations_crossref(query: str, year_min: int = None, year_max: int = None,
                               rows: int = 20, issn: str = None) -> list:
    """
    REAL fetch dari CrossRef API.
    Returns list of citation dicts with APA, DOI, year.
    """
    try:
        import requests
    except ImportError:
        return []

    if year_min is None:
        cy = datetime.now().year
        year_min = cy - 2
        year_max = cy

    params = {
        "query.bibliographic": query[:500],
        "rows": min(rows, 100),
        "filter": f"from-pub-date:{year_min},until-pub-date:{year_max},type:journal-article",
        "select": "DOI,title,author,container-title,issued,volume,issue,page,ISSN",
    }
    if issn:
        params["filter"] += f",issn:{issn}"

    try:
        r = requests.get("https://api.crossref.org/works", params=params, timeout=15,
                          headers={"User-Agent": "ResearchWorkflowV9 (mailto:research@example.com)"})
        if r.status_code != 200:
            return []
        data = r.json()
        items = data.get("message", {}).get("items", [])
    except Exception:
        return []

    citations = []
    for item in items:
        doi = item.get("DOI", "")
        if not doi: continue
        try:
            year = item["issued"]["date-parts"][0][0]
            if year < year_min or year > year_max:
                continue
        except (KeyError, IndexError):
            continue

        title_list = item.get("title", [])
        journal_list = item.get("container-title", [])

        # Blacklist filter (Frontiers, Hindawi)
        journal_name = journal_list[0] if journal_list else ""
        if any(b.lower() in journal_name.lower() for b in ["frontiers", "hindawi"]):
            continue

        citations.append({
            "doi": doi,
            "title": title_list[0] if title_list else "",
            "journal": journal_name,
            "year": year,
            "authors": _format_authors_apa(item.get("author", [])),
            "apa": _format_apa(item),
            "url": f"https://doi.org/{doi}",
            "verified": True,
            "source": "CrossRef",
        })

    return citations


def fetch_from_journal(issn: str, query: str = "", rows: int = 10,
                        year_min: int = None) -> list:
    """Fetch citations from specific journal by ISSN."""
    return fetch_citations_crossref(query, year_min=year_min, rows=rows, issn=issn)


def deduplicate(citations: list) -> list:
    """Remove duplicates by DOI."""
    seen = set()
    unique = []
    for c in citations:
        if c["doi"] and c["doi"] not in seen:
            seen.add(c["doi"])
            unique.append(c)
    return unique


def build_citation_pool(topic: str, journal_issn: str = None,
                         min_total: int = 50,
                         target_journal_count: int = 10) -> dict:
    """
    Build complete citation pool v15.
    Strategy: BASE 50 sitasi umum + 20% × 50 = 10 dari jurnal target = 60 total.
    Returns dict with stats and breakdown.
    """
    cy = datetime.now().year
    year_min = cy - 2

    result = {"target_journal": [], "general": [], "total": 0,
               "errors": [], "config": {
                   "base": min_total, "target_count": target_journal_count,
                   "target_ratio": 0.20, "total_target": min_total + target_journal_count,
               }}

    # 1. Target journal citations — FETCH DULU (10 sitasi)
    if journal_issn:
        # Fetch slightly more for buffer (CrossRef may return fewer)
        target_cits = fetch_from_journal(journal_issn, topic,
                                          rows=target_journal_count + 5,
                                          year_min=year_min)
        target_cits = deduplicate(target_cits)[:target_journal_count]
        # Tag setiap citation
        for c in target_cits:
            c["source_tag"] = "[TARGET-JOURNAL][TERVALIDASI]"
        result["target_journal"] = target_cits

    # 2. General citations — fetch sisa untuk lengkapi 50
    general_needed = min_total + 10  # buffer untuk dedup
    general = fetch_citations_crossref(topic, year_min, cy, general_needed)
    general = deduplicate(general)
    # Exclude duplicates of target
    target_dois = {c["doi"] for c in result["target_journal"]}
    general_filtered = [c for c in general if c["doi"] not in target_dois]
    general_filtered = general_filtered[:min_total]
    for c in general_filtered:
        c["source_tag"] = "[CORE-DB][TERVALIDASI]"
    result["general"] = general_filtered

    result["total"] = len(result["target_journal"]) + len(result["general"])
    return result
