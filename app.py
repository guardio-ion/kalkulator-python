import re
from flask import Flask, request, render_template
import sympy as sp

app = Flask(__name__)

def preprocess_input(expr: str) -> str:
    """Tambahkan * otomatis pada ekspresi seperti 2x, ab, 3(x+1)"""
    expr = expr.replace("^", "**")  # ubah pangkat
    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)  # 2x -> 2*x, 3(x+1) -> 3*(x+1)
    expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)  # ab -> a*b
    expr = re.sub(r'([a-zA-Z)])(\d)', r'\1*\2', expr)  # x2 -> x*2 (kalau maksudnya x*2)
    return expr

def clean_latex(expr):
    latex_str = sp.latex(expr)
    latex_str = latex_str.replace(" ", "")
    latex_str = latex_str.replace("+-", "-")
    return latex_str

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            poly1_expr = request.form.get("poly1_expr", "").strip()
            poly2_expr = request.form.get("poly2_expr", "").strip()
            subs_values = request.form.get("subs_values", "").strip()

            if not poly1_expr:
                raise ValueError("Poly1 harus diisi!")

            # preprocess biar aman
            poly1_expr = preprocess_input(poly1_expr)
            poly2_expr = preprocess_input(poly2_expr) if poly2_expr else ""

            p1 = sp.sympify(poly1_expr)
            p2 = sp.sympify(poly2_expr) if poly2_expr else None

            operation = request.form.get("operation")

            if operation == "add":
                result = f"\\[{clean_latex(sp.expand(p1 + p2))}\\]"

            elif operation == "sub":
                result = f"\\[{clean_latex(sp.expand(p1 - p2))}\\]"

            elif operation == "mul":
                result = f"\\[{clean_latex(sp.expand(p1 * p2))}\\]"

            elif operation == "div":
                q, r = sp.div(p1, p2)
                result = f"\\[\\text{{Hasil bagi: }} {clean_latex(q)}, \\quad \\text{{Sisa: }} {clean_latex(r)}\\]"

            elif operation == "remainder":
                result = f"\\[{clean_latex(sp.rem(p1, p2))}\\]"

            elif operation == "factor":
                result = f"\\[{clean_latex(sp.factor(p1))}\\]"

            elif operation == "diff":
                result = f"\\[{clean_latex(sp.diff(p1))}\\]"

            elif operation == "integral":
                result = f"\\[{clean_latex(sp.integrate(p1))}\\]"

            elif operation == "eval":
                subs_dict = {}
                if subs_values:
                    for item in subs_values.split(","):
                        if "=" in item:
                            var, val = item.split("=")
                            subs_dict[sp.symbols(var.strip())] = float(val.strip())
                val = p1.subs(subs_dict) if subs_dict else p1
                result = f"\\[{clean_latex(p1)} = {clean_latex(val)}\\]"

            elif operation == "roots":
                roots = sp.solve(sp.Eq(p1, 0))
                if not roots:
                    result = "Tidak ada akar real yang ditemukan."
                else:
                    latex_roots = ", ".join([clean_latex(r) for r in roots])
                    result = f"\\[ \\text{{Akar-akar: }} {latex_roots} \\]"

            else:
                result = "Operasi tidak dikenali."

        except Exception as e:
            result = f"Error: {e}"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
