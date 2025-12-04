#!/usr/bin/env python3
"""
Тест для функции расчёта местной потери устойчивости обшивки
"""

from material import Material
from stability import local_skin_buckling

def test_skin_buckling():
    """Тестирование функции расчёта критического напряжения обшивки"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МЕСТНОЙ ПОТЕРИ УСТОЙЧИВОСТИ ОБШИВКИ")
    print("=" * 60)
    
    material = Material('B95T1', 'sheet')
    
    # Типовые параметры
    skin_thickness = 0.003  # 3 мм
    stringer_spacing = 0.15  # 15 см
    
    # Тест 1: Разные граничные условия
    print("\n1. Критическое напряжение для разных граничных условий:")
    print(f"   Толщина обшивки: {skin_thickness*1000:.1f} мм")
    print(f"   Шаг стрингеров: {stringer_spacing*1000:.0f} мм")
    
    for condition in ['hinged', 'clamped', 'mixed']:
        sigma_cr = local_skin_buckling(
            skin_thickness, stringer_spacing, material, condition
        )
        print(f"   {condition:8s}: σ_cr = {sigma_cr/1e6:.2f} МПа")
    
    # Тест 2: Влияние толщины обшивки
    print("\n2. Влияние толщины обшивки (шаг стрингеров = 150 мм, hinged):")
    for t_mm in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        t = t_mm / 1000
        sigma_cr = local_skin_buckling(
            t, stringer_spacing, material, 'hinged'
        )
        print(f"   t = {t_mm:4.1f} мм: σ_cr = {sigma_cr/1e6:6.2f} МПа")
    
    # Тест 3: Влияние шага стрингеров
    print("\n3. Влияние шага стрингеров (толщина = 3 мм, hinged):")
    for s_mm in [100, 120, 150, 180, 200]:
        s = s_mm / 1000
        sigma_cr = local_skin_buckling(
            skin_thickness, s, material, 'hinged'
        )
        print(f"   s = {s_mm:3d} мм: σ_cr = {sigma_cr/1e6:6.2f} МПа")
    
    # Тест 4: Проверка формулы
    print("\n4. Проверка формулы:")
    t = 0.003  # 3 мм
    b_p = 0.15  # 15 см
    E = material.young_modulus
    nu = material.poisson_ratio
    k_sigma = 4.0  # hinged
    
    # Расчёт вручную
    sigma_manual = (
        k_sigma * math.pi**2 * E / 
        (12 * (1 - nu**2)) * 
        (t / b_p)**2
    )
    
    # Расчёт функцией
    sigma_func = local_skin_buckling(t, b_p, material, 'hinged')
    
    print(f"   Формула вручную: {sigma_manual/1e6:.2f} МПа")
    print(f"   Функция:         {sigma_func/1e6:.2f} МПа")
    print(f"   Разница:         {abs(sigma_manual - sigma_func)/1e6:.4f} МПа")
    print(f"   Совпадение:      {'✓' if abs(sigma_manual - sigma_func) < 1e-6 else '✗'}")
    
    # Тест 5: Валидация
    print("\n5. Тест валидации:")
    try:
        local_skin_buckling(-0.001, stringer_spacing, material, 'hinged')
        print("   ОШИБКА: не сработала валидация для отрицательной толщины")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательной толщины: {e}")
    
    try:
        local_skin_buckling(skin_thickness, -0.1, material, 'hinged')
        print("   ОШИБКА: не сработала валидация для отрицательного шага")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательного шага: {e}")
    
    try:
        local_skin_buckling(skin_thickness, stringer_spacing, material, 'invalid')
        print("   ОШИБКА: не сработала валидация граничных условий")
    except ValueError as e:
        print(f"   ✓ Валидация граничных условий: {e}")
    
    # Тест 6: Сравнение с пределом прочности
    print("\n6. Сравнение с пределом прочности материала:")
    sigma_cr = local_skin_buckling(skin_thickness, stringer_spacing, material, 'hinged')
    print(f"   Критическое напряжение: {sigma_cr/1e6:.2f} МПа")
    print(f"   Предел прочности: {material.ultimate_strength/1e6:.0f} МПа")
    print(f"   Предел текучести: {material.yield_strength/1e6:.0f} МПа")
    print(f"   Отношение σ_cr / σ_в: {sigma_cr / material.ultimate_strength:.3f}")
    
    # Тест 7: Типовые значения для Boeing 737-800
    print("\n7. Типовые значения для Boeing 737-800:")
    print("   (толщина обшивки 2-4 мм, шаг стрингеров 120-180 мм)")
    for t_mm in [2.0, 2.5, 3.0, 3.5]:
        for s_mm in [120, 150, 180]:
            t = t_mm / 1000
            s = s_mm / 1000
            sigma_cr = local_skin_buckling(t, s, material, 'hinged')
            print(f"   t={t_mm:.1f}мм, s={s_mm}мм: σ_cr={sigma_cr/1e6:5.1f} МПа")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    import math
    test_skin_buckling()

