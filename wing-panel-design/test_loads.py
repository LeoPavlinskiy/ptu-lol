#!/usr/bin/env python3
"""
Простой тест для модуля loads
"""

from loads import (
    load_moments_from_bot,
    load_overloads_from_bot,
    get_moment_at_section,
    load_forces_from_bot
)

def test_loads():
    """Тестирование функций загрузки данных"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ loads")
    print("=" * 60)
    
    # Тест 1: Загрузка изгибающих моментов
    print("\n1. Загрузка изгибающих моментов:")
    try:
        moments = load_moments_from_bot('data/bot-moments.txt')
        print(f"   Загружено моментов: {len(moments)}")
        for z_rel in sorted(moments.keys()):
            data = moments[z_rel]
            print(f"   z/L = {z_rel}: z = {data['z']:.3f} м, M = {data['M']/1e6:.2f} МН·м")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # Тест 2: Загрузка перегрузок
    print("\n2. Загрузка перегрузок:")
    try:
        overloads = load_overloads_from_bot('data/bot-overloads.txt')
        print(f"   Загружено параметров: {len(overloads)}")
        for key, value in overloads.items():
            print(f"   {key} = {value}")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # Тест 3: Получение момента для сечения
    print("\n3. Получение момента для сечения:")
    if 'moments' in locals():
        test_sections = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        for z_rel in test_sections:
            try:
                M = get_moment_at_section(z_rel, moments)
                print(f"   z/L = {z_rel:.1f}: M = {M/1e6:.2f} МН·м")
            except Exception as e:
                print(f"   z/L = {z_rel:.1f}: ОШИБКА - {e}")
    
    # Тест 4: Интерполяция
    print("\n4. Проверка интерполяции:")
    if 'moments' in locals():
        # Проверяем интерполяцию между точками
        z_interp = 0.3  # между 0.2 и 0.4
        M_interp = get_moment_at_section(z_interp, moments)
        M_02 = moments[0.2]['M']
        M_04 = moments[0.4]['M']
        # Линейная интерполяция вручную
        M_manual = M_02 + (M_04 - M_02) * (0.3 - 0.2) / (0.4 - 0.2)
        print(f"   z/L = 0.3 (интерполяция):")
        print(f"      Функция: {M_interp/1e6:.2f} МН·м")
        print(f"      Вручную: {M_manual/1e6:.2f} МН·м")
        print(f"      Разница: {abs(M_interp - M_manual)/1e6:.4f} МН·м")
    
    # Тест 5: Экстраполяция
    print("\n5. Проверка экстраполяции:")
    if 'moments' in locals():
        # Экстраполяция к корню
        z_extrap_down = 0.1
        M_extrap_down = get_moment_at_section(z_extrap_down, moments)
        print(f"   z/L = {z_extrap_down} (экстраполяция к корню): "
              f"M = {M_extrap_down/1e6:.2f} МН·м")
        
        # Экстраполяция к законцовке
        z_extrap_up = 0.9
        M_extrap_up = get_moment_at_section(z_extrap_up, moments)
        print(f"   z/L = {z_extrap_up} (экстраполяция к законцовке): "
              f"M = {M_extrap_up/1e6:.2f} МН·м")
    
    # Тест 6: Загрузка поперечных сил (опционально)
    print("\n6. Загрузка поперечных сил (опционально):")
    try:
        forces = load_forces_from_bot('data/bot-forces.txt')
        if forces:
            print(f"   Загружено значений: {len(forces)}")
            for z_rel in sorted(forces.keys())[:3]:  # Показываем первые 3
                data = forces[z_rel]
                print(f"   z/L = {z_rel}: {data}")
        else:
            print("   Файл не найден или пуст (не критично)")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # Тест 7: Валидация
    print("\n7. Тест валидации:")
    if 'moments' in locals():
        try:
            get_moment_at_section(-0.1, moments)
            print("   ОШИБКА: не сработала валидация для z < 0")
        except ValueError as e:
            print(f"   ✓ Валидация z < 0: {e}")
        
        try:
            get_moment_at_section(1.1, moments)
            print("   ОШИБКА: не сработала валидация для z > 1")
        except ValueError as e:
            print(f"   ✓ Валидация z > 1: {e}")
        
        try:
            get_moment_at_section(0.5, {})
            print("   ОШИБКА: не сработала валидация пустого словаря")
        except ValueError as e:
            print(f"   ✓ Валидация пустого словаря: {e}")
    
    # Тест 8: Расчётные сечения
    print("\n8. Моменты для расчётных сечений:")
    if 'moments' in locals():
        for z_rel in [0.2, 0.4, 0.6, 0.8]:
            M = get_moment_at_section(z_rel, moments)
            print(f"   z/L = {z_rel}: M = {M/1e6:.2f} МН·м = {M:.2e} Н·м")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_loads()

