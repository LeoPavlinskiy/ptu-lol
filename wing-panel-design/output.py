"""
Вывод результатов расчёта.
Функции для форматированного вывода результатов в консоль и файл.
"""


def print_results(results):
    """
    Вывод результатов в консоль.
    
    Args:
        results: Словарь с результатами расчёта:
            {z_relative: {
                'panel': Panel,
                'stringers': list,
                'moment': float,
                'stresses': dict,
                'strength': dict,
                'iterations': int,
                'convergence': dict
            }}
            
    Raises:
        KeyError: Если в данных отсутствуют обязательные поля
        AttributeError: Если у объектов отсутствуют необходимые атрибуты
    """
    if not results:
        print("Нет результатов для вывода")
        return
    
    for z_rel in sorted(results.keys()):
        try:
            data = results[z_rel]
            panel = data.get('panel')
            stresses = data.get('stresses', {})
            strength = data.get('strength', {})
            moment = data.get('moment', 0)
            
            if panel is None:
                print(f"\n{'='*60}")
                print(f"Сечение z/L = {z_rel}")
                print(f"{'='*60}")
                print("Ошибка: данные панели отсутствуют")
                continue
            
            print(f"\n{'='*60}")
            print(f"Сечение z/L = {z_rel}")
            print(f"{'='*60}")
            print(f"Изгибающий момент: {moment/1e6:.2f} МН·м")
            print(f"\nГеометрия панели:")
            print(f"  Ширина панели: {panel.panel_width*1000:.1f} мм")
            print(f"  Высота кессона: {panel.box_height*1000:.1f} мм")
            print(f"  Толщина обшивки: {panel.skin_thickness*1000:.2f} мм")
            print(f"  Количество стрингеров: {panel.stringer_count}")
            print(f"  Шаг стрингеров: {panel.stringer_spacing*1000:.1f} мм")
            
            if panel.effective_skin_width is not None:
                print(f"  Эффективная ширина обшивки: {panel.effective_skin_width*1000:.1f} мм")
            
            print(f"\nНапряжения:")
            if 'max' in stresses:
                print(f"  Максимальное: {stresses['max']/1e6:.2f} МПа")
            if 'skin' in stresses:
                print(f"  В обшивке: {stresses['skin']/1e6:.2f} МПа")
            if 'stringers' in stresses:
                print(f"  В стрингерах: {stresses['stringers']/1e6:.2f} МПа")
            
            print(f"\nПрочность:")
            if 'skin_check' in strength:
                skin_check = strength['skin_check']
                print(f"  Обшивка:")
                print(f"    Напряжение: {skin_check.get('stress', 0)/1e6:.2f} МПа")
                print(f"    Допускаемое: {skin_check.get('allowable', 0)/1e6:.2f} МПа")
                print(f"    Предел пропорциональности: {skin_check.get('proportional_limit', 0)/1e6:.2f} МПа")
                print(f"    Запас прочности (допускаемое): {skin_check.get('safety_margin_allowable', 0):.2f}")
                print(f"    Запас прочности (пропорциональность): {skin_check.get('safety_margin_proportional', 0):.2f}")
                print(f"    Статус: {'✓ БЕЗОПАСНО' if skin_check.get('safe', False) else '✗ НЕ БЕЗОПАСНО'}")
            
            print(f"\n  Общая оценка:")
            print(f"    Статус: {'✓ БЕЗОПАСНО' if strength.get('overall_safe', False) else '✗ НЕ БЕЗОПАСНО'}")
            
            if panel.reduced_area is not None:
                print(f"\nЭффективные параметры:")
                print(f"  Эффективная площадь: {panel.reduced_area*1e4:.2f} см²")
                print(f"  Эффективный момент инерции: {panel.reduced_inertia*1e8:.2f} см⁴")
            
            iterations = data.get('iterations', 0)
            print(f"\nИтерации: {iterations}")
            conv = data.get('convergence', {})
            if conv.get('converged', False):
                print(f"  Сходимость: ✓")
                if 'final_b_eff' in conv and panel.stringer_spacing is not None and panel.stringer_spacing > 0:
                    print(f"  Коэффициент редуцирования: {conv['final_b_eff']/panel.stringer_spacing:.3f}")
        except Exception as e:
            print(f"\nОшибка при выводе результатов для сечения z/L = {z_rel}: {e}")
            import traceback
            traceback.print_exc()
            continue


