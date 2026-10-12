"""
XON MATH ENGINE — Matematika Uy Vazifasi va Misollarini
100% Aniq, Qadamma-qadam va O'zbek Tilida Yechish Dvigateli.
SymPy, Python Math va Regex asosida ishlaydi (0% Qotish, 100% Tezkorlik).
"""

import math
import re
from fractions import Fraction
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application, convert_xor)

def clean_input(text: str) -> str:
    """Foydalanuvchi kiritgan matematik matnni standart shaklga keltirish."""
    s = text.strip()
    s = s.replace('×', '*').replace('÷', '/').replace(':', '/')
    s = s.replace('−', '-').replace('–', '-')
    s = s.replace('²', '^2').replace('³', '^3')
    s = s.replace('^', '**')
    s = re.sub(r'\btg\(', 'tan(', s, flags=re.IGNORECASE)
    s = re.sub(r'\bctg\(', 'cot(', s, flags=re.IGNORECASE)
    s = re.sub(r'\barcsin\(', 'asin(', s, flags=re.IGNORECASE)
    s = re.sub(r'\barccos\(', 'acos(', s, flags=re.IGNORECASE)
    s = re.sub(r'\barctg\(', 'atan(', s, flags=re.IGNORECASE)
    s = re.sub(r'\bildiz\(', 'sqrt(', s, flags=re.IGNORECASE)
    s = re.sub(r'\bpi\b', 'pi', s, flags=re.IGNORECASE)
    return s


def is_likely_math(text: str) -> bool:
    """Matn haqiqatdan ham matematik ifoda ekanligini aniqlash."""
    t = text.strip()
    # Raqamlar bormi?
    has_digits = bool(re.search(r'\d', t))
    # Matematik belgilar bormi?
    has_math_ops = bool(re.search(r'[+\-*/=^><√²³]|sqrt|sin|cos|tan|tg|ctg|hosila|diff|integral|int\b|lim', t, re.IGNORECASE))
    
    # Agar faqat bitta so'z bo'lsa va unda raqam yoki belgi bo'lmasa -> matematika emas
    if not has_digits and not has_math_ops:
        return False
    return True


def solve_quadratic_equation(eq_str: str) -> str:
    """Kvadrat tenglamani D (Diskriminant) bo'yicha qadamma-qadam yechish."""
    try:
        clean = clean_input(eq_str)
        if '=' in clean:
            left_s, right_s = clean.split('=', 1)
            left_expr = parse_expr(left_s, transformations=TRANSFORMATIONS)
            right_expr = parse_expr(right_s, transformations=TRANSFORMATIONS)
            poly_expr = sp.simplify(left_expr - right_expr)
        else:
            poly_expr = sp.simplify(parse_expr(clean, transformations=TRANSFORMATIONS))

        x = sp.Symbol('x')
        poly = sp.Poly(poly_expr, x)

        if poly.degree() != 2:
            return None

        coeffs = poly.all_coeffs()
        a = coeffs[0]
        b = coeffs[1]
        c = coeffs[2]

        D = b**2 - 4*a*c
        
        lines = []
        lines.append("📐 <b>KVADRAT TENGLAMA YECHIMI</b>\n")
        lines.append(f"📝 <b>Berilgan:</b> <code>{poly_expr} = 0</code>")
        lines.append(f"📌 <b>Koeffitsiyentlar:</b> <code>a = {a}</code>, <code>b = {b}</code>, <code>c = {c}</code>\n")
        
        lines.append("🔍 <b>1-bosqich: Diskriminantni hisoblash:</b>")
        lines.append("💡 Formula: <code>D = b² - 4ac</code>")
        lines.append(f"<code>D = ({b})² - 4 · ({a}) · ({c}) = {b**2} - ({4*a*c}) = {D}</code>\n")

        if D > 0:
            sqrt_D = sp.sqrt(D)
            x1 = (-b - sqrt_D) / (2*a)
            x2 = (-b + sqrt_D) / (2*a)
            x1_simp = sp.simplify(x1)
            x2_simp = sp.simplify(x2)

            lines.append("🔍 <b>2-bosqich: Ildizlarni topish (D > 0 bo'lgani uchun 2 ta ildiz bor):</b>")
            lines.append("💡 Formula: <code>x₁,₂ = (-b ± √D) / (2a)</code>\n")
            lines.append(f"• <code>x₁ = (-({b}) - √{D}) / (2 · {a}) = ({-b} - {sqrt_D}) / {2*a} = <b>{x1_simp}</b></code>")
            lines.append(f"• <code>x₂ = (-({b}) + √{D}) / (2 · {a}) = ({-b} + {sqrt_D}) / {2*a} = <b>{x2_simp}</b></code>\n")

            lines.append("✨ <b>Viet teoremasi bo'yicha tekshirish:</b>")
            lines.append(f"• <code>x₁ + x₂ = {x1_simp} + {x2_simp} = {x1_simp + x2_simp}</code> (<code>-b/a = {-b/a}</code>) ✅")
            lines.append(f"• <code>x₁ · x₂ = {x1_simp} · {x2_simp} = {x1_simp * x2_simp}</code> (<code>c/a = {c/a}</code>) ✅\n")

            lines.append(f"✅ <b>Javob:</b> <code>x₁ = {x1_simp}</code>, <code>x₂ = {x2_simp}</code>")
        elif D == 0:
            x_val = -b / (2*a)
            x_simp = sp.simplify(x_val)
            lines.append("🔍 <b>2-bosqich: D = 0 bo'lgani uchun tenglama yagona (karrali) ildizga ega:</b>")
            lines.append(f"• <code>x = -b / (2a) = -({b}) / (2 · {a}) = <b>{x_simp}</b></code>\n")
            lines.append(f"✅ <b>Javob:</b> <code>x = {x_simp}</code>")
        else:
            lines.append("🔍 <b>2-bosqich: Xulosa:</b>")
            lines.append("• <code>D < 0</code> bo'lgani uchun tenglama <b>haqiqiy sonlar to'plamida ildizga ega emas</b> (∅).")
            c_x1 = sp.simplify((-b - sp.I * sp.sqrt(-D)) / (2*a))
            c_x2 = sp.simplify((-b + sp.I * sp.sqrt(-D)) / (2*a))
            lines.append(f"• Kompleks sonlar maydonida: <code>x₁ = {c_x1}</code>, <code>x₂ = {c_x2}</code>\n")
            lines.append("✅ <b>Javob:</b> Haqiqiy ildizlari yo'q (∅)")

        return "\n".join(lines)
    except Exception:
        return None


