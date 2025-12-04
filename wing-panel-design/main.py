"""
Главный файл запуска расчёта верхней панели крыла.
Интегрирует все модули для полного расчёта панели в нескольких сечениях.
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from geometry import calculate_box_width, calculate_box_height
from loads import load_moments_from_bot, load_overloads_from_bot, get_moment_at_section
from stability import local_skin_buckling
from reduction import iterative_reduction
from strength import calculate_stresses, check_strength, check_panel_strength
from output import print_results, output_results


def preliminary_panel_design(panel, moment, material, target_stress=200e6):
    """
    Предварительный подбор параметров панели.
    
    Подбирает начальные значения:
    - Толщина обшивки
    - Количество стрингеров
    - Шаг стрингеров
    - Параметры стрингеров
    
    Args:
        panel: Объект класса Panel с рассчитанной геометрией
        moment: Изгибающий момент в Н·м
        material: Объект класса Material
        target_stress: Целевое напряжение для подбора (по умолчанию 200 МПа)
        
    Returns:
        tuple: (panel, stringers) где:
            - panel: Обновлённый объект Panel с подобранными параметрами
            - stringers: Список объектов Stringer
    """
    # Расчёт геометрии, если ещё не рассчитано
    if panel.panel_width is None:
        panel.calculate_panel_width()
    
    if panel.box_height is None:
        panel.calculate_box_height()
    
    # Начальная толщина обшивки (2-4 мм в зависимости от момента)
    # Чем больше момент, тем толще обшивка
    if moment > 5e6:
        initial_thickness = 0.004  # 4 мм для больших моментов
    elif moment > 3e6:
        initial_thickness = 0.003  # 3 мм для средних моментов
    else:
        initial_thickness = 0.0025  # 2.5 мм для малых моментов
    
    panel.skin_thickness = initial_thickness
    
    # Количество стрингеров (2-4 в зависимости от ширины панели)
    if panel.panel_width > 2.0:
        stringer_count = 4
    elif panel.panel_width > 1.5:
        stringer_count = 3
    else:
        stringer_count = 2
    
    panel.stringer_count = stringer_count
    panel.stringer_spacing = panel.panel_width / (stringer_count + 1)
    
    # Создание стрингеров (тип Z, типичные размеры)
    stringers = []
    for i in range(stringer_count):
        stringer = Stringer('Z')
        stringer.set_geometry_from_typical()
        stringer.calculate_area()
        stringer.calculate_inertia()
        stringers.append(stringer)
        panel.add_stringer(stringer)
    
    return panel, stringers


def main():
    """
    Главная функция расчёта верхней панели крыла.
    
    Выполняет расчёт для нескольких сечений по размаху крыла:
    - z/L = 0.2, 0.4, 0.6, 0.8
    
    Для каждого сечения:
    1. Создаёт панель и рассчитывает геометрию
    2. Загружает изгибающий момент
    3. Подбирает параметры панели
    4. Выполняет итерационный расчёт с редуцированием
    5. Рассчитывает напряжения
    6. Проверяет прочность
    """
    print("=" * 70)
    print("Расчёт верхней панели крыла Boeing 737-800")
    print("=" * 70)
    
    try:
        # Инициализация
        print("\n1. Инициализация...")
        aircraft = Aircraft()
        material = Material('B95T1', 'sheet')
        print(f"   Материал: {material.material_type} ({material.product_type})")
        print(f"   Предел прочности: {material.ultimate_strength/1e6:.1f} МПа")
        print(f"   Предел текучести: {material.yield_strength/1e6:.1f} МПа")
        
        # Расчётные сечения
        sections = [0.2, 0.4, 0.6, 0.8]
        print(f"   Расчётные сечения: {sections}")
        
        # Загрузка данных от бота
        print("\n2. Загрузка данных о нагрузках...")
        moments = load_moments_from_bot()
        overloads = load_overloads_from_bot()
        print(f"   Загружено моментов: {len(moments)}")
        print(f"   Перегрузка: ny_max = {overloads['ny_max']:.2f}")
        print(f"   Коэффициент запаса: {overloads['safety_factor']:.2f}")
        
        results = {}
        
        # Расчёт для каждого сечения
        print("\n3. Расчёт для каждого сечения:")
        print("=" * 70)
        
        for z_rel in sections:
            print(f"\n=== Сечение z/L = {z_rel} ===")
            
            try:
                # Создание панели
                panel = Panel(z_rel, aircraft, material)
                
                # Расчёт геометрии
                panel.calculate_panel_width()
                panel.calculate_box_height()
                print(f"   Ширина панели: {panel.panel_width*1000:.1f} мм")
                print(f"   Высота кессона: {panel.box_height*1000:.1f} мм")
                
                # Получение изгибающего момента
                M = get_moment_at_section(z_rel, moments)
                print(f"   Изгибающий момент: {M/1e6:.2f} МН·м")
                
                # Предварительный подбор параметров панели
                print(f"   Подбор параметров панели...")
                panel, stringers = preliminary_panel_design(panel, M, material)
                print(f"   Толщина обшивки: {panel.skin_thickness*1000:.2f} мм")
                print(f"   Количество стрингеров: {panel.stringer_count}")
                print(f"   Шаг стрингеров: {panel.stringer_spacing*1000:.1f} мм")
                
                # Длина панели (принимаем равной шагу нервюр, ~0.5 м)
                panel_length = 0.5
                
                # Итерационный расчёт с редуцированием
                print(f"   Итерационный расчёт с редуцированием...")
                panel_result, stringers_result, iteration, conv_info = iterative_reduction(
                    panel, stringers, material, M, panel_length,
                    max_iterations=10, tolerance=0.02, method='winter'
                )
                
                print(f"   Итераций выполнено: {iteration}")
                print(f"   Сходимость: {'✓' if conv_info['converged'] else '✗'}")
                if conv_info['converged']:
                    print(f"   Эффективная ширина: {conv_info['final_b_eff']*1000:.1f} мм")
                    print(f"   Коэффициент редуцирования: {conv_info['final_b_eff']/panel.stringer_spacing:.3f}")
                
                # Расчёт напряжений
                print(f"   Расчёт напряжений...")
                stresses = calculate_stresses(panel_result, stringers_result, M, material)
                print(f"   Максимальное напряжение: {stresses['max']/1e6:.2f} МПа")
                print(f"   Напряжение в обшивке: {stresses['skin']/1e6:.2f} МПа")
                
                # Проверка прочности
                print(f"   Проверка прочности...")
                strength_check = check_panel_strength(panel_result, stringers_result, M, material)
                
                is_safe = strength_check['overall_safe']
                print(f"   Прочность: {'✓ БЕЗОПАСНО' if is_safe else '✗ НЕ БЕЗОПАСНО'}")
                
                if strength_check['skin_check']['safe']:
                    print(f"   Обшивка: запас прочности {strength_check['skin_check']['safety_margin_allowable']:.2f}")
                else:
                    print(f"   Обшивка: ПРЕВЫШЕНИЕ ДОПУСКАЕМОГО НАПРЯЖЕНИЯ!")
                
                # Сохранение результатов
                results[z_rel] = {
                    'panel': panel_result,
                    'stringers': stringers_result,
                    'moment': M,
                    'stresses': stresses,
                    'strength': strength_check,
                    'iterations': iteration,
                    'convergence': conv_info
                }
                
            except Exception as e:
                print(f"   ОШИБКА при расчёте сечения z/L = {z_rel}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Вывод результатов
        print("\n" + "=" * 70)
        print("4. Вывод результатов:")
        print("=" * 70)
        
        print_results(results)
        
        # Сохранение в файл
        output_file = 'data/results.md'
        output_results(results, output_file)
        print(f"\nРезультаты сохранены в файл: {output_file}")
        
        print("\n" + "=" * 70)
        print("Расчёт завершён успешно!")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\nОШИБКА: Файл не найден: {e}")
        print("Проверьте наличие файлов данных в директории data/")
        return 1
    
    except ValueError as e:
        print(f"\nОШИБКА: Неверные данные: {e}")
        return 1
    
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
