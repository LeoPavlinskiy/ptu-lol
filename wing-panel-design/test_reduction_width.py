#!/usr/bin/env python3
"""
Тест для функции расчёта эффективной ширины обшивки
"""

from material import Material
from reduction import effective_width

def test_effective_width():
    """Тестирование функции расчёта эффективной ширины"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЭФФЕКТИВНОЙ ШИРИНЫ ОБШИВКИ")
    print("=" * 60)
    
    material = Material('B95T1', 'sheet')
    
    # Типовые параметры
    skin_width = 0.15  # 15 см (шаг стрингеров)
    sigma_cr = 108e6  # 108 МПа (критическое напряжение для t=3мм, s=150мм)
    
    # Тест 1: Метод Винтера для разных напряжений
    print("\n1. Метод Винтера (разные напряжения на краю):")
    print(f"   Полная ширина: {skin_width*1000:.0f} мм")
    print(f"   Критическое напряжение: {sigma_cr/1e6:.1f} МПа")
    print(f"   Предел текучести: {material.yield_strength/1e6:.0f} МПа")
    
    for sigma_edge_mpa in [50, 100, 150, 200, 300, 400, 440]:
        sigma_edge = sigma_edge_mpa * 1e6
        b_eff, rho = effective_width(
            skin_width, sigma_cr, sigma_edge, material, 'winter'
        )
        print(f"   σ_edge = {sigma_edge_mpa:3d} МПа: "
              f"b_eff = {b_eff*1000:5.1f} мм, ρ = {rho:.3f}")
    
    # Тест 2: Метод фон Кармана
    print("\n2. Метод фон Кармана (упругая область):")
    for sigma_edge_mpa in [50, 100, 150, 200, 300]:
        sigma_edge = sigma_edge_mpa * 1e6
        b_eff, rho = effective_width(
            skin_width, sigma_cr, sigma_edge, material, 'karman'
        )
        print(f"   σ_edge = {sigma_edge_mpa:3d} МПа: "
              f"b_eff = {b_eff*1000:5.1f} мм, ρ = {rho:.3f}")
    
    # Тест 3: Сравнение методов
    print("\n3. Сравнение методов Винтера и Кармана:")
    sigma_edge = 200e6  # 200 МПа
    b_eff_winter, rho_winter = effective_width(
        skin_width, sigma_cr, sigma_edge, material, 'winter'
    )
    b_eff_karman, rho_karman = effective_width(
        skin_width, sigma_cr, sigma_edge, material, 'karman'
    )
    
    print(f"   σ_edge = {sigma_edge/1e6:.0f} МПа:")
    print(f"      Винтер:  b_eff = {b_eff_winter*1000:.1f} мм, ρ = {rho_winter:.3f}")
    print(f"      Карман:  b_eff = {b_eff_karman*1000:.1f} мм, ρ = {rho_karman:.3f}")
    print(f"      Разница: {abs(b_eff_winter - b_eff_karman)*1000:.1f} мм")
    
    # Тест 4: Влияние критического напряжения
    print("\n4. Влияние критического напряжения (метод Винтера, σ_edge = 300 МПа):")
    sigma_edge = 300e6
    for sigma_cr_mpa in [50, 75, 100, 125, 150]:
        sigma_cr_test = sigma_cr_mpa * 1e6
        b_eff, rho = effective_width(
            skin_width, sigma_cr_test, sigma_edge, material, 'winter'
        )
        lambda_p = math.sqrt(material.yield_strength / sigma_cr_test)
        print(f"   σ_cr = {sigma_cr_mpa:3d} МПа (λ_p = {lambda_p:.3f}): "
              f"b_eff = {b_eff*1000:5.1f} мм, ρ = {rho:.3f}")
    
    # Тест 5: Проверка формулы Винтера
    print("\n5. Проверка формулы Винтера:")
    sigma_cr_test = 108e6
    lambda_p = math.sqrt(material.yield_strength / sigma_cr_test)
    
    if lambda_p <= 0.673:
        rho_manual = 1.0
    else:
        rho_manual = (1 - 0.22 / lambda_p) / lambda_p
    
    b_eff_manual = rho_manual * skin_width
    
    b_eff_func, rho_func = effective_width(
        skin_width, sigma_cr_test, material.yield_strength, material, 'winter'
    )
    
    print(f"   Параметр тонкостенности: λ_p = {lambda_p:.3f}")
    print(f"   Формула вручную: ρ = {rho_manual:.3f}, b_eff = {b_eff_manual*1000:.1f} мм")
    print(f"   Функция:         ρ = {rho_func:.3f}, b_eff = {b_eff_func*1000:.1f} мм")
    print(f"   Совпадение:      {'✓' if abs(rho_manual - rho_func) < 1e-6 else '✗'}")
    
    # Тест 6: Проверка формулы Кармана
    print("\n6. Проверка формулы Кармана:")
    sigma_edge_test = 200e6
    if sigma_edge_test > sigma_cr:
        b_eff_manual = skin_width * math.sqrt(sigma_cr / sigma_edge_test)
    else:
        b_eff_manual = skin_width
    
    b_eff_func, rho_func = effective_width(
        skin_width, sigma_cr, sigma_edge_test, material, 'karman'
    )
    
    print(f"   σ_edge = {sigma_edge_test/1e6:.0f} МПа, σ_cr = {sigma_cr/1e6:.1f} МПа")
    print(f"   Формула вручную: b_eff = {b_eff_manual*1000:.1f} мм")
    print(f"   Функция:         b_eff = {b_eff_func*1000:.1f} мм")
    print(f"   Совпадение:      {'✓' if abs(b_eff_manual - b_eff_func) < 1e-6 else '✗'}")
    
    # Тест 7: Валидация
    print("\n7. Тест валидации:")
    try:
        effective_width(-0.1, sigma_cr, 200e6, material, 'winter')
        print("   ОШИБКА: не сработала валидация для отрицательной ширины")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательной ширины: {e}")
    
    try:
        effective_width(skin_width, -sigma_cr, 200e6, material, 'winter')
        print("   ОШИБКА: не сработала валидация для отрицательного σ_cr")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательного σ_cr: {e}")
    
    try:
        effective_width(skin_width, sigma_cr, 200e6, material, 'invalid')
        print("   ОШИБКА: не сработала валидация метода")
    except ValueError as e:
        print(f"   ✓ Валидация метода: {e}")
    
    # Тест 8: Граничные случаи
    print("\n8. Граничные случаи:")
    # Случай 1: Напряжение меньше критического
    b_eff, rho = effective_width(
        skin_width, sigma_cr, 50e6, material, 'winter'
    )
    print(f"   σ_edge < σ_cr (50 МПа < 108 МПа): b_eff = {b_eff*1000:.1f} мм, ρ = {rho:.3f}")
    
    # Случай 2: Напряжение равно критическому
    b_eff, rho = effective_width(
        skin_width, sigma_cr, sigma_cr, material, 'winter'
    )
    print(f"   σ_edge = σ_cr: b_eff = {b_eff*1000:.1f} мм, ρ = {rho:.3f}")
    
    # Случай 3: Напряжение равно пределу текучести
    b_eff, rho = effective_width(
        skin_width, sigma_cr, material.yield_strength, material, 'winter'
    )
    print(f"   σ_edge = σ_y ({material.yield_strength/1e6:.0f} МПа): "
          f"b_eff = {b_eff*1000:.1f} мм, ρ = {rho:.3f}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    import math
    test_effective_width()

