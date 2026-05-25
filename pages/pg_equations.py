"""NEW v7: Equation Builder page (M12)"""
import streamlit as st
from core.data import EQUATION_TEMPLATES, FIELDS, get_equation_templates

def render():
    st.title("📐 Equation Builder · M12 Core Intelligence v7")
    st.caption("LaTeX equations · Word-compatible · Copy-paste ready · Per bidang ilmu")

    st.info(
        "**M12 NEW v7:** Rumus matematika dalam LaTeX yang kompatibel dengan "
        "Word Equation Editor (Insert > Equation). Pilih bidang ilmu untuk "
        "melihat template yang relevan, atau buat custom equation di bawah.",
        icon="📐"
    )

    field = st.selectbox("Bidang ilmu", FIELDS, key="eq_field")
    eqs = get_equation_templates(field)

    st.subheader(f"Template rumus untuk {field} ({len(eqs)} equation)")

    for i, eq in enumerate(eqs, 1):
        with st.expander(f"{i}. {eq['name']}", expanded=(i==1)):
            ec1, ec2 = st.columns([1,1])
            with ec1:
                st.markdown(f"**Deskripsi:**")
                st.write(eq['desc'])
                st.markdown(f"**Rendered LaTeX:**")
                st.latex(eq['latex'])
            with ec2:
                st.markdown(f"**LaTeX source** (copy ke Word):")
                st.code(eq['latex'], language="latex")
                st.markdown("**Cara copy ke Word:**")
                st.markdown(
                    "1. Klik tombol copy di kanan atas kode LaTeX\n"
                    "2. Di Word: Insert > Equation > Insert New Equation\n"
                    "3. Pastikan mode 'LaTeX' aktif di Equation Tools\n"
                    "4. Paste LaTeX → Word otomatis render persamaan"
                )

    st.divider()

    st.subheader("✏️ Custom equation builder")
    custom_name = st.text_input("Nama persamaan",
        placeholder="Contoh: Custom Loss Function")
    custom_latex = st.text_area("LaTeX code",
        placeholder=r"L = -\sum_{i=1}^{N} y_i \log(\hat{y}_i)",
        height=100)
    custom_desc = st.text_area("Deskripsi & variabel",
        placeholder="L = loss, N = sample size, y_i = true label, ŷ_i = predicted",
        height=80)

    if custom_latex:
        st.markdown(f"### Preview: {custom_name or 'Untitled'}")
        try:
            st.latex(custom_latex)
            st.success("✅ LaTeX valid")
            if custom_desc:
                st.caption(custom_desc)
            st.code(custom_latex, language="latex")
            st.download_button(
                "⬇ Unduh sebagai .tex",
                data=f"% {custom_name}\n% {custom_desc}\n${custom_latex}$",
                file_name=f"equation_{custom_name.replace(' ','_').lower() or 'custom'}.tex",
                mime="text/plain")
        except Exception as e:
            st.error(f"LaTeX error: {e}")

    st.divider()

    st.subheader("📚 LaTeX cheat sheet")
    cheat = {
        "Greek letters": r"\alpha, \beta, \gamma, \delta, \epsilon, \theta, \mu, \sigma, \omega",
        "Subscript/Superscript": r"x_i, x^2, x_{i,j}, x^{n+1}",
        "Fractions": r"\frac{a}{b}, \frac{\partial f}{\partial x}",
        "Square root": r"\sqrt{x}, \sqrt[n]{x}",
        "Summation": r"\sum_{i=1}^{N} x_i, \int_0^1 f(x)\,dx",
        "Greek bold/script": r"\mathbf{x}, \mathcal{L}, \mathbb{R}",
        "Equality variants": r"\leq, \geq, \neq, \approx, \equiv",
        "Limits": r"\lim_{x \to \infty} f(x)",
        "Matrix": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
    }
    for name, latex in cheat.items():
        cc1, cc2 = st.columns([1,2])
        cc1.markdown(f"**{name}**")
        cc2.code(latex, language="latex")
