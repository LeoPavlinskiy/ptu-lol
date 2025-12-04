#!/usr/bin/env python3
"""
Тест для функции итерационного расчёта с редуцированием
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from reduction import iterative_reduction

def test_iterative_reduction():
    """Тестирование итерационного алгоритма редуцирования"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИТЕРАЦИОННОГО РАСЧЁТА С РЕДУЦИРОВАНИЕМ")
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
    
    # Изгибающий момент для сечения 0.4
    moment = 4.66e6  # 4.66 МН·м
    panel_length = 0.5  # 0.5 м (расстояние между нервюрами)
    
    # Тест 1: Базовый итерационный расчёт
    print("\n1. Базовый итерационный расчёт:")
    print(f"   Изгибающий момент: {moment/1e6:.2f} МН·м")
    print(f"   Длина панели: {panel_length*1000:.0f} мм")
    print(f"   Толщина обшивки: {panel.skin_thickness*1000:.1f} мм")
    print(f"   Шаг стрингеров: {panel.stringer_spacing*1000:.0f} мм")
    
    panel_test = Panel(0.4, aircraft, material)
    panel_test.calculate_panel_width()
    panel_test.calculate_box_height()
    panel_test.skin_thickness = 0.003
    panel_test.stringer_spacing = 0.15
    
    stringers_test = []
    for i in range(2):
        s = Stringer('Z')
        s.set_geometry_from_typical()
        s.calculate_area()
        s.calculate_inertia()
        stringers_test.append(s)
        panel_test.add_stringer(s)
    
    try:
        panel_result, stringers_result, iterations, conv_info = iterative_reduction(
            panel_test, stringers_test, material, moment, panel_length
        )
        
        print(f"\n   Результаты:")
        print(f"      Итераций: {iterations}")
        print(f"      Сходимость: {'✓' if conv_info['converged'] else '✗'}")
        print(f"      Начальная ширина: {panel.stringer_spacing*1000:.1f} мм")
        print(f"      Эффективная ширина: {conv_info['final_b_eff']*1000:.1f} мм")
        print(f"      Коэффициент редуцирования: {conv_info['final_b_eff']/panel.stringer_spacing:.3f}")
        print(f"      Напряжение на краю: {conv_info['final_sigma_edge']/1e6:.2f} МПа")
        print(f"      Критическое напряжение: {conv_info['final_sigma_cr']/1e6:.2f} МПа")
        print(f"      Эффективная площадь: {panel_result.reduced_area*1e4:.2f} см²")
        print(f"      Эффективный момент инерции: {panel_result.reduced_inertia*1e8:.2f} см⁴")
        
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 2: Разные методы редуцирования
    print("\n2. Сравнение методов редуцирования:")
    for method in ['winter', 'karman']:
        panel_test = Panel(0.4, aircraft, material)
        panel_test.calculate_panel_width()
        panel_test.calculate_box_height()
        panel_test.skin_thickness = 0.003
        panel_test.stringer_spacing = 0.15
        
        stringers_test = []
        for i in range(2):
            s = Stringer('Z')
            s.set_geometry_from_typical()
            s.calculate_area()
            s.calculate_inertia()
            stringers_test.append(s)
            panel_test.add_stringer(s)
        
        try:
            panel_result, _, iterations, conv_info = iterative_reduction(
                panel_test, stringers_test, material, moment, panel_length,
                method=method
            )
            print(f"   {method:6s}: итераций={iterations}, "
                  f"b_eff={conv_info['final_b_eff']*1000:.1f} мм, "
                  f"σ={conv_info['final_sigma_edge']/1e6:.1f} МПа")
        except Exception as e:
            print(f"   {method:6s}: ОШИБКА - {e}")
    
    # Тест 3: Разные моменты
    print("\n3. Влияние изгибающего момента:")
    moments = [2e6, 4e6, 6e6, 8e6]  # МН·м
    for M in moments:
        panel_test = Panel(0.4, aircraft, material)
        panel_test.calculate_panel_width()
        panel_test.calculate_box_height()
        panel_test.skin_thickness = 0.003
        panel_test.stringer_spacing = 0.15
        
        stringers_test = []
        for i in range(2):
            s = Stringer('Z')
            s.set_geometry_from_typical()
            s.calculate_area()
            s.calculate_inertia()
            stringers_test.append(s)
            panel_test.add_stringer(s)
        
        try:
            panel_result, _, iterations, conv_info = iterative_reduction(
                panel_test, stringers_test, material, M, panel_length
            )
            print(f"   M = {M/1e6:.1f} МН·м: итераций={iterations}, "
                  f"b_eff={conv_info['final_b_eff']*1000:.1f} мм, "
                  f"σ={conv_info['final_sigma_edge']/1e6:.1f} МПа")
        except Exception as e:
            print(f"   M = {M/1e6:.1f} МН·м: ОШИБКА - {e}")
    
    # Тест 4: Разные толщины обшивки
    print("\n4. Влияние толщины обшивки (M = 4.66 МН·м):")
    for t_mm in [2.0, 2.5, 3.0, 3.5, 4.0]:
        panel_test = Panel(0.4, aircraft, material)
        panel_test.calculate_panel_width()
        panel_test.calculate_box_height()
        panel_test.skin_thickness = t_mm / 1000
        panel_test.stringer_spacing = 0.15
        
        stringers_test = []
        for i in range(2):
            s = Stringer('Z')
            s.set_geometry_from_typical()
            s.calculate_area()
            s.calculate_inertia()
            stringers_test.append(s)
            panel_test.add_stringer(s)
        
        try:
            panel_result, _, iterations, conv_info = iterative_reduction(
                panel_test, stringers_test, material, moment, panel_length
            )
            print(f"   t = {t_mm:.1f} мм: итераций={iterations}, "
                  f"b_eff={conv_info['final_b_eff']*1000:.1f} мм, "
                  f"σ_cr={conv_info['final_sigma_cr']/1e6:.1f} МПа")
        except Exception as e:
            print(f"   t = {t_mm:.1f} мм: ОШИБКА - {e}")
    
    # Тест 5: Валидация
    print("\n5. Тест валидации:")
    panel_empty = Panel(0.4, aircraft, material)
    try:
        iterative_reduction(panel_empty, [], material, moment, panel_length)
        print("   ОШИБКА: не сработала валидация отсутствующих параметров")
    except ValueError as e:
        print(f"   ✓ Валидация: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_iterative_reduction()

