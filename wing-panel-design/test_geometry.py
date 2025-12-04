#!/usr/bin/env python3
"""
Простой тест для модуля geometry
"""

from aircraft_data import Aircraft
from material import Material
from geometry import (
    calculate_chord,
    calculate_box_height,
    calculate_spar_positions,
    calculate_box_width,
    calculate_spar_flange_area,
    calculate_absolute_position
)

def test_geometry():
    """Тестирование функций расчёта геометрии"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ geometry")
    print("=" * 60)
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    
    # Тест 1: Расчёт хорды
    print("\n1. Расчёт хорды:")
    for z_rel in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        chord = calculate_chord(
            z_rel,
            aircraft.root_chord,
            aircraft.tip_chord,
            aircraft.wing_span
        )
        print(f"   z/L = {z_rel:.1f}: c = {chord:.3f} м")
    
    # Тест 2: Расчёт высоты кессона
    print("\n2. Расчёт высоты кессона:")
    for z_rel in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        height = calculate_box_height(z_rel, aircraft)
        print(f"   z/L = {z_rel:.1f}: h = {height:.3f} м")
    
    # Тест 3: Расчёт положения лонжеронов
    print("\n3. Расчёт положения лонжеронов:")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        positions = calculate_spar_positions(z_rel, aircraft)
        print(f"   z/L = {z_rel:.1f}: передний = {positions['front']:.3f}c, "
              f"задний = {positions['rear']:.3f}c")
    
    # Тест 4: Расчёт ширины кессона
    print("\n4. Расчёт ширины кессона:")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        width = calculate_box_width(z_rel, aircraft)
        print(f"   z/L = {z_rel:.1f}: b = {width:.3f} м")
    
    # Тест 5: Расчёт площади полок лонжеронов
    print("\n5. Расчёт площади полок лонжеронов:")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        areas = calculate_spar_flange_area(z_rel, aircraft, material)
        print(f"   z/L = {z_rel:.1f}: передний = {areas['front']*1e4:.1f} см², "
              f"задний = {areas['rear']*1e4:.1f} см²")
    
    # Тест 6: Преобразование относительного положения
    print("\n6. Преобразование относительного положения:")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        z_abs = calculate_absolute_position(z_rel, aircraft.wing_span)
        print(f"   z/L = {z_rel:.1f}: z = {z_abs:.3f} м")
    
    # Тест 7: Проверка согласованности с классом Aircraft
    print("\n7. Проверка согласованности с классом Aircraft:")
    z_rel = 0.4
    chord_func = calculate_chord(
        z_rel, aircraft.root_chord, aircraft.tip_chord, aircraft.wing_span
    )
    chord_method = aircraft.get_chord(z_rel)
    print(f"   z/L = {z_rel}:")
    print(f"      Функция: {chord_func:.3f} м")
    print(f"      Метод: {chord_method:.3f} м")
    print(f"      Совпадение: {'✓' if abs(chord_func - chord_method) < 1e-6 else '✗'}")
    
    width_func = calculate_box_width(z_rel, aircraft)
    width_method = aircraft.get_box_width(z_rel)
    print(f"   Ширина кессона:")
    print(f"      Функция: {width_func:.3f} м")
    print(f"      Метод: {width_method:.3f} м")
    print(f"      Совпадение: {'✓' if abs(width_func - width_method) < 1e-6 else '✗'}")
    
    # Тест 8: Валидация
    print("\n8. Тест валидации:")
    try:
        calculate_chord(-0.1, 6.65, 1.25, 34.32)
        print("   ОШИБКА: не сработала валидация для z < 0")
    except ValueError as e:
        print(f"   ✓ Валидация: {e}")
    
    try:
        calculate_chord(1.1, 6.65, 1.25, 34.32)
        print("   ОШИБКА: не сработала валидация для z > 1")
    except ValueError as e:
        print(f"   ✓ Валидация: {e}")
    
    # Тест 9: Расчётные сечения
    print("\n9. Параметры для расчётных сечений:")
    for z_rel in [0.2, 0.4, 0.6, 0.8]:
        z_abs = calculate_absolute_position(z_rel, aircraft.wing_span)
        chord = calculate_chord(z_rel, aircraft.root_chord, aircraft.tip_chord, aircraft.wing_span)
        height = calculate_box_height(z_rel, aircraft)
        width = calculate_box_width(z_rel, aircraft)
        positions = calculate_spar_positions(z_rel, aircraft)
        
        print(f"\n   Сечение z/L = {z_rel} (z = {z_abs:.3f} м):")
        print(f"      Хорда: {chord:.3f} м")
        print(f"      Высота кессона: {height:.3f} м")
        print(f"      Ширина кессона: {width:.3f} м")
        print(f"      Лонжероны: передний = {positions['front']:.3f}c, "
              f"задний = {positions['rear']:.3f}c")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_geometry()

