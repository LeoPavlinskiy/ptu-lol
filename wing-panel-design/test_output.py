"""
Тест модуля вывода результатов output.py
Проверяет корректность работы функций вывода.
"""

import os
import sys
from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from loads import load_moments_from_bot, get_moment_at_section
from strength import check_panel_strength, calculate_stresses
from output import print_results, output_results


def test_output_functions():
    """Тест функций вывода результатов"""
    print("Тест функций вывода результатов:")
    
    # Создаём тестовые данные
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    panel = Panel(0.4, aircraft, material)
    panel.calculate_panel_width()
    panel.calculate_box_height()
    panel.skin_thickness = 0.003
    panel.stringer_spacing = 0.15
    panel.stringer_count = 2
    
    # Создаём стрингеры
    stringers = []
    for i in range(2):
        s = Stringer('Z')
        s.set_geometry_from_typical()
        s.calculate_area()
        s.calculate_inertia()
        stringers.append(s)
        panel.add_stringer(s)
    
    # Устанавливаем эффективные параметры
    panel.effective_skin_width = 0.12
    panel.reduced_area = 0.001
    panel.reduced_inertia = 1e-6
    
    # Загружаем момент
    moments = load_moments_from_bot()
    M = get_moment_at_section(0.4, moments)
    
    # Рассчитываем напряжения
    stresses = calculate_stresses(panel, stringers, M, material)
    
    # Проверяем прочность
    strength = check_panel_strength(panel, stringers, M, material)
    
    # Формируем результаты
    results = {
        0.4: {
            'panel': panel,
            'stringers': stringers,
            'moment': M,
            'stresses': stresses,
            'strength': strength,
            'iterations': 5,
            'convergence': {
                'converged': True,
                'final_b_eff': 0.12,
                'final_sigma_edge': 200e6,
                'final_sigma_cr': 150e6
            }
        }
    }
    
    # Тест 1: Вывод в консоль
    print("\n1. Тест print_results():")
    try:
        print_results(results)
        print("   ✓ print_results() работает корректно")
    except Exception as e:
        print(f"   ✗ Ошибка в print_results(): {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Тест 2: Вывод в файл
    print("\n2. Тест output_results():")
    test_output_file = 'data/test_results.md'
    try:
        output_results(results, test_output_file)
        
        # Проверяем, что файл создан
        if os.path.exists(test_output_file):
            print(f"   ✓ Файл создан: {test_output_file}")
            
            # Проверяем содержимое
            with open(test_output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Результаты расчёта верхней панели крыла' in content:
                    print("   ✓ Заголовок присутствует")
                if 'Сечение z/L = 0.4' in content:
                    print("   ✓ Данные о сечении присутствуют")
                if 'Изгибающий момент' in content:
                    print("   ✓ Данные о нагрузках присутствуют")
                if 'Геометрия панели' in content:
                    print("   ✓ Данные о геометрии присутствуют")
                if 'Напряжения' in content:
                    print("   ✓ Данные о напряжениях присутствуют")
                if 'Проверка прочности' in content:
                    print("   ✓ Данные о прочности присутствуют")
            
            # Удаляем тестовый файл
            os.remove(test_output_file)
            print("   ✓ Тестовый файл удалён")
        else:
            print(f"   ✗ Файл не создан: {test_output_file}")
            raise FileNotFoundError(f"Файл не создан: {test_output_file}")
            
    except Exception as e:
        print(f"   ✗ Ошибка в output_results(): {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("\n   ✓ Все тесты функций вывода пройдены успешно")


if __name__ == '__main__':
    print("=" * 60)
    print("Тестирование output.py")
    print("=" * 60)
    
    try:
        test_output_functions()
        
        print("\n" + "=" * 60)
        print("Все тесты пройдены успешно!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