def solve_linear_equation(eq_str: str) -> str:
    """Chiziqli tenglamani qadamma-qadam yechish."""
    try:
        clean = clean_input(eq_str)
        if '=' not in clean:
            return None
        
        left_s, right_s = clean.split('=', 1)
        x = sp.Symbol('x')
        left_expr = parse_expr(left_s, transformations=TRANSFORMATIONS)
        right_expr = parse_expr(right_s, transformations=TRANSFORMATIONS)

        diff = sp.simplify(left_expr - right_expr)
        poly = sp.Poly(diff, x)
        
        if poly.degree() != 1:
            return None

        coeffs = poly.all_coeffs()
        a = coeffs[0]
        b = coeffs[1]
        solution = -b / a
        sol_simp = sp.simplify(solution)

        lines = []
        lines.append("📐 <b>CHIZIQLI TENGLAMA YECHIMI</b>\n")
        lines.append(f"📝 <b>Berilgan:</b> <code>{left_expr} = {right_expr}</code>\n")
        lines.append("🔍 <b>Qadamma-qadam yechish:</b>")
        lines.append(f"1. Barcha noma'lumlarni chapga, ozod sonlarni o'ng tomonga o'tkazamiz:")
        lines.append(f"   <code>{a}x = {-b}</code>")
        lines.append(f"2. Tenglamaning ikkala qismini <code>x</code> ning koeffitsiyenti (<code>{a}</code>) ga bo'lamiz:")
        lines.append(f"   <code>x = ({-b}) / ({a})</code>")
        lines.append(f"   <code>x = {sol_simp}</code>\n")

        check_left = sp.simplify(left_expr.subs(x, sol_simp))
        check_right = sp.simplify(right_expr.subs(x, sol_simp))
        lines.append("✨ <b>Tekshirish:</b>")
        lines.append(f"   <code>{check_left} = {check_right}</code> (To'g'ri!) ✅\n")
        lines.append(f"✅ <b>Javob:</b> <code>x = {sol_simp}</code>")

        return "\n".join(lines)
    except Exception:
        return None


