#!/usr/bin/env python3
"""
Простой тест для класса Stringer
"""

from stringer import Stringer

def test_stringer():
    """Тестирование основных методов класса Stringer"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КЛАССА Stringer")
    print("=" * 60)
    
    # Тест 1: Создание стрингеров разных типов
    print("\n1. Создание стрингеров разных типов:")
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        print(f"   {stringer.type}-стрингер:")
        print(f"      Высота стенки: {stringer.web_height*1000:.0f} мм")
        print(f"      Ширина полки: {stringer.flange_width*1000:.0f} мм")
        print(f"      Толщина стенки: {stringer.web_thickness*1000:.1f} мм")
        print(f"      Толщина полки: {stringer.flange_thickness*1000:.1f} мм")
    
    # Тест 2: Расчёт площади
    print("\n2. Расчёт площади поперечного сечения:")
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        area = stringer.calculate_area()
        print(f"   {st_type}-стрингер: {area*1e4:.2f} см²")
    
    # Тест 3: Расчёт момента инерции
    print("\n3. Расчёт момента инерции:")
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        stringer.calculate_area()
        inertia = stringer.calculate_inertia()
        print(f"   {st_type}-стрингер: {inertia*1e8:.2f} см⁴")
        if stringer.centroid_y:
            print(f"      Центр тяжести: {stringer.centroid_y*1000:.2f} мм от нижнего края")
    
    # Тест 4: Расчёт эффективной площади
    print("\n4. Расчёт эффективной площади с обшивкой:")
    skin_thickness = 0.003  # 3 мм
    effective_width = 0.15  # 15 см
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        stringer.calculate_area()
        eff_area = stringer.calculate_effective_area(skin_thickness, effective_width)
        print(f"   {st_type}-стрингер:")
        print(f"      Площадь стрингера: {stringer.area*1e4:.2f} см²")
        print(f"      Эффективная площадь: {eff_area*1e4:.2f} см²")
        print(f"      Площадь обшивки: {(eff_area - stringer.area)*1e4:.2f} см²")
    
    # Тест 5: Валидация
    print("\n5. Тест валидации:")
    try:
        Stringer('INVALID')
        print("   ОШИБКА: не сработала валидация типа стрингера")
    except ValueError as e:
        print(f"   ✓ Валидация типа стрингера: {e}")
    
    # Тест 6: Проверка расчёта без установки геометрии
    print("\n6. Проверка расчёта без установки геометрии:")
    stringer = Stringer('Z')
    try:
        stringer.calculate_area()
        print("   ОШИБКА: расчёт прошёл без установки геометрии")
    except ValueError as e:
        print(f"   ✓ Валидация геометрии: {e}")
    
    # Тест 7: Сравнение типов стрингеров
    print("\n7. Сравнение характеристик разных типов стрингеров:")
    print("   Тип | Площадь (см²) | Момент инерции (см⁴)")
    print("   " + "-" * 45)
    for st_type in ['Z', 'C', 'T', 'L']:
        stringer = Stringer(st_type)
        stringer.set_geometry_from_typical()
        area = stringer.calculate_area()
        inertia = stringer.calculate_inertia()
        print(f"   {st_type:4s} | {area*1e4:11.2f} | {inertia*1e8:20.2f}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_stringer()

