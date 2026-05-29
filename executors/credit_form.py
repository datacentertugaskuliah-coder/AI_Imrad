"""
executors/credit_form.py — CRediT Author Statement Generator v15
Algoritma: input user → 14 CRediT roles → generate statement APA-compatible
"""
import streamlit as st


# 14 standard CRediT roles (CASRAI taxonomy)
CREDIT_ROLES = [
    "Conceptualization",
    "Data curation",
    "Formal analysis",
    "Funding acquisition",
    "Investigation",
    "Methodology",
    "Project administration",
    "Resources",
    "Software",
    "Supervision",
    "Validation",
    "Visualization",
    "Writing — original draft",
    "Writing — review & editing",
]

# Common role presets
ROLE_PRESETS = {
    "First Author":  ["Conceptualization", "Methodology", "Investigation",
                       "Formal analysis", "Writing — original draft"],
    "Co-Author":     ["Methodology", "Investigation", "Writing — review & editing"],
    "Supervisor":    ["Conceptualization", "Supervision", "Funding acquisition",
                       "Writing — review & editing"],
    "Data Analyst":  ["Data curation", "Formal analysis", "Software",
                       "Visualization"],
    "Reviewer":      ["Validation", "Writing — review & editing"],
}


def render_credit_form() -> list:
    """
    Render Streamlit form for author input.
    Returns list of author dicts.
    """
    st.markdown("**👥 CRediT Author Contribution Statement**")
    st.caption("Input jumlah penulis dan peran masing-masing. "
                "Sistem otomatis tag First Author dan Co-Author.")

    # Init storage
    if "v15_authors" not in st.session_state:
        st.session_state["v15_authors"] = []

    n_authors = st.number_input(
        "Jumlah penulis (author)", min_value=1, max_value=20,
        value=max(1, len(st.session_state["v15_authors"])),
        key="v15_n_authors",
        help="Berapa banyak penulis di manuskrip ini? Penulis pertama otomatis = First Author."
    )

    # Sync authors list length
    while len(st.session_state["v15_authors"]) < n_authors:
        st.session_state["v15_authors"].append({"name": "", "roles": [], "position": len(st.session_state["v15_authors"])})
    while len(st.session_state["v15_authors"]) > n_authors:
        st.session_state["v15_authors"].pop()

    # Render form for each author
    authors = []
    for i in range(n_authors):
        position_label = "🥇 First Author" if i == 0 else f"👤 Co-Author {i}"
        with st.expander(f"{position_label}", expanded=(i < 2)):
            c1, c2 = st.columns([1, 2])

            cur = st.session_state["v15_authors"][i] if i < len(st.session_state["v15_authors"]) else {}

            with c1:
                name = st.text_input(
                    f"Nama lengkap", value=cur.get("name", ""),
                    key=f"v15_auth_name_{i}",
                    placeholder="John A. Smith")
                affiliation = st.text_input(
                    f"Afiliasi (opsional)", value=cur.get("affiliation", ""),
                    key=f"v15_auth_aff_{i}",
                    placeholder="University Name, City, Country")
                email = st.text_input(
                    f"Email (opsional)", value=cur.get("email", ""),
                    key=f"v15_auth_email_{i}",
                    placeholder="email@university.edu")

                # Preset shortcut
                preset = st.selectbox(
                    "Preset peran (opsional)",
                    ["— Pilih preset —"] + list(ROLE_PRESETS.keys()),
                    key=f"v15_auth_preset_{i}")
                if preset != "— Pilih preset —" and st.button(f"Apply preset", key=f"v15_apply_{i}"):
                    st.session_state["v15_authors"][i]["roles"] = ROLE_PRESETS[preset]
                    st.rerun()

            with c2:
                default_roles = cur.get("roles", [])
                if i == 0 and not default_roles:
                    # First author default
                    default_roles = ROLE_PRESETS["First Author"]

                roles = st.multiselect(
                    f"Peran (CRediT) — pilih semua yang sesuai",
                    CREDIT_ROLES,
                    default=default_roles,
                    key=f"v15_auth_roles_{i}",
                    help="Pilih peran sesuai standar CRediT (Contributor Roles Taxonomy)")

                corresponding = st.checkbox(
                    "Corresponding Author",
                    value=cur.get("corresponding", i == 0),
                    key=f"v15_auth_corr_{i}")

            authors.append({
                "name": name, "affiliation": affiliation, "email": email,
                "roles": roles, "position": i,
                "corresponding": corresponding,
                "label": "First Author" if i == 0 else f"Co-Author {i}",
            })

    st.session_state["v15_authors"] = authors
    return authors


def generate_credit_statement(authors: list, journal_name: str = "") -> str:
    """
    Generate formal CRediT Author Contribution Statement.
    Format ready for journal submission.
    """
    if not authors:
        return ""

    lines = ["**CRediT Author Contribution Statement**", ""]

    # Each author with their roles
    for author in authors:
        name = author.get("name", "").strip()
        roles = author.get("roles", [])
        if not name or not roles:
            continue

        role_str = "; ".join(roles)
        lines.append(f"**{name}**: {role_str}.")
        lines.append("")  # spacing

    # Author affiliations block
    lines.append("---")
    lines.append("")
    lines.append("**Author Information:**")
    lines.append("")

    for author in authors:
        name = author.get("name", "").strip()
        if not name:
            continue

        marker = " *" if author.get("corresponding") else ""
        line = f"- **{name}**{marker}"
        if author.get("affiliation"):
            line += f", {author['affiliation']}"
        if author.get("email"):
            line += f" ({author['email']})"
        lines.append(line)

    if any(a.get("corresponding") for a in authors):
        lines.append("")
        lines.append("*Corresponding Author")

    if journal_name:
        lines.append("")
        lines.append(f"*Prepared for submission to: {journal_name}*")

    return "\n".join(lines)


def validate_credit(authors: list) -> tuple[bool, list]:
    """Validate CRediT contributions. Returns (is_valid, warnings)."""
    warnings = []
    if not authors:
        return False, ["No authors specified"]

    # Check first author has roles
    if authors[0].get("roles") == []:
        warnings.append("First author has no roles assigned")

    # Check all roles covered across all authors
    all_roles = set()
    for a in authors:
        all_roles.update(a.get("roles", []))

    essential = {"Conceptualization", "Methodology", "Writing — original draft"}
    missing = essential - all_roles
    if missing:
        warnings.append(f"Missing essential roles: {', '.join(missing)}")

    # Check corresponding author exists
    if not any(a.get("corresponding") for a in authors):
        warnings.append("No Corresponding Author marked")

    return len(warnings) == 0, warnings
