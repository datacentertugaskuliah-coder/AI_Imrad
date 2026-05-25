"""
executors/auto_extractor.py — M13 NYATA v8
Algoritma extraction: regex + section-based + frequency analysis
"""
import re
from collections import Counter


def extract_topic(sections: dict) -> tuple[str, float]:
    """Extract topic/title. Returns (topic, confidence)."""
    if "title" in sections and sections["title"]:
        return sections["title"].strip(), 0.9

    if "abstract" in sections:
        # First 30 words of abstract
        abstract = sections["abstract"]
        words = abstract.split()[:30]
        return " ".join(words), 0.6

    return "[Tidak ditemukan]", 0.0


def extract_method(sections: dict) -> tuple[str, float]:
    """Extract method/algorithm. Returns (method, confidence)."""
    if "method" not in sections:
        return "[Tidak ditemukan dalam dokumen]", 0.0

    method_text = sections["method"]
    # Find sentences mentioning approach/algorithm/model
    sentences = re.split(r"(?<=[.!?])\s+", method_text)
    keywords = ["using", "approach", "algorithm", "model", "method",
                "berdasarkan", "menggunakan", "metode", "pendekatan"]

    relevant = []
    for sent in sentences[:20]:
        if any(kw in sent.lower() for kw in keywords):
            relevant.append(sent.strip())

    if relevant:
        # Take first 2 most relevant sentences
        return " ".join(relevant[:2])[:300], 0.8

    # Fallback: first 200 chars after method heading
    return method_text[100:400].strip(), 0.5


def extract_novelty(sections: dict) -> tuple[str, float]:
    """Extract novelty statement. Returns (novelty, confidence)."""
    text = sections.get("_full_text", "")
    if "novelty" in sections:
        return sections["novelty"][:300], 0.85

    # Search whole text for novelty patterns
    patterns = [
        r"(novelty[^\.]{20,200}\.)",
        r"(kebaruan[^\.]{20,200}\.)",
        r"(propose[^\.]{20,200}\.)",
        r"(first time[^\.]{20,200}\.)",
        r"(novel[^\.]{20,200}\.)",
        r"(contribution[^\.]{20,200}\.)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), 0.7

    return "[Tidak ditemukan dalam dokumen — perlu dilengkapi penulis]", 0.0


def extract_quant_data(sections: dict) -> tuple[str, float]:
    """Extract quantitative data. Returns (data, confidence)."""
    text = sections.get("_full_text", "")
    if not text:
        return "[Tidak ditemukan]", 0.0

    # Pattern: number + unit
    patterns = [
        (r"(\d+\.?\d*)\s*(%)",              "%"),
        (r"accuracy[:\s]+(\d+\.?\d*)",      "accuracy"),
        (r"precision[:\s]+(\d+\.?\d*)",     "precision"),
        (r"recall[:\s]+(\d+\.?\d*)",        "recall"),
        (r"F1[\s-]*score[:\s]+(\d+\.?\d*)", "F1"),
        (r"AUC[:\s]+(\d+\.?\d*)",           "AUC"),
        (r"R[²2][:\s]+(\d+\.?\d*)",         "R²"),
        (r"p[\s-]*value[:\s]+(\d+\.?\d*)",  "p-value"),
        (r"(\d+\.?\d*)\s*kg",                "kg"),
        (r"(\d+\.?\d*)\s*meter",             "meter"),
    ]

    findings = []
    for pattern, unit in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches[:3]:
            val = m if isinstance(m, str) else m[0] if m else ""
            if val:
                findings.append(f"{unit}={val}")

    if findings:
        # Deduplicate, take top 8
        unique = list(dict.fromkeys(findings))[:8]
        return ", ".join(unique), 0.85

    return "[Tidak ditemukan data kuantitatif eksplisit]", 0.0


def extract_keywords(sections: dict, top_n: int = 5) -> tuple[str, float]:
    """Extract keywords. Returns (keywords, confidence)."""
    # 1. Explicit keywords section
    if "keywords" in sections:
        kw_text = sections["keywords"]
        # Try common separators
        for sep in [";", ",", "·", "•"]:
            if sep in kw_text:
                parts = [p.strip() for p in kw_text.split(sep) if 3 < len(p.strip()) < 50]
                if 3 <= len(parts) <= 10:
                    return ", ".join(parts[:top_n]), 0.95
        # Fallback: take first 200 chars
        return kw_text[:200].strip(), 0.7

    # 2. Frequency-based fallback
    text = sections.get("_full_text", "")
    if not text:
        return "[Tidak ditemukan]", 0.0

    # Remove common stopwords (EN + ID basic)
    stopwords = set("""a an the and or of in on at to from for by with as is are was were be been being
        this that these those it its their this they we us our you your i my me
        di dan atau dari dengan untuk pada ke yang adalah ini itu juga akan dapat tidak
        bahwa karena oleh para sebagai jika sebuah suatu telah""".split())

    words = re.findall(r"\b[a-zA-Z]{4,15}\b", text.lower())
    filtered = [w for w in words if w not in stopwords]
    counter = Counter(filtered)
    top_words = [w for w, _ in counter.most_common(top_n)]
    if top_words:
        return ", ".join(top_words), 0.5

    return "[Tidak dapat diekstrak]", 0.0


def auto_extract_all(sections: dict) -> dict:
    """Extract all 5 fields. Returns dict with values and confidences."""
    topic, c_topic     = extract_topic(sections)
    method, c_method   = extract_method(sections)
    novelty, c_novelty = extract_novelty(sections)
    quant, c_quant     = extract_quant_data(sections)
    keywords, c_kw     = extract_keywords(sections)

    return {
        "topic":      {"value": topic,    "confidence": c_topic},
        "method":     {"value": method,   "confidence": c_method},
        "novelty":    {"value": novelty,  "confidence": c_novelty},
        "quant_data": {"value": quant,    "confidence": c_quant},
        "keywords":   {"value": keywords, "confidence": c_kw},
    }