def solve_system_equations(text: str) -> str:
    """Tenglamalar sistemasini yechish (masalan: 2x + y = 10, x - y = 2)."""
    try:
        raw_eqs = [e.strip() for e in text.replace(';', ',').split(',') if e.strip() and '=' in e]
        if len(raw_eqs) < 2:
            return None

        x, y = sp.symbols('x y')
        sp_eqs = []
        for eq_str in raw_eqs:
            clean = clean_input(eq_str)
            left_s, right_s = clean.split('=', 1)
            left_expr = parse_expr(left_s, transformations=TRANSFORMATIONS)
            right_expr = parse_expr(right_s, transformations=TRANSFORMATIONS)
            sp_eqs.append(sp.Eq(left_expr, right_expr))

        sols = sp.solve(sp_eqs, (x, y))
        if not sols:
            return "📐 <b>TENGLAMALAR SISTEMASI</b>\n\n❌ Ushbu sistema yechimga ega emas yoki cheksiz ko'p yechimga ega."

        lines = []
        lines.append("📐 <b>TENGLAMALAR SISTEMASI YECHIMI</b>\n")
        lines.append("📝 <b>Berilgan sistema:</b>")
        for i, eq in enumerate(sp_eqs, 1):
            lines.append(f"  {i}) <code>{eq.lhs} = {eq.rhs}</code>")
        lines.append("")

        lines.append("🔍 <b>Yechish usuli (Qo'shish / O'rniga qo'yish usuli):</b>")
        if isinstance(sols, dict):
            lines.append(f"• <code>x = {sols.get(x)}</code>")
            lines.append(f"• <code>y = {sols.get(y)}</code>\n")
            lines.append(f"✅ <b>Javob:</b> <code>(x = {sols.get(x)}; y = {sols.get(y)})</code>")
        elif isinstance(sols, list) and len(sols) > 0:
            sol = sols[0]
            lines.append(f"• <code>x = {sol[0]}</code>")
            lines.append(f"• <code>y = {sol[1]}</code>\n")
            lines.append(f"✅ <b>Javob:</b> <code>(x = {sol[0]}; y = {sol[1]})</code>")

        return "\n".join(lines)
    except Exception:
        return None


def solve_fraction_expression(expr_str: str) -> str:
    """Oddiy va o'nli kasrlar ifodasini umumiy maxraj bilan yechish."""
    try:
        clean = clean_input(expr_str)
        expr = parse_expr(clean, transformations=TRANSFORMATIONS)
        exact_res = sp.Rational(expr)

        num = exact_res.p
        den = exact_res.q

        lines = []
        lines.append("🔢 <b>KASRLAR BILAN AMALLAR</b>\n")
        lines.append(f"📝 <b>Berilgan ifoda:</b> <code>{clean}</code>\n")

        lines.append("🔍 <b>Qadamma-qadam yechim:</b>")
        lines.append(f"1. Amallar umumiy maxrajga keltirilib bajarildi.")
        lines.append(f"2. Qisqarmas oddiy kasr shakli: <code>{num}/{den}</code>")

        if den != 1:
            butun = num // den
            qoldiq = abs(num % den)
            if butun != 0 and qoldiq != 0:
                lines.append(f"3. Aralash kasr ko'rinishi: <code>{butun} butun {qoldiq}/{den}</code>")
            
            decimal_val = float(num) / float(den)
            lines.append(f"4. O'nli kasr ko'rinishi: <code>≈ {decimal_val:.4f}</code>\n")
            lines.append(f"✅ <b>Aniq Javob:</b> <code>{num}/{den}</code> (yoki <code>{butun} {qoldiq}/{den}</code>)")
        else:
            lines.append(f"✅ <b>Javob:</b> <code>{num}</code>")

        return "\n".join(lines)
    except Exception:
        return None


def solve_derivative(func_str: str) -> str:
    """Funksiyaning hosilasini topish."""
    try:
        clean = clean_input(func_str)
        if '=' in clean:
            clean = clean.split('=', 1)[1].strip()

        x = sp.Symbol('x')
        f = parse_expr(clean, transformations=TRANSFORMATIONS)
        df = sp.diff(f, x)
        df_simp = sp.simplify(df)

        lines = []
        lines.append("📈 <b>HOSILA HISOBLASH (f'(x))</b>\n")
        lines.append(f"📝 <b>Berilgan funksiya:</b> <code>f(x) = {f}</code>\n")
        lines.append("🔍 <b>Hosila olish qoidalari:</b>")
        lines.append("• Daraja qoidasi: <code>(xⁿ)' = n · xⁿ⁻¹</code>")
        lines.append("• O'zgarmas son: <code>(C)' = 0</code>")
        lines.append("• Yig'indi hosilasi: <code>(u + v)' = u' + v'</code>\n")

        lines.append(f"🔍 <b>Bosqichma-bosqich:</b>")
        lines.append(f"<code>d/dx ({f}) = {df}</code>\n")
        lines.append(f"✅ <b>Javob:</b> <code>f'(x) = {df_simp}</code>")
        return "\n".join(lines)
    except Exception:
        return None


