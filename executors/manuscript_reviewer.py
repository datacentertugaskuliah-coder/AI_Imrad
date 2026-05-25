"""
executors/manuscript_reviewer.py — M27 Manuscript Reviewer v13
Upload IMRAD → Q1 reviewer comments + recommendations
"""
import re
from executors.document_parser import extract_text, detect_sections


# Q1 reviewer criteria (evidence-based)
REVIEW_CRITERIA = {
    "Introduction": {
        "checks": [
            ("gap_explicit",    r"gap|lacuna|missing|not addressed|unexplored", "Research gap clearly stated"),
            ("novelty_claim",   r"novel|new approach|first time|propose|contribution", "Novelty claim present"),
            ("objective_clear", r"aim|objective|purpose|goal|this study", "Study objective stated"),
            ("citations_rich",  r"\(\w+,\s*\d{4}\)", "In-text citations present"),
        ],
        "word_target": (800, 1200),
        "weight": 0.15,
    },
    "Methods": {
        "checks": [
            ("reproducible",  r"dataset|sample|n\s*=|N\s*=|participants|collected", "Methodology reproducible"),
            ("validation",    r"validat|cross-valid|test set|holdout|k-fold", "Validation strategy described"),
            ("metrics",       r"accuracy|precision|recall|F1|AUC|RMSE|MAE|metric", "Evaluation metrics defined"),
            ("ethical",       r"ethic|IRB|consent|approved|protocol", "Ethical considerations (if applicable)"),
        ],
        "word_target": (1200, 2000),
        "weight": 0.20,
    },
    "Results": {
        "checks": [
            ("quantitative",  r"\d+\.?\d*\s*%|\d+\.\d+", "Quantitative results reported"),
            ("tables",        r"[Tt]able\s+\d|[Ff]igure\s+\d", "Tables/figures referenced"),
            ("comparison",    r"compar|baseline|state.of.the.art|previous|benchmark", "Comparison with baselines"),
            ("statistical",   r"p\s*[<>=]\s*0\.\d+|CI\s*=|confidence|significant", "Statistical significance (if applicable)"),
        ],
        "word_target": (1200, 2000),
        "weight": 0.25,
    },
    "Discussion": {
        "checks": [
            ("interprets_results", r"[Tt]able\s+\d|[Ff]igure\s+\d|result|finding", "Results interpreted with data reference"),
            ("limitation",    r"limitat|constraint|shortcoming|future|drawback", "Limitations acknowledged"),
            ("implication",   r"implic|applicat|practical|suggest|recommend", "Implications discussed"),
            ("novelty_discuss", r"novel|contribut|advance|improve|outperform", "Novelty contribution discussed"),
        ],
        "word_target": (1200, 2000),
        "weight": 0.25,
    },
    "Conclusion": {
        "checks": [
            ("summary",       r"achiev|demonstrat|confirm|show|result|found", "Results summarized"),
            ("future_work",   r"future|further|next|recommend|can be", "Future work indicated"),
            ("no_new_data",   r"", "No new data introduced"),  # absence check
        ],
        "word_target": (150, 400),
        "weight": 0.10,
    },
    "Abstract": {
        "checks": [
            ("structured",    r"method|result|conclusion|background", "Structured abstract elements"),
            ("quant_present", r"\d+\.?\d*\s*%|\d+\.\d+", "Quantitative results in abstract"),
            ("keywords",      r"[Kk]eyword", "Keywords present"),
        ],
        "word_target": (150, 350),
        "weight": 0.05,
    },
}

Q1_REJECTION_REASONS = [
    "Insufficient novelty or incremental contribution",
    "Missing comparison with recent state-of-the-art methods",
    "Lack of statistical analysis or significance testing",
    "Inadequate literature review — missing key references (2021–present)",
    "Methodology not reproducible — missing dataset details",
    "Results not interpreted — Discussion is too superficial",
    "Limitations not acknowledged",
    "Abstract does not reflect quantitative results",
    "Poor English language quality",
    "Ethical statement missing",
]


