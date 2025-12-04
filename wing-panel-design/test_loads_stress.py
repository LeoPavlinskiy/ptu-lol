#!/usr/bin/env python3
"""
Тест для функций расчёта напряжений в модуле loads
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from loads import (
    calculate_bending_stress,
    calculate_neutral_axis,
    calculate_stress_distribution
)

def test_stress_calculation():
    """Тестирование функций расчёта напряжений"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РАСЧЁТА НАПРЯЖЕНИЙ")
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
    
    # Тест 1: Расчёт напряжения от изгибающего момента
    print("\n1. Расчёт напряжения от изгибающего момента:")
    M = 4.66e6  # Н·м (для сечения 0.4)
    I_eff = panel.reduced_inertia
    y_max = panel.box_height / 2  # расстояние до крайнего волокна
    
    stress = calculate_bending_stress(M, I_eff, y_max)
    print(f"   Изгибающий момент: {M/1e6:.2f} МН·м")
    print(f"   Момент инерции: {I_eff*1e8:.2f} см⁴")
    print(f"   Расстояние до крайнего волокна: {y_max*1000:.1f} мм")
    print(f"   Напряжение: {stress/1e6:.2f} МПа")
    
    # Тест 2: Определение нейтральной оси
    print("\n2. Определение нейтральной оси:")
    try:
        neutral_axis = calculate_neutral_axis(panel, panel.stringers)
        print(f"   Нейтральная ось: {neutral_axis*1000:.2f} мм от нижнего края")
        print(f"   Высота кессона: {panel.box_height*1000:.1f} мм")
        print(f"   Расстояние от нейтральной оси до верхнего края: "
              f"{(panel.box_height - neutral_axis)*1000:.2f} мм")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # Тест 3: Распределение напряжений
    print("\n3. Распределение напряжений в сечении:")
    try:
        stress_dist = calculate_stress_distribution(panel, panel.stringers, M)
        print(f"   Нейтральная ось: {stress_dist['neutral_axis']*1000:.2f} мм")
        print(f"   Напряжение в обшивке: {stress_dist['skin_stress']/1e6:.2f} МПа")
        print(f"   Напряжение в стрингерах:")
        for i, s_stress in enumerate(stress_dist['stringer_stresses'], 1):
            print(f"      Стрингер {i}: {s_stress/1e6:.2f} МПа")
        print(f"   Максимальное напряжение: {stress_dist['max_stress']/1e6:.2f} МПа")
        print(f"   Минимальное напряжение: {stress_dist['min_stress']/1e6:.2f} МПа")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # Тест 4: Валидация
    print("\n4. Тест валидации:")
    try:
        calculate_bending_stress(M, 0, y_max)
        print("   ОШИБКА: не сработала валидация для I_eff = 0")
    except ValueError as e:
        print(f"   ✓ Валидация I_eff = 0: {e}")
    
    try:
        calculate_bending_stress(M, I_eff, 0)
        print("   ОШИБКА: не сработала валидация для y_max = 0")
    except ValueError as e:
        print(f"   ✓ Валидация y_max = 0: {e}")
    
    # Тест 5: Проверка формулы
    print("\n5. Проверка формулы σ = M * y / I:")
    M_test = 1e6  # 1 МН·м
    I_test = 1e-4  # 100 см⁴
    y_test = 0.2  # 20 см
    
    stress_test = calculate_bending_stress(M_test, I_test, y_test)
    stress_manual = M_test * y_test / I_test
    
    print(f"   M = {M_test/1e6:.1f} МН·м, I = {I_test*1e8:.0f} см⁴, y = {y_test*1000:.0f} мм")
    print(f"   Функция: {stress_test/1e6:.2f} МПа")
    print(f"   Вручную: {stress_manual/1e6:.2f} МПа")
    print(f"   Совпадение: {'✓' if abs(stress_test - stress_manual) < 1e-6 else '✗'}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_stress_calculation()