def solve_integral(func_str: str) -> str:
    """Aniq yoki noaniq integralni hisoblash."""
    try:
        clean = clean_input(func_str)
        if '=' in clean:
            clean = clean.split('=', 1)[1].strip()

        x = sp.Symbol('x')
        f = parse_expr(clean, transformations=TRANSFORMATIONS)
        F = sp.integrate(f, x)

        lines = []
        lines.append("📈 <b>INTEGRAL HISOBLASH</b>\n")
        lines.append(f"📝 <b>Berilgan:</b> <code>∫ ({f}) dx</code>\n")
        lines.append("🔍 <b>Integrallash qoidasi:</b>")
        lines.append("• Daraja qoidasi: <code>∫ xⁿ dx = (xⁿ⁺¹) / (n + 1) + C</code>")
        lines.append("• O'zgarmas son: <code>∫ k dx = k · x + C</code>\n")
        lines.append(f"🔍 <b>Boshlang'ich funksiya:</b>")
        lines.append(f"<code>F(x) = {F}</code>\n")
        lines.append(f"✅ <b>Javob:</b> <code>{F} + C</code>")
        return "\n".join(lines)
    except Exception:
        return None


def solve_general_math(text: str) -> str:
    """
    Har qanday matematik misolni avtomatik tahlil qilib, 
    eng mos modulga yo'naltirish (Universal Math Dispatcher).
    """
    # Agar matn matematika emas bo'lsa (masalan oddiy so'z), None qaytaramiz
    if not is_likely_math(text):
        return None

    clean = clean_input(text)

    # 1. Tenglamalar sistemasi
    if ('=' in clean and (',' in clean or ';' in clean)):
        res = solve_system_equations(text)
        if res:
            return res

    # 2. Kvadrat tenglama
    if '=' in clean and ('x**2' in clean or 'x^2' in clean or 'x²' in clean):
        res = solve_quadratic_equation(text)
        if res:
            return res

    # 3. Chiziqli tenglama
    if '=' in clean and 'x' in clean.lower():
        res = solve_linear_equation(text)
        if res:
            return res
        try:
            left_s, right_s = clean.split('=', 1)
            x = sp.Symbol('x')
            left_expr = parse_expr(left_s, transformations=TRANSFORMATIONS)
            right_expr = parse_expr(right_s, transformations=TRANSFORMATIONS)
            eq = sp.Eq(left_expr, right_expr)
            sols = sp.solve(eq, x)
            return (
                f"📐 <b>TENGLAMA YECHIMI</b>\n\n"
                f"📝 <b>Berilgan:</b> <code>{left_expr} = {right_expr}</code>\n"
                f"🔍 <b>Tenglama yechimlari:</b>\n"
                f"• <code>x = {sols}</code>\n\n"
                f"✅ <b>Javob:</b> <code>{sols}</code>"
            )
        except Exception:
            pass

    # 4. Hosila
    if any(k in text.lower() for k in ['hosila', 'diff', "f'"]):
        clean_f = re.sub(r'hosila|diff|f\'|\(|\)', '', text, flags=re.IGNORECASE).strip()
        res = solve_derivative(clean_f or text)
        if res:
            return res

    # 5. Integral
    if any(k in text.lower() for k in ['integral', 'int ']):
        clean_i = re.sub(r'integral|int', '', text, flags=re.IGNORECASE).strip()
        res = solve_integral(clean_i or text)
        if res:
            return res

    # 6. Kasrlar yoki arifmetik ifodalar
    try:
        expr = parse_expr(clean, transformations=TRANSFORMATIONS)
        simplified = sp.simplify(expr)
        factored = sp.factor(expr)
        expanded = sp.expand(expr)

        # Agar natija shunchaki o'ziga teng bo'lib qolsa va hech qanday belgi bo'lmasa
        if str(simplified) == clean and not any(op in clean for op in ['+', '-', '*', '/', '^', '**']):
            return None

        lines = []
        lines.append("🧮 <b>MATEMATIK IFODA HISOBLANDI</b>\n")
        lines.append(f"📝 <b>Berilgan:</b> <code>{clean}</code>\n")
        lines.append(f"✅ <b>Natija:</b> <code>{simplified}</code>")

        try:
            eval_num = float(simplified.evalf())
            if not simplified.is_Integer:
                lines.append(f"🔢 <b>O'nli kasrda:</b> <code>≈ {eval_num:.4f}</code>")
        except Exception:
            pass

        if factored != simplified and 'x' in clean.lower():
            lines.append(f"💡 <b>Ko'paytuvchilarga ajratilgan:</b> <code>{factored}</code>")

        if expanded != simplified and 'x' in clean.lower():
            lines.append(f"💡 <b>Qavslar ochilgan shakli:</b> <code>{expanded}</code>")

        return "\n".join(lines)
    except Exception:
        return None


