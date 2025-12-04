#!/usr/bin/env python3
"""
Тест для модуля strength
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from reduction import iterative_reduction
from strength import (
    calculate_stresses,
    check_strength,
    check_panel_strength
)

def test_strength():
    """Тестирование функций расчёта напряжений и проверки прочности"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ strength")
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
    
    # Итерационный расчёт с редуцированием
    moment = 4.66e6  # 4.66 МН·м
    panel_length = 0.5  # 0.5 м
    
    print("\n1. Итерационный расчёт с редуцированием:")
    panel_result, stringers_result, iterations, conv_info = iterative_reduction(
        panel, panel.stringers, material, moment, panel_length
    )
    print(f"   Итераций: {iterations}")
    print(f"   Эффективная ширина: {conv_info['final_b_eff']*1000:.1f} мм")
    
    # Тест 2: Расчёт напряжений
    print("\n2. Расчёт напряжений в панели:")
    try:
        stresses = calculate_stresses(panel_result, stringers_result, moment, material)
        print(f"   Напряжение в обшивке: {stresses['skin']/1e6:.2f} МПа")
        print(f"   Напряжение в стрингерах: {stresses['stringers']/1e6:.2f} МПа")
        print(f"   Максимальное напряжение: {stresses['max']/1e6:.2f} МПа")
        print(f"   Минимальное напряжение: {stresses['min']/1e6:.2f} МПа")
        print(f"   Нейтральная ось: {stresses['neutral_axis']*1000:.2f} мм от нижнего края")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 3: Проверка прочности
    print("\n3. Проверка прочности:")
    test_stresses = [100e6, 200e6, 300e6, 400e6, 440e6]
    for stress in test_stresses:
        check = check_strength(stress, material, 'compression')
        status = "✓ Безопасно" if check['safe'] else "✗ Превышение"
        print(f"   σ = {stress/1e6:.0f} МПа:")
        print(f"      Допускаемое: {check['allowable']/1e6:.0f} МПа")
        print(f"      Предел пропорциональности: {check['proportional_limit']/1e6:.0f} МПа")
        print(f"      Запас (допускаемое): {check['safety_margin_allowable']:.2f}")
        print(f"      Запас (пропорциональность): {check['safety_margin_proportional']:.2f}")
        print(f"      {status}")
    
    # Тест 4: Полная проверка прочности панели
    print("\n4. Полная проверка прочности панели:")
    try:
        strength_check = check_panel_strength(panel_result, stringers_result, moment, material)
        
        print(f"   Напряжения:")
        print(f"      Обшивка: {strength_check['stresses']['skin']/1e6:.2f} МПа")
        print(f"      Стрингеры: {strength_check['stresses']['stringers']/1e6:.2f} МПа")
        print(f"      Максимальное: {strength_check['stresses']['max']/1e6:.2f} МПа")
        
        print(f"\n   Проверка обшивки:")
        skin = strength_check['skin_check']
        print(f"      Напряжение: {skin['stress']/1e6:.2f} МПа")
        print(f"      Допускаемое: {skin['allowable']/1e6:.0f} МПа")
        print(f"      Запас: {skin['safety_margin_allowable']:.2f}")
        print(f"      Безопасно: {'✓' if skin['safe'] else '✗'}")
        
        print(f"\n   Проверка стрингеров:")
        for sc in strength_check['stringer_checks']:
            check = sc['check']
            print(f"      Стрингер {sc['stringer_index']+1}: "
                  f"σ = {check['stress']/1e6:.2f} МПа, "
                  f"запас = {check['safety_margin_allowable']:.2f}, "
                  f"{'✓' if check['safe'] else '✗'}")
        
        print(f"\n   Общая безопасность: {'✓' if strength_check['overall_safe'] else '✗'}")
        
    except Exception as e:
        print(f"   ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 5: Разные типы нагрузок
    print("\n5. Проверка для разных типов нагрузок:")
    stress = 250e6
    for load_type in ['tension', 'compression', 'shear']:
        check = check_strength(stress, material, load_type)
        print(f"   {load_type:12s}: σ = {stress/1e6:.0f} МПа, "
              f"допускаемое = {check['allowable']/1e6:.0f} МПа, "
              f"запас = {check['safety_margin_allowable']:.2f}, "
              f"{'✓' if check['safe'] else '✗'}")
    
    # Тест 6: Валидация
    print("\n6. Тест валидации:")
    panel_empty = Panel(0.4, aircraft, material)
    try:
        calculate_stresses(panel_empty, [], moment, material)
        print("   ОШИБКА: не сработала валидация отсутствующих параметров")
    except ValueError as e:
        print(f"   ✓ Валидация: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_strength()

