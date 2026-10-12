"""
Matematika boti funksiyalari va yechimlarining to'liq avtomatlashtirilgan testi.
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from services.math_engine import (
    solve_general_math,
    solve_quadratic_equation,
    solve_linear_equation,
    solve_system_equations,
    solve_fraction_expression,
    solve_derivative,
    solve_integral,
    calculate_geometry
)

def run_all_tests():
    print("==================================================")
    print("📐 MATEMATIKA BOTI TESTLARI")
    print("==================================================")

    # 1. Kvadrat tenglama
    res1 = solve_quadratic_equation("x^2 - 5x + 6 = 0")
    assert res1 and "x₁ = 2" in res1 and "x₂ = 3" in res1 and "Diskriminant" in res1
    print("✅ 1. Kvadrat tenglama (Diskriminant & Viet): OK")

    # 2. Chiziqli tenglama
    res2 = solve_linear_equation("2x + 8 = 20")
    assert res2 and "x = 6" in res2
    print("✅ 2. Chiziqli tenglama (2x + 8 = 20 -> x = 6): OK")

    # 3. Kasrlar
    res3 = solve_fraction_expression("3/4 + 5/6 - 1/3")
    assert res3 and "5/4" in res3
    print("✅ 3. Kasrlar bilan amallar (3/4 + 5/6 - 1/3 = 5/4): OK")

    # 4. Tenglamalar sistemasi
    res4 = solve_system_equations("2x + y = 10, x - y = 2")
    assert res4 and "x = 4" in res4 and "y = 2" in res4
    print("✅ 4. Tenglamalar sistemasi: OK")

    # 5. Hosila
    res5 = solve_derivative("3x^3 - 4x^2 + 5x - 7")
    assert res5 and "9*x**2 - 8*x + 5" in res5
    print("✅ 5. Hosila hisoblash (f'(x)): OK")

    # 6. Integral
    res6 = solve_integral("3x^2 + 4x")
    assert res6 and "x**3 + 2*x**2" in res6
    print("✅ 6. Integral hisoblash: OK")

    # 7. Qavslarni ochish va umumiy arifmetika
    res7 = solve_general_math("(x + 5)^2")
    assert res7 and "x**2 + 10*x + 25" in res7
    print("✅ 7. Qavslarni ochish: OK")

    # 8. Geometriya
    res8 = calculate_geometry("uchburchak", {"a": 3, "b": 4, "c": 5})
    assert res8 and "6.00" in res8
    print("✅ 8. Geometriya hisoblash: OK")

    print("\n🎉 BARCHA 8 TA TEST MUVAFFAQIYATLI O'TDI! QOTISHLAR YO'Q, 100% ANIQ!")

if __name__ == "__main__":
    run_all_tests()