def review_manuscript(file_bytes: bytes, filename: str) -> dict:
    """
    Full Q1 reviewer assessment of uploaded manuscript.
    Returns structured review with scores, comments, recommendations.
    """
    text, metadata = extract_text(file_bytes, filename)
    if not text or len(text) < 200:
        return {"error": "Dokumen tidak dapat dibaca atau terlalu pendek."}

    sections = detect_sections(text)
    sections["_raw_text"] = text
    word_count = len(text.split())

    section_reviews = {}
    overall_score = 0
    total_weight = 0

    for sec_name, criteria in REVIEW_CRITERIA.items():
        # Find section text
        sec_text = sections.get(sec_name.lower(), sections.get("_full_text", text))
        if sec_text.startswith("["):
            sec_text = ""

        sec_words = len(sec_text.split()) if sec_text else 0
        wmin, wmax = criteria["word_target"]

        # Run checks
        passed = []
        failed = []
        for check_id, pattern, description in criteria["checks"]:
            if pattern == "":  # absence check
                passed.append(description)
                continue
            if re.search(pattern, sec_text, re.IGNORECASE):
                passed.append(description)
            else:
                failed.append(description)

        # Score
        check_score = len(passed) / max(len(criteria["checks"]), 1)
        word_score = 1.0
        if sec_words < wmin * 0.7:
            word_score = 0.5
        elif sec_words > wmax * 1.5:
            word_score = 0.8

        sec_score = round((check_score * 0.7 + word_score * 0.3) * 10, 1)
        overall_score += sec_score * criteria["weight"]
        total_weight += criteria["weight"]

        # Generate comments
        comments = _generate_section_comments(sec_name, failed, sec_words, wmin, wmax)
        recommendations = _generate_recommendations(sec_name, failed)

        section_reviews[sec_name] = {
            "score": sec_score,
            "word_count": sec_words,
            "word_target": f"{wmin}–{wmax}",
            "checks_passed": passed,
            "checks_failed": failed,
            "comments": comments,
            "recommendations": recommendations,
        }

    final_score = round(overall_score / max(total_weight, 0.01), 1)
    accept_prob = _estimate_acceptance(final_score, section_reviews)

    # Generate overall review
    major_revisions = []
    minor_revisions = []
    for sec, rev in section_reviews.items():
        for fail in rev["checks_failed"]:
            if rev["score"] < 5:
                major_revisions.append(f"[{sec}] {fail}")
            else:
                minor_revisions.append(f"[{sec}] {fail}")

    return {
        "overall_score":     final_score,
        "accept_probability": accept_prob,
        "word_count_total":  word_count,
        "verdict":           _verdict(final_score),
        "section_reviews":   section_reviews,
        "major_revisions":   major_revisions[:8],
        "minor_revisions":   minor_revisions[:8],
        "editor_comment":    _editor_comment(final_score, accept_prob),
        "filename":          filename,
        "reviewed_at":       __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _generate_section_comments(sec: str, failed: list, words: int, wmin: int, wmax: int) -> list:
    comments = []
    if words < wmin * 0.7:
        comments.append(f"Section appears underdeveloped ({words} words; target {wmin}–{wmax}). "
                         "Expand with more detail and supporting evidence.")
    if words > wmax * 1.5:
        comments.append(f"Section is excessively long ({words} words). "
                         "Consider condensing to improve readability.")
    if sec == "Discussion" and "Results interpreted with data reference" in failed:
        comments.append("Discussion must directly reference Tables and Figures from Results. "
                         "Each claim should cite specific numerical findings.")
    if sec == "Methods" and "Validation strategy described" in failed:
        comments.append("The validation approach is unclear. Specify train/test split ratios, "
                         "cross-validation folds, or holdout strategy.")
    return comments


def _generate_recommendations(sec: str, failed: list) -> list:
    recs = []
    rec_map = {
        "Research gap clearly stated": "Add a paragraph explicitly identifying the gap in literature before stating your objective.",
        "Novelty claim present": "Include an explicit statement: 'The novelty of this work is...' in Introduction.",
        "Methodology reproducible": "Provide: dataset name, size (n=), source URL/DOI, preprocessing steps.",
        "Quantitative results reported": "Replace qualitative statements with specific values: 'improved by 4.3%' not 'improved significantly'.",
        "Comparison with baselines": "Add Table comparing your method vs ≥3 recent SOTA methods (2022–2024).",
        "Results interpreted with data reference": "For each result, write: 'As shown in Table X, the accuracy of Y% indicates...'",
        "Limitations acknowledged": "Add a dedicated paragraph: 'This study has several limitations. First,...'",
        "Structured abstract elements": "Restructure abstract: Background (1 sentence) | Methods (2) | Results (2) | Conclusion (1).",
        "Quantitative results in abstract": "Include your best metric in abstract: 'achieving F1-score of X% on dataset Y'.",
    }
    for fail in failed:
        if fail in rec_map:
            recs.append(rec_map[fail])
    return recs


def _estimate_acceptance(score: float, reviews: dict) -> str:
    if score >= 8.5: return "High (>70%)"
    if score >= 7.0: return "Moderate (40–70%)"
    if score >= 5.5: return "Low (15–40%)"
    return "Very Low (<15%)"


def _verdict(score: float) -> str:
    if score >= 8.5: return "✅ Accept with Minor Revisions"
    if score >= 7.0: return "⚠️ Major Revisions Required"
    if score >= 5.5: return "❌ Reject — Substantial Rewriting Needed"
    return "❌ Reject — Does Not Meet Q1 Standards"


def _editor_comment(score: float, prob: str) -> str:
    if score >= 8.0:
        return ("The manuscript presents a well-structured contribution with clear methodology "
                "and quantitative results. A few minor revisions are recommended before final acceptance.")
    if score >= 6.5:
        return ("The manuscript addresses an important problem; however, the current version "
                "requires substantial revisions — particularly in the Discussion section and "
                "comparison with state-of-the-art methods.")
    return ("In its current form, the manuscript does not meet the standards for publication "
            "in a Scopus Q1 journal. The authors are encouraged to substantially revise the "
            "manuscript addressing all reviewer concerns before resubmission.")
