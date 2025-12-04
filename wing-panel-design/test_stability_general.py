#!/usr/bin/env python3
"""
Тест для функции расчёта общей потери устойчивости панели
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from stability import general_panel_buckling

def test_general_buckling():
    """Тестирование функции расчёта общей потери устойчивости"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ОБЩЕЙ ПОТЕРИ УСТОЙЧИВОСТИ ПАНЕЛИ")
    print("=" * 60)
    
    # Создание объектов
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    panel = Panel(0.4, aircraft, material)
    
    # Установка параметров панели
    panel.calculate_panel_width()
    panel.calculate_box_height()
    panel.skin_thickness = 0.003  # 3 мм
    panel.stringer_spacing = 0.15  # 15 см
    panel.effective_skin_width = 0.15  # начальное значение
    
    # Создание стрингеров
    stringer1 = Stringer('Z')
    stringer1.set_geometry_from_typical()
    stringer1.calculate_area()
    stringer1.calculate_inertia()
    
    stringer2 = Stringer('Z')
    stringer2.set_geometry_from_typical()
    stringer2.calculate_area()
    stringer2.calculate_inertia()
    
    panel.add_stringer(stringer1)
    panel.add_stringer(stringer2)
    
    # Расчёт эффективных параметров
    panel.calculate_effective_area()
    panel.calculate_effective_inertia()
    
    # Длина панели (типовое значение для Boeing 737-800)
    panel_length = 0.5  # 0.5 м (расстояние между нервюрами)
    
    # Тест 1: Критическое напряжение для разных граничных условий
    print("\n1. Критическое напряжение для разных граничных условий:")
    print(f"   Длина панели: {panel_length*1000:.0f} мм")
    print(f"   Эффективная площадь: {panel.reduced_area*1e4:.2f} см²")
    print(f"   Эффективный момент инерции: {panel.reduced_inertia*1e8:.2f} см⁴")
    
    for condition in ['hinged', 'clamped', 'mixed', 'cantilever']:
        try:
            sigma_cr = general_panel_buckling(
                panel, panel.stringers, material, panel_length, condition
            )
            print(f"   {condition:10s}: σ_cr = {sigma_cr/1e6:.2f} МПа")
        except Exception as e:
            print(f"   {condition:10s}: ОШИБКА - {e}")
    
    # Тест 2: Влияние длины панели
    print("\n2. Влияние длины панели (boundary_condition='hinged'):")
    for L_m in [0.3, 0.4, 0.5, 0.6, 0.7]:
        try:
            sigma_cr = general_panel_buckling(
                panel, panel.stringers, material, L_m, 'hinged'
            )
            print(f"   L = {L_m*1000:.0f} мм: σ_cr = {sigma_cr/1e6:.2f} МПа")
        except Exception as e:
            print(f"   L = {L_m*1000:.0f} мм: ОШИБКА - {e}")
    
    # Тест 3: Влияние редуцированного модуля
    print("\n3. Влияние редуцированного модуля:")
    E_normal = material.young_modulus
    for E_ratio in [1.0, 0.8, 0.6, 0.4]:
        E_red = E_normal * E_ratio
        try:
            sigma_cr = general_panel_buckling(
                panel, panel.stringers, material, panel_length, 'hinged', E_red
            )
            print(f"   E_red/E = {E_ratio:.1f}: σ_cr = {sigma_cr/1e6:.2f} МПа")
        except Exception as e:
            print(f"   E_red/E = {E_ratio:.1f}: ОШИБКА - {e}")
    
    # Тест 4: Проверка формулы
    print("\n4. Проверка формулы Эйлера:")
    # Расчёт вручную
    A_eff = panel.reduced_area
    I_eff = panel.reduced_inertia
    E_red = material.young_modulus
    mu = 1.0  # hinged
    L = panel_length
    
    r_eff = math.sqrt(I_eff / A_eff)
    lambda_eff = (mu * L) / r_eff
    sigma_manual = (math.pi**2 * E_red) / (lambda_eff**2)
    
    # Расчёт функцией
    sigma_func = general_panel_buckling(
        panel, panel.stringers, material, panel_length, 'hinged'
    )
    
    print(f"   Эффективный радиус инерции: {r_eff*1000:.2f} мм")
    print(f"   Эффективная гибкость: {lambda_eff:.2f}")
    print(f"   Формула вручную: {sigma_manual/1e6:.2f} МПа")
    print(f"   Функция:         {sigma_func/1e6:.2f} МПа")
    print(f"   Разница:         {abs(sigma_manual - sigma_func)/1e6:.4f} МПа")
    print(f"   Совпадение:      {'✓' if abs(sigma_manual - sigma_func) < 1e-6 else '✗'}")
    
    # Тест 5: Валидация
    print("\n5. Тест валидации:")
    try:
        general_panel_buckling(panel, panel.stringers, material, -0.1, 'hinged')
        print("   ОШИБКА: не сработала валидация для отрицательной длины")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательной длины: {e}")
    
    try:
        general_panel_buckling(panel, panel.stringers, material, panel_length, 'invalid')
        print("   ОШИБКА: не сработала валидация граничных условий")
    except ValueError as e:
        print(f"   ✓ Валидация граничных условий: {e}")
    
    # Тест 6: Панель без рассчитанных параметров
    print("\n6. Тест панели без рассчитанных параметров:")
    panel_empty = Panel(0.4, aircraft, material)
    try:
        general_panel_buckling(panel_empty, [], material, panel_length, 'hinged')
        print("   ОШИБКА: не сработала валидация отсутствующих параметров")
    except ValueError as e:
        print(f"   ✓ Валидация отсутствующих параметров: {e}")
    
    # Тест 7: Сравнение с пределом прочности
    print("\n7. Сравнение с пределом прочности материала:")
    sigma_cr = general_panel_buckling(
        panel, panel.stringers, material, panel_length, 'hinged'
    )
    print(f"   Критическое напряжение: {sigma_cr/1e6:.2f} МПа")
    print(f"   Предел прочности: {material.ultimate_strength/1e6:.0f} МПа")
    print(f"   Предел текучести: {material.yield_strength/1e6:.0f} МПа")
    print(f"   Отношение σ_cr / σ_в: {sigma_cr / material.ultimate_strength:.3f}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    import math
    test_general_buckling()