def output_results(results, output_file='data/results.md'):
    """
    Вывод результатов в markdown файл.
    
    Args:
        results: Словарь с результатами расчёта
        output_file: Путь к выходному файлу (по умолчанию 'data/results.md')
        
    Raises:
        IOError: Если не удаётся создать или записать файл
        KeyError: Если в данных отсутствуют обязательные поля
    """
    if not results:
        raise ValueError("Нет результатов для вывода")
    
    # Создаём директорию, если её нет
    import os
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Результаты расчёта верхней панели крыла\n\n")
        f.write("**Самолёт:** Boeing 737-800\n\n")
        f.write("**Материал:** В95-Т1 (лист)\n\n")
        f.write("---\n\n")
        
        for z_rel in sorted(results.keys()):
            try:
                data = results[z_rel]
                panel = data.get('panel')
                stresses = data.get('stresses', {})
                strength = data.get('strength', {})
                moment = data.get('moment', 0)
                
                if panel is None:
                    f.write(f"## Сечение z/L = {z_rel}\n\n")
                    f.write("**Ошибка:** данные панели отсутствуют\n\n")
                    f.write("---\n\n")
                    continue
                
                f.write(f"## Сечение z/L = {z_rel}\n\n")
                
                f.write(f"### Нагрузки\n\n")
                f.write(f"- Изгибающий момент: {moment/1e6:.2f} МН·м\n\n")
                
                f.write(f"### Геометрия панели\n\n")
                f.write(f"- Ширина панели: {panel.panel_width*1000:.1f} мм\n")
                f.write(f"- Высота кессона: {panel.box_height*1000:.1f} мм\n")
                f.write(f"- Толщина обшивки: {panel.skin_thickness*1000:.2f} мм\n")
                f.write(f"- Количество стрингеров: {panel.stringer_count}\n")
                f.write(f"- Шаг стрингеров: {panel.stringer_spacing*1000:.1f} мм\n")
                
                if panel.effective_skin_width is not None:
                    f.write(f"- Эффективная ширина обшивки: {panel.effective_skin_width*1000:.1f} мм\n")
                
                f.write(f"\n### Напряжения\n\n")
                if 'max' in stresses:
                    f.write(f"- Максимальное: {stresses['max']/1e6:.2f} МПа\n")
                if 'skin' in stresses:
                    f.write(f"- В обшивке: {stresses['skin']/1e6:.2f} МПа\n")
                if 'stringers' in stresses:
                    f.write(f"- В стрингерах: {stresses['stringers']/1e6:.2f} МПа\n")
                
                f.write(f"\n### Проверка прочности\n\n")
                if 'skin_check' in strength:
                    skin_check = strength['skin_check']
                    f.write(f"**Обшивка:**\n")
                    f.write(f"- Напряжение: {skin_check.get('stress', 0)/1e6:.2f} МПа\n")
                    f.write(f"- Допускаемое: {skin_check.get('allowable', 0)/1e6:.2f} МПа\n")
                    f.write(f"- Предел пропорциональности: {skin_check.get('proportional_limit', 0)/1e6:.2f} МПа\n")
                    f.write(f"- Запас прочности (допускаемое): {skin_check.get('safety_margin_allowable', 0):.2f}\n")
                    f.write(f"- Запас прочности (пропорциональность): {skin_check.get('safety_margin_proportional', 0):.2f}\n")
                    f.write(f"- Статус: {'✓ БЕЗОПАСНО' if skin_check.get('safe', False) else '✗ НЕ БЕЗОПАСНО'}\n\n")
                
                f.write(f"**Общая оценка:**\n")
                f.write(f"- Статус: {'✓ БЕЗОПАСНО' if strength.get('overall_safe', False) else '✗ НЕ БЕЗОПАСНО'}\n\n")
                
                if panel.reduced_area is not None:
                    f.write(f"### Эффективные параметры\n\n")
                    f.write(f"- Эффективная площадь: {panel.reduced_area*1e4:.2f} см²\n")
                    f.write(f"- Эффективный момент инерции: {panel.reduced_inertia*1e8:.2f} см⁴\n\n")
                
                f.write(f"### Итерационный расчёт\n\n")
                iterations = data.get('iterations', 0)
                f.write(f"- Количество итераций: {iterations}\n")
                conv = data.get('convergence', {})
                if conv.get('converged', False):
                    f.write(f"- Сходимость: ✓\n")
                    if 'final_b_eff' in conv and panel.stringer_spacing is not None and panel.stringer_spacing > 0:
                        f.write(f"- Коэффициент редуцирования: {conv['final_b_eff']/panel.stringer_spacing:.3f}\n")
                else:
                    f.write(f"- Сходимость: ✗\n")
                
                f.write(f"\n---\n\n")
            except Exception as e:
                f.write(f"## Сечение z/L = {z_rel}\n\n")
                f.write(f"**Ошибка при обработке данных:** {e}\n\n")
                f.write("---\n\n")
                continue
        
        f.write(f"## Примечания\n\n")
        f.write(f"- Расчёт выполнен с учётом редуцирования обшивки (метод Винтера)\n")
        f.write(f"- Проверка прочности выполнена по допускаемым напряжениям и пределу пропорциональности\n")
        f.write(f"- Коэффициент запаса прочности: 1.5\n")
