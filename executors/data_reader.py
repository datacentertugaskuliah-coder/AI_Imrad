"""
executors/data_reader.py — M25 Data File Reader v13
Baca file data IN-MEMORY (no disk write, no download)
Support: CSV, Excel, TXT, PDF
Extract quantitative data → auto-fill quant field
"""
import re
from io import BytesIO
from datetime import datetime


def read_datafile_inplace(file_bytes: bytes, filename: str) -> dict:
    """
    Read any data file into memory without writing to disk.
    Returns structured dict with raw_text, dataframe_summary, quant_extracted.
    """
    name_lower = filename.lower()
    result = {
        "filename": filename,
        "format": "unknown",
        "raw_text": "",
        "columns": [],
        "rows": 0,
        "quant_extracted": "",
        "stats_summary": {},
        "error": "",
    }

    try:
        if name_lower.endswith(".csv"):
            return _read_csv(file_bytes, result)
        elif name_lower.endswith((".xlsx", ".xls")):
            return _read_excel(file_bytes, result)
        elif name_lower.endswith(".txt"):
            return _read_txt(file_bytes, result)
        elif name_lower.endswith(".pdf"):
            return _read_pdf(file_bytes, result)
        else:
            result["error"] = f"Format tidak didukung: {filename}"
            return result
    except Exception as e:
        result["error"] = str(e)[:200]
        return result


def _read_csv(file_bytes: bytes, result: dict) -> dict:
    try:
        import pandas as pd
        df = pd.read_csv(BytesIO(file_bytes), on_bad_lines='skip')
        result["format"] = "csv"
        result["rows"] = len(df)
        result["columns"] = list(df.columns)
        result["raw_text"] = df.to_string(index=False, max_rows=20)
        result["stats_summary"] = _extract_stats(df)
        result["quant_extracted"] = _format_quant(result["stats_summary"], df)
    except ImportError:
        result["error"] = "pandas tidak terinstall"
    return result


def _read_excel(file_bytes: bytes, result: dict) -> dict:
    try:
        import pandas as pd
        df = pd.read_excel(BytesIO(file_bytes), sheet_name=0)
        result["format"] = "excel"
        result["rows"] = len(df)
        result["columns"] = list(df.columns)
        result["raw_text"] = df.to_string(index=False, max_rows=20)
        result["stats_summary"] = _extract_stats(df)
        result["quant_extracted"] = _format_quant(result["stats_summary"], df)
    except ImportError:
        result["error"] = "pandas/openpyxl tidak terinstall"
    return result


def _read_txt(file_bytes: bytes, result: dict) -> dict:
    text = file_bytes.decode("utf-8", errors="ignore")
    result["format"] = "txt"
    result["raw_text"] = text[:3000]
    # Extract numbers from text
    numbers = re.findall(r'\b\d+\.?\d*\s*(?:%|percent|accuracy|precision|recall|f1|auc)?\b', text, re.IGNORECASE)
    if numbers:
        result["quant_extracted"] = "Angka ditemukan: " + ", ".join(numbers[:20])
    return result


def _read_pdf(file_bytes: bytes, result: dict) -> dict:
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages[:10]:
            try: text += page.extract_text() or ""
            except: pass
        result["format"] = "pdf"
        result["raw_text"] = text[:3000]
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\s*(?:%|percent)?\b', text)
        numbers = [n for n in numbers if len(n.strip()) > 1]
        if numbers:
            result["quant_extracted"] = "Angka: " + ", ".join(numbers[:20])
    except ImportError:
        result["error"] = "pypdf tidak terinstall"
    return result


def _extract_stats(df) -> dict:
    """Extract descriptive stats from DataFrame numeric columns."""
    try:
        import pandas as pd
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return {}
        stats = {}
        for col in numeric.columns[:10]:  # max 10 columns
            col_data = numeric[col].dropna()
            if len(col_data) == 0:
                continue
            stats[col] = {
                "mean":   round(col_data.mean(), 4),
                "std":    round(col_data.std(), 4),
                "min":    round(col_data.min(), 4),
                "max":    round(col_data.max(), 4),
                "median": round(col_data.median(), 4),
                "n":      len(col_data),
            }
        return stats
    except Exception:
        return {}


def _format_quant(stats: dict, df) -> str:
    """Format stats as natural language quant string."""
    if not stats:
        # Try to find metric-like column names
        try:
            metric_cols = [c for c in df.columns
                           if any(m in c.lower() for m in
                                  ["acc","f1","precision","recall","auc","score","error","loss","rate"])]
            if metric_cols:
                parts = []
                for col in metric_cols[:5]:
                    val = df[col].dropna()
                    if len(val):
                        parts.append(f"{col}={val.mean():.4f} (max={val.max():.4f})")
                return ", ".join(parts)
        except Exception:
            pass
        return ""

    parts = []
    for col, s in list(stats.items())[:8]:
        # Format nicely depending on range
        mean_v = s["mean"]
        if 0 < mean_v <= 1:
            pct = f"{mean_v*100:.2f}%"
            parts.append(f"{col}: mean={pct}, max={s['max']*100:.2f}%, std={s['std']*100:.2f}%")
        elif 0 < mean_v <= 100:
            parts.append(f"{col}: mean={mean_v:.2f}, max={s['max']:.2f}, n={s['n']}")
        else:
            parts.append(f"{col}: mean={mean_v:.4f}, std={s['std']:.4f}, n={s['n']}")
    return "; ".join(parts)


def aggregate_corpus_quant(corpus_data_list: list) -> str:
    """Aggregate quant data from multiple files."""
    all_quants = []
    for item in corpus_data_list:
        if item.get("quant_extracted"):
            all_quants.append(f"[{item['filename']}] {item['quant_extracted']}")
    return " | ".join(all_quants) if all_quants else ""