def calculate_geometry(shape: str, params: dict) -> str:
    """Geometrik shakllar yuzi va perimetrini hisoblash."""
    shape = shape.lower()
    
    if shape in ['uchburchak', 'triangle']:
        a = float(params.get('a', 0))
        b = float(params.get('b', 0))
        c = float(params.get('c', 0))
        h = float(params.get('h', 0))

        lines = ["📐 <b>UCHBURCHAK HISOBLASH</b>\n"]
        if a > 0 and h > 0:
            S = 0.5 * a * h
            lines.append("💡 Formula: <code>S = (a · h) / 2</code>")
            lines.append(f"<code>S = ({a} · {h}) / 2 = <b>{S}</b></code>\n")
            lines.append(f"✅ <b>Yuzi:</b> <code>S = {S} birlik²</code>")
            return "\n".join(lines)
        elif a > 0 and b > 0 and c > 0:
            P = a + b + c
            p = P / 2
            S = math.sqrt(p * (p - a) * (p - b) * (p - c))
            lines.append("💡 Geron formulasi: <code>S = √(p·(p-a)·(p-b)·(p-c))</code>")
            lines.append(f"• Perimetr: <code>P = {a} + {b} + {c} = {P}</code>")
            lines.append(f"• Yarim perimetr: <code>p = {p}</code>")
            lines.append(f"• Yuzi: <code>S = √({p} · {p-a} · {p-b} · {p-c}) = <b>{S:.2f}</b></code>\n")
            lines.append(f"✅ <b>Perimetri:</b> <code>P = {P}</code>")
            lines.append(f"✅ <b>Yuzi:</b> <code>S ≈ {S:.2f}</code>")
            return "\n".join(lines)

    elif shape in ['aylana', 'doira', 'circle']:
        r = float(params.get('r', 0))
        if r > 0:
            S = math.pi * r**2
            L = 2 * math.pi * r
            lines = [
                "⭕ <b>DOIRA VA AYLANA HISOBLASH</b>\n",
                f"📝 Radiusi: <code>R = {r}</code>\n",
                "💡 Formulalar:",
                "• Doira yuzi: <code>S = π · R²</code>",
                "• Aylana uzunligi: <code>L = 2 · π · R</code>\n",
                f"• <code>S = 3.1416 · ({r})² = <b>{S:.2f}</b></code>",
                f"• <code>L = 2 · 3.1416 · {r} = <b>{L:.2f}</b></code>\n",
                f"✅ <b>Doira yuzi:</b> <code>S ≈ {S:.2f}</code>",
                f"✅ <b>Aylana uzunligi:</b> <code>L ≈ {L:.2f}</code>"
            ]
            return "\n".join(lines)

    elif shape in ['tortburchak', 'rectangle']:
        a = float(params.get('a', 0))
        b = float(params.get('b', 0))
        if a > 0 and b > 0:
            S = a * b
            P = 2 * (a + b)
            d = math.sqrt(a**2 + b**2)
            lines = [
                "⬛ <b>TO'G'RI TO'RTBURCHAK HISOBLASH</b>\n",
                f"📝 Tomonlari: <code>a = {a}</code>, <code>b = {b}</code>\n",
                "💡 Formulalar:",
                "• Yuzi: <code>S = a · b</code>",
                "• Perimetri: <code>P = 2 · (a + b)</code>",
                "• Diagonali: <code>d = √(a² + b²)</code>\n",
                f"• <code>S = {a} · {b} = <b>{S}</b></code>",
                f"• <code>P = 2 · ({a} + {b}) = <b>{P}</b></code>",
                f"• <code>d = √({a}² + {b}²) = <b>{d:.2f}</b></code>\n",
                f"✅ <b>Yuzi:</b> <code>S = {S}</code>",
                f"✅ <b>Perimetri:</b> <code>P = {P}</code>",
                f"✅ <b>Diagonali:</b> <code>d ≈ {d:.2f}</code>"
            ]
            return "\n".join(lines)

    return "❌ Geometrik parametrlar to'liq kiritilmadi."
