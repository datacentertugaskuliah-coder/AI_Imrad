"""
executors/equation_selector.py — REAL context-aware equation v9
Algoritma: detect keywords in document → select RELEVANT equations
"""

# Keyword relevance map per equation (for context detection)
EQUATION_RELEVANCE = {
    "Linear Regression":      ["regression", "linear", "predict", "trend", "coefficient", "slope"],
    "Standard Deviation":     ["deviation", "variance", "spread", "dispersion", "variability", "standard"],
    "Energy Efficiency":      ["efficiency", "energy", "thermal", "power", "kwh", "joule"],
    "Cross-Entropy Loss":     ["loss", "neural", "classification", "softmax", "logit", "training"],
    "F1-Score":               ["precision", "recall", "f1", "classification", "evaluation", "performance"],
    "Sigmoid Function":       ["sigmoid", "activation", "logistic", "binary", "probability"],
    "Gradient Descent":       ["gradient", "optimization", "learning rate", "convergence", "backpropagation"],
    "Cronbach Alpha":         ["reliability", "cronbach", "scale", "questionnaire", "instrument", "validity"],
    "Pearson Correlation":    ["correlation", "pearson", "relationship", "association", "bivariate"],
    "Chi-Square Test":        ["chi-square", "categorical", "independence", "contingency", "association"],
    "Sample Mean":            ["mean", "average", "central tendency", "expected value"],
    "Z-Score":                ["z-score", "standardize", "normalize", "outlier", "standardization"],
}


def select_equations_by_context(text: str, all_equations: list,
                                  top_n: int = 5, min_score: int = 1) -> list:
    """
    Select equations relevant to document content.
    Returns top_n equations ranked by relevance score.
    """
    if not text:
        return all_equations[:top_n]

    text_lower = text.lower()
    scored = []

    for eq in all_equations:
        name = eq.get("name", "")
        keywords = EQUATION_RELEVANCE.get(name, [])

        # Count keyword matches in text
        score = 0
        matched_kw = []
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 0:
                score += count
                matched_kw.append(kw)

        # Also check if equation name itself is mentioned
        if name.lower() in text_lower:
            score += 5
            matched_kw.append(f"[name:{name}]")

        scored.append({
            "equation": eq,
            "score": score,
            "matched_keywords": matched_kw,
            "relevance": "high" if score >= 3 else "medium" if score >= 1 else "low"
        })

    # Sort by score descending, filter by min_score
    scored.sort(key=lambda x: -x["score"])
    relevant = [s for s in scored if s["score"] >= min_score]

    if not relevant:
        # Fallback: return top defaults
        return [{"equation": eq, "score": 0, "matched_keywords": [],
                 "relevance": "default"} for eq in all_equations[:top_n]]

    return relevant[:top_n]


def explain_selection(scored_eq: dict) -> str:
    """Generate explanation why equation was selected."""
    eq = scored_eq["equation"]
    score = scored_eq["score"]
    matched = scored_eq["matched_keywords"]

    if score == 0:
        return f"Default selection (no specific keywords matched)"

    return (f"Relevance score: {score} · Matched keywords in document: "
            f"{', '.join(matched[:5])}")
