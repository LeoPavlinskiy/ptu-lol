#!/usr/bin/env python3
"""
Простой тест для класса Material
"""

from material import Material

def test_material():
    """Тестирование основных методов класса Material"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КЛАССА Material")
    print("=" * 60)
    
    # Тест 1: Создание материала (лист)
    print("\n1. Создание материала (лист В95-Т1):")
    material_sheet = Material('B95T1', 'sheet')
    print(f"   {material_sheet}")
    print(f"   Предел прочности: {material_sheet.ultimate_strength/1e6:.0f} МПа")
    print(f"   Предел текучести: {material_sheet.yield_strength/1e6:.0f} МПа")
    print(f"   Предел пропорциональности: {material_sheet.proportional_limit/1e6:.0f} МПа")
    print(f"   Модуль упругости: {material_sheet.young_modulus/1e9:.0f} ГПа")
    print(f"   Модуль сдвига: {material_sheet.shear_modulus/1e9:.0f} ГПа")
    print(f"   Коэффициент Пуассона: {material_sheet.poisson_ratio}")
    print(f"   Плотность: {material_sheet.density} кг/м³")
    
    # Тест 2: Создание материала (профиль)
    print("\n2. Создание материала (профиль В95-Т1):")
    material_profile = Material('B95T1', 'profile')
    print(f"   {material_profile}")
    print(f"   Предел прочности: {material_profile.ultimate_strength/1e6:.0f} МПа")
    print(f"   Предел текучести: {material_profile.yield_strength/1e6:.0f} МПа")
    print(f"   Предел пропорциональности: {material_profile.proportional_limit/1e6:.0f} МПа")
    
    # Тест 3: Допускаемые напряжения
    print("\n3. Допускаемые напряжения:")
    for load_type in ['tension', 'compression', 'shear']:
        allowable = material_sheet.get_allowable_stress(load_type)
        print(f"   {load_type}: {allowable/1e6:.0f} МПа")
    
    # Тест 4: Проверка прочности
    print("\n4. Проверка прочности:")
    test_stresses = [
        (200e6, 'compression', 'Безопасное напряжение'),
        (300e6, 'compression', 'На границе допускаемого'),
        (350e6, 'compression', 'Превышение допускаемого'),
        (250e6, 'tension', 'Растяжение'),
        (150e6, 'shear', 'Сдвиг'),
    ]
    
    for stress, load_type, description in test_stresses:
        result = material_sheet.check_strength(stress, load_type)
        status = "✓ Безопасно" if result['safe'] else "✗ Превышение"
        print(f"   {description}:")
        print(f"      Напряжение: {stress/1e6:.0f} МПа")
        print(f"      Допускаемое: {result['allowable']/1e6:.0f} МПа")
        print(f"      Запас прочности: {result['safety_margin']:.2f}")
        print(f"      {status}")
    
    # Тест 5: Редуцированный модуль
    print("\n5. Редуцированный модуль упругости:")
    test_stresses_mod = [100e6, 300e6, 400e6, 500e6]
    for stress in test_stresses_mod:
        E_red = material_sheet.get_reduced_modulus(stress)
        E_ratio = E_red / material_sheet.young_modulus
        print(f"   σ = {stress/1e6:.0f} МПа: E_red = {E_red/1e9:.1f} ГПа "
              f"({E_ratio:.2%} от E)")
    
    # Тест 6: Валидация
    print("\n6. Тест валидации:")
    try:
        Material('INVALID', 'sheet')
        print("   ОШИБКА: не сработала валидация типа материала")
    except ValueError as e:
        print(f"   ✓ Валидация типа материала: {e}")
    
    try:
        Material('B95T1', 'invalid')
        print("   ОШИБКА: не сработала валидация типа продукции")
    except ValueError as e:
        print(f"   ✓ Валидация типа продукции: {e}")
    
    try:
        material_sheet.get_allowable_stress('invalid')
        print("   ОШИБКА: не сработала валидация типа нагрузки")
    except ValueError as e:
        print(f"   ✓ Валидация типа нагрузки: {e}")
    
    # Тест 7: Коэффициенты запаса
    print("\n7. Коэффициенты запаса прочности:")
    print(f"   По разрушению: {material_sheet.safety_factor_ultimate}")
    print(f"   По текучести: {material_sheet.safety_factor_yield}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_material()

