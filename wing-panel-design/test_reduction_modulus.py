#!/usr/bin/env python3
"""
Тест для функции расчёта редуцированного модуля упругости
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from reduction import reduced_modulus

def test_reduced_modulus():
    """Тестирование функции расчёта редуцированного модуля"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РЕДУЦИРОВАННОГО МОДУЛЯ УПРУГОСТИ")
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
    panel.effective_skin_width = 0.12  # 12 см (редуцированная)
    
    # Создание стрингеров
    stringer1 = Stringer('Z')
    stringer1.set_geometry_from_typical()
    stringer1.calculate_area()
    
    stringer2 = Stringer('Z')
    stringer2.set_geometry_from_typical()
    stringer2.calculate_area()
    
    panel.add_stringer(stringer1)
    panel.add_stringer(stringer2)
    
    # Тест 1: Редуцированный модуль для разных уровней напряжений
    print("\n1. Редуцированный модуль для разных уровней напряжений:")
    E = material.young_modulus
    print(f"   Модуль упругости: {E/1e9:.0f} ГПа")
    print(f"   Предел текучести: {material.yield_strength/1e6:.0f} МПа")
    print(f"   Порог пластичности (0.6*σ_y): {0.6*material.yield_strength/1e6:.0f} МПа")
    
    stress_levels = [50e6, 100e6, 200e6, 264e6, 300e6, 400e6, 440e6]
    for stress in stress_levels:
        E_red = reduced_modulus(panel, panel.stringers, material, stress)
        E_ratio = E_red / E
        print(f"   σ = {stress/1e6:3.0f} МПа: E_red = {E_red/1e9:5.1f} ГПа ({E_ratio:.3f} от E)")
    
    # Тест 2: Влияние эффективной ширины обшивки
    print("\n2. Влияние эффективной ширины обшивки (σ = 300 МПа):")
    stress = 300e6
    for b_eff_mm in [150, 120, 100, 80, 60]:
        panel.effective_skin_width = b_eff_mm / 1000
        E_red = reduced_modulus(panel, panel.stringers, material, stress)
        E_ratio = E_red / E
        print(f"   b_eff = {b_eff_mm:3d} мм: E_red = {E_red/1e9:5.1f} ГПа ({E_ratio:.3f} от E)")
    
    # Тест 3: Проверка формулы
    print("\n3. Проверка формулы:")
    panel.effective_skin_width = 0.12  # 12 см
    stress = 200e6
    
    A_s = sum(s.area for s in panel.stringers)
    A_skin_eff = panel.skin_thickness * panel.effective_skin_width
    
    # Касательный модуль (упрощённо)
    threshold = 0.6 * material.yield_strength
    if stress < threshold:
        E_t = E
    else:
        stress_range = material.yield_strength - threshold
        stress_excess = stress - threshold
        E_t_min = 0.1 * E
        E_t = E - (E - E_t_min) * (stress_excess / stress_range)
    
    # Расчёт вручную
    E_red_manual = (E * A_s + E_t * A_skin_eff) / (A_s + A_skin_eff)
    
    # Расчёт функцией
    E_red_func = reduced_modulus(panel, panel.stringers, material, stress)
    
    print(f"   Площадь стрингеров: {A_s*1e4:.2f} см²")
    print(f"   Эффективная площадь обшивки: {A_skin_eff*1e4:.2f} см²")
    print(f"   Касательный модуль: {E_t/1e9:.1f} ГПа")
    print(f"   Формула вручную: {E_red_manual/1e9:.2f} ГПа")
    print(f"   Функция:         {E_red_func/1e9:.2f} ГПа")
    print(f"   Разница:         {abs(E_red_manual - E_red_func)/1e9:.4f} ГПа")
    print(f"   Совпадение:      {'✓' if abs(E_red_manual - E_red_func) < 1e6 else '✗'}")
    
    # Тест 4: Влияние количества стрингеров
    print("\n4. Влияние количества стрингеров (σ = 300 МПа, b_eff = 120 мм):")
    panel.effective_skin_width = 0.12
    stress = 300e6
    
    for n_stringers in [1, 2, 3, 4]:
        # Создаём новую панель с нужным количеством стрингеров
        panel_test = Panel(0.4, aircraft, material)
        panel_test.skin_thickness = 0.003
        panel_test.stringer_spacing = 0.15
        panel_test.effective_skin_width = 0.12
        
        stringers_test = []
        for i in range(n_stringers):
            s = Stringer('Z')
            s.set_geometry_from_typical()
            s.calculate_area()
            stringers_test.append(s)
        
        E_red = reduced_modulus(panel_test, stringers_test, material, stress)
        A_s_total = sum(s.area for s in stringers_test)
        E_ratio = E_red / E
        print(f"   {n_stringers} стрингер(ов), A_s = {A_s_total*1e4:.2f} см²: "
              f"E_red = {E_red/1e9:5.1f} ГПа ({E_ratio:.3f} от E)")
    
    # Тест 5: Валидация
    print("\n5. Тест валидации:")
    panel.effective_skin_width = 0.12
    
    # Панель без установленной толщины
    panel_empty = Panel(0.4, aircraft, material)
    try:
        reduced_modulus(panel_empty, panel.stringers, material, 200e6)
        print("   ОШИБКА: не сработала валидация отсутствующей толщины")
    except ValueError as e:
        print(f"   ✓ Валидация отсутствующей толщины: {e}")
    
    # Панель без стрингеров
    try:
        reduced_modulus(panel, [], material, 200e6)
        print("   ОШИБКА: не сработала валидация отсутствия стрингеров")
    except ValueError as e:
        print(f"   ✓ Валидация отсутствия стрингеров: {e}")
    
    # Тест 6: Граничные случаи
    print("\n6. Граничные случаи:")
    panel.effective_skin_width = 0.12
    
    # Низкое напряжение (упругая область)
    E_red_low = reduced_modulus(panel, panel.stringers, material, 50e6)
    print(f"   Низкое напряжение (50 МПа): E_red = {E_red_low/1e9:.2f} ГПа "
          f"({E_red_low/E:.3f} от E)")
    
    # Высокое напряжение (пластическая область)
    E_red_high = reduced_modulus(panel, panel.stringers, material, 440e6)
    print(f"   Высокое напряжение (440 МПа = σ_y): E_red = {E_red_high/1e9:.2f} ГПа "
          f"({E_red_high/E:.3f} от E)")
    
    # Очень высокая эффективная ширина (почти полная)
    panel.effective_skin_width = 0.149  # почти полная ширина
    E_red_full = reduced_modulus(panel, panel.stringers, material, 300e6)
    print(f"   Почти полная ширина обшивки: E_red = {E_red_full/1e9:.2f} ГПа "
          f"({E_red_full/E:.3f} от E)")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_reduced_modulus()

