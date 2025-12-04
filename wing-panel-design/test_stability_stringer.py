#!/usr/bin/env python3
"""
Тест для функций расчёта местной потери устойчивости стрингера
"""

from material import Material
from stringer import Stringer
from stability import (
    local_stringer_buckling,
    check_stringer_local_buckling
)

def test_stringer_buckling():
    """Тестирование функций расчёта критического напряжения стрингера"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МЕСТНОЙ ПОТЕРИ УСТОЙЧИВОСТИ СТРИНГЕРА")
    print("=" * 60)
    
    material = Material('B95T1', 'sheet')
    
    # Тест 1: Критическое напряжение для разных типов элементов
    print("\n1. Критическое напряжение для разных типов элементов:")
    element_width = 0.025  # 25 мм (высота стенки или ширина полки)
    element_thickness = 0.002  # 2 мм
    
    print(f"   Ширина элемента: {element_width*1000:.0f} мм")
    print(f"   Толщина элемента: {element_thickness*1000:.1f} мм")
    
    for element_type in ['web', 'flange_internal', 'flange_free', 'flange_Z']:
        sigma_cr = local_stringer_buckling(
            element_width, element_thickness, material, element_type
        )
        print(f"   {element_type:18s}: σ_cr = {sigma_cr/1e6:.2f} МПа")
    
    # Тест 2: Влияние размеров стенки
    print("\n2. Влияние размеров стенки (web, clamped):")
    for h_mm in [15, 20, 25, 30]:
        for t_mm in [1.5, 2.0, 2.5]:
            h = h_mm / 1000
            t = t_mm / 1000
            sigma_cr = local_stringer_buckling(h, t, material, 'web')
            print(f"   h={h_mm:2d}мм, t={t_mm:.1f}мм: σ_cr={sigma_cr/1e6:6.2f} МПа")
    
    # Тест 3: Влияние размеров полки
    print("\n3. Влияние размеров полки (flange_free, консоль):")
    for b_mm in [15, 20, 25]:
        for t_mm in [1.5, 2.0, 2.5]:
            b = b_mm / 1000
            t = t_mm / 1000
            sigma_cr = local_stringer_buckling(b, t, material, 'flange_free')
            print(f"   b={b_mm:2d}мм, t={t_mm:.1f}мм: σ_cr={sigma_cr/1e6:6.2f} МПа")
    
    # Тест 4: Проверка всех элементов стрингера
    print("\n4. Проверка всех элементов стрингера:")
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        
        # Рабочее напряжение (сжатие)
        stress = 200e6  # 200 МПа
        
        results = check_stringer_local_buckling(stringer, material, stress)
        
        print(f"\n   {st_type}-стрингер (σ = {stress/1e6:.0f} МПа):")
        
        if results['web']:
            web = results['web']
            if web.get('sigma_cr'):
                print(f"      Стенка: σ_cr = {web['sigma_cr']/1e6:.2f} МПа, "
                      f"безопасно: {'✓' if web['safe'] else '✗'}, "
                      f"запас: {web['safety_margin']:.2f}")
            else:
                print(f"      Стенка: {web.get('error', 'ошибка')}")
        
        for i, flange in enumerate(results['flanges'], 1):
            if flange.get('sigma_cr'):
                print(f"      Полка {i} ({flange['type']}): σ_cr = {flange['sigma_cr']/1e6:.2f} МПа, "
                      f"безопасно: {'✓' if flange['safe'] else '✗'}, "
                      f"запас: {flange['safety_margin']:.2f}")
            else:
                print(f"      Полка {i}: {flange.get('error', 'ошибка')}")
        
        print(f"      Общая безопасность: {'✓' if results['overall_safe'] else '✗'}")
    
    # Тест 5: Проверка формулы
    print("\n5. Проверка формулы:")
    b = 0.025  # 25 мм
    t = 0.002  # 2 мм
    E = material.young_modulus
    nu = material.poisson_ratio
    k = 6.97  # web_clamped
    
    # Расчёт вручную
    sigma_manual = (
        k * math.pi**2 * E / 
        (12 * (1 - nu**2)) * 
        (t / b)**2
    )
    
    # Расчёт функцией
    sigma_func = local_stringer_buckling(b, t, material, 'web')
    
    print(f"   Формула вручную: {sigma_manual/1e6:.2f} МПа")
    print(f"   Функция:         {sigma_func/1e6:.2f} МПа")
    print(f"   Разница:         {abs(sigma_manual - sigma_func)/1e6:.4f} МПа")
    print(f"   Совпадение:      {'✓' if abs(sigma_manual - sigma_func) < 1e-6 else '✗'}")
    
    # Тест 6: Валидация
    print("\n6. Тест валидации:")
    try:
        local_stringer_buckling(-0.001, 0.002, material, 'web')
        print("   ОШИБКА: не сработала валидация для отрицательной ширины")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательной ширины: {e}")
    
    try:
        local_stringer_buckling(0.025, -0.001, material, 'web')
        print("   ОШИБКА: не сработала валидация для отрицательной толщины")
    except ValueError as e:
        print(f"   ✓ Валидация отрицательной толщины: {e}")
    
    try:
        local_stringer_buckling(0.025, 0.002, material, 'invalid')
        print("   ОШИБКА: не сработала валидация типа элемента")
    except ValueError as e:
        print(f"   ✓ Валидация типа элемента: {e}")
    
    # Тест 7: Сравнение с пределом прочности
    print("\n7. Сравнение с пределом прочности материала:")
    sigma_cr_web = local_stringer_buckling(0.025, 0.002, material, 'web')
    sigma_cr_flange = local_stringer_buckling(0.020, 0.002, material, 'flange_free')
    
    print(f"   Стенка (web): σ_cr = {sigma_cr_web/1e6:.2f} МПа")
    print(f"   Полка (free): σ_cr = {sigma_cr_flange/1e6:.2f} МПа")
    print(f"   Предел прочности: {material.ultimate_strength/1e6:.0f} МПа")
    print(f"   Предел текучести: {material.yield_strength/1e6:.0f} МПа")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    import math
    test_stringer_buckling()

