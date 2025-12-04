#!/usr/bin/env python3
"""
Простой тест для класса Aircraft
"""

from aircraft_data import Aircraft

def test_aircraft():
    """Тестирование основных методов класса Aircraft"""
    
    aircraft = Aircraft()
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КЛАССА Aircraft")
    print("=" * 60)
    
    # Тест 1: Базовые параметры
    print(f"\n1. Базовые параметры:")
    print(f"   Название: {aircraft.name}")
    print(f"   Размах крыла: {aircraft.wing_span} м")
    print(f"   Полуразмах: {aircraft.get_semispan()} м")
    
    # Тест 2: Хорды
    print(f"\n2. Хорды в сечениях:")
    for z_rel in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        chord = aircraft.get_chord(z_rel)
        print(f"   z/L = {z_rel:.1f}: c = {chord:.3f} м")
    
    # Тест 3: Высота кессона
    print(f"\n3. Высота кессона:")
    for z_rel in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
        height = aircraft.get_box_height(z_rel)
        print(f"   z/L = {z_rel:.1f}: h = {height:.3f} м")
    
    # Тест 4: Позиции лонжеронов
    print(f"\n4. Позиции лонжеронов (в долях хорды):")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        positions = aircraft.get_spar_positions(z_rel)
        print(f"   z/L = {z_rel:.1f}: передний = {positions['front']:.3f}, "
              f"задний = {positions['rear']:.3f}")
    
    # Тест 5: Ширина кессона
    print(f"\n5. Ширина кессона:")
    for z_rel in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        width = aircraft.get_box_width(z_rel)
        print(f"   z/L = {z_rel:.1f}: b = {width:.3f} м")
    
    # Тест 6: Валидация
    print(f"\n6. Тест валидации:")
    try:
        aircraft.get_chord(-0.1)
        print("   ОШИБКА: не сработала валидация для z < 0")
    except ValueError as e:
        print(f"   ✓ Валидация работает: {e}")
    
    try:
        aircraft.get_chord(1.1)
        print("   ОШИБКА: не сработала валидация для z > 1")
    except ValueError as e:
        print(f"   ✓ Валидация работает: {e}")
    
    # Тест 7: Расчётные сечения из задачи
    print(f"\n7. Параметры для расчётных сечений:")
    for z_rel in [0.2, 0.4, 0.6, 0.8]:
        z_abs = aircraft.get_absolute_position(z_rel)
        chord = aircraft.get_chord(z_rel)
        height = aircraft.get_box_height(z_rel)
        width = aircraft.get_box_width(z_rel)
        positions = aircraft.get_spar_positions(z_rel)
        
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
    test_aircraft()

