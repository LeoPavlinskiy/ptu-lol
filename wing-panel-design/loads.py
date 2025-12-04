"""
Расчёт нагрузок и изгибающих моментов.
Функции для загрузки данных от бота и работы с нагрузками.
"""

import os


def load_moments_from_bot(filepath='data/bot-moments.txt'):
    """
    Загрузка изгибающих моментов из файла.
    
    Формат файла:
    # Изгибающие моменты из бота Чедрика (Н·м)
    # Сечение z/L | z (м) | M (Н·м)
    0.2 | 3.432 | 7.63e6
    0.4 | 6.864 | 4.66e6
    ...
    
    Args:
        filepath: Путь к файлу с данными изгибающих моментов
        
    Returns:
        dict: Словарь с изгибающими моментами:
            {z_relative: {'z': z_absolute, 'M': moment}}
            где z_relative - относительное положение (0.2, 0.4, ...)
            z_absolute - абсолютное расстояние от корня в метрах
            moment - изгибающий момент в Н·м
            
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если формат данных некорректен
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    
    moments = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Пропускаем комментарии и пустые строки
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            try:
                # Разделяем строку по разделителю |
                parts = line.split('|')
                if len(parts) != 3:
                    raise ValueError(
                        f"Неверный формат строки {line_num}: ожидается 3 значения, "
                        f"разделённых символом '|'"
                    )
                
                z_rel = float(parts[0].strip())
                z_abs = float(parts[1].strip())
                M = float(parts[2].strip())
                
                moments[z_rel] = {'z': z_abs, 'M': M}
                
            except ValueError as e:
                raise ValueError(
                    f"Ошибка парсинга строки {line_num} в файле {filepath}: {e}"
                )
    
    if not moments:
        raise ValueError(f"Файл {filepath} не содержит данных о моментах")
    
    return moments


def load_overloads_from_bot(filepath='data/bot-overloads.txt'):
    """
    Загрузка перегрузок из файла.
    
    Формат файла:
    # Расчётные перегрузки
    ny_max = 3.75
    ny_min = -1.5
    safety_factor = 1.5
    
    Args:
        filepath: Путь к файлу с данными перегрузок
        
    Returns:
        dict: Словарь с перегрузками:
            {'ny_max': float, 'ny_min': float, 'safety_factor': float}
            
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если формат данных некорректен
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    
    overloads = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Пропускаем комментарии и пустые строки
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            if '=' in line:
                try:
                    key, value = line.split('=', 1)  # Разделяем только по первому '='
                    key = key.strip()
                    value = float(value.strip())
                    overloads[key] = value
                except ValueError as e:
                    raise ValueError(
                        f"Ошибка парсинга строки {line_num} в файле {filepath}: {e}"
                    )
    
    if not overloads:
        raise ValueError(f"Файл {filepath} не содержит данных о перегрузках")
    
    return overloads


def get_moment_at_section(z_relative, moments_dict):
    """
    Получение изгибающего момента для заданного сечения.
    
    Если значение для точного z_relative есть в словаре, возвращает его.
    Иначе выполняет линейную интерполяцию между ближайшими значениями.
    
    Args:
        z_relative: Относительное положение сечения (0.0 - 1.0)
        moments_dict: Словарь с моментами из load_moments_from_bot()
        
    Returns:
        float: Изгибающий момент в Н·м
        
    Raises:
        ValueError: Если z_relative вне диапазона данных или словарь пуст
    """
    if not moments_dict:
        raise ValueError("Словарь моментов пуст")
    
    if not 0 <= z_relative <= 1:
        raise ValueError(
            f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}"
        )
    
    # Если значение есть в словаре, возвращаем его
    if z_relative in moments_dict:
        return moments_dict[z_relative]['M']
    
    # Иначе выполняем интерполяцию
    sorted_keys = sorted(moments_dict.keys())
    
    # Проверка границ
    if z_relative < sorted_keys[0]:
        # Экстраполяция вниз (к корню)
        # Используем первые два значения для линейной экстраполяции
        if len(sorted_keys) < 2:
            return moments_dict[sorted_keys[0]]['M']
        
        z1, z2 = sorted_keys[0], sorted_keys[1]
        M1 = moments_dict[z1]['M']
        M2 = moments_dict[z2]['M']
        
        # Линейная экстраполяция
        slope = (M2 - M1) / (z2 - z1)
        M = M1 + slope * (z_relative - z1)
        return M
    
    if z_relative > sorted_keys[-1]:
        # Экстраполяция вверх (к законцовке)
        # Используем последние два значения
        if len(sorted_keys) < 2:
            return moments_dict[sorted_keys[-1]]['M']
        
        z1, z2 = sorted_keys[-2], sorted_keys[-1]
        M1 = moments_dict[z1]['M']
        M2 = moments_dict[z2]['M']
        
        # Линейная экстраполяция
        slope = (M2 - M1) / (z2 - z1)
        M = M2 + slope * (z_relative - z2)
        return M
    
    # Интерполяция между двумя точками
    # Находим две ближайшие точки
    for i in range(len(sorted_keys) - 1):
        z1 = sorted_keys[i]
        z2 = sorted_keys[i + 1]
        
        if z1 <= z_relative <= z2:
            M1 = moments_dict[z1]['M']
            M2 = moments_dict[z2]['M']
            
            # Линейная интерполяция
            t = (z_relative - z1) / (z2 - z1)
            M = M1 + (M2 - M1) * t
            return M
    
    # Если не попали ни в один интервал (не должно произойти)
    return moments_dict[sorted_keys[-1]]['M']


def load_forces_from_bot(filepath='data/bot-forces.txt'):
    """
    Загрузка поперечных сил из файла (опционально).
    
    Формат файла:
    # Поперечные силы из бота Чедрика (Н)
    # Сечение z/L | z (м) | Q_CaseA (Н) | Q_CaseD (Н)
    0.2 | 3.432 | 1.045e6 | -4.21e5
    ...
    
    Args:
        filepath: Путь к файлу с данными поперечных сил
        
    Returns:
        dict: Словарь с поперечными силами:
            {z_relative: {'z': z_absolute, 'Q_CaseA': float, 'Q_CaseD': float}}
            
    Raises:
        FileNotFoundError: Если файл не найден (не критично, файл опциональный)
    """
    if not os.path.exists(filepath):
        # Файл опциональный, возвращаем пустой словарь
        return {}
    
    forces = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            try:
                parts = line.split('|')
                if len(parts) >= 3:
                    z_rel = float(parts[0].strip())
                    z_abs = float(parts[1].strip())
                    
                    force_data = {'z': z_abs}
                    
                    # Может быть несколько значений поперечных сил (Case A, Case D)
                    for i in range(2, len(parts)):
                        part = parts[i].strip()
                        if '=' in part:
                            # Формат: "Q_CaseA = 1.045e6"
                            key, value = part.split('=', 1)
                            force_data[key.strip()] = float(value.strip())
                        else:
                            # Просто значение
                            force_data[f'Q_{i-1}'] = float(part)
                    
                    forces[z_rel] = force_data
                    
            except (ValueError, IndexError) as e:
                # Пропускаем некорректные строки
                continue
    
    return forces


def calculate_bending_stress(M, I_eff, y_max, area_eff=None):
    """
    Расчёт нормальных напряжений от изгибающего момента.
    
    Формула:
    σ = M * y / I
    
    где:
    - M - изгибающий момент (Н·м)
    - I_eff - эффективный момент инерции сечения (м⁴)
    - y_max - расстояние от нейтральной оси до крайнего волокна (м)
    - area_eff - эффективная площадь (опционально, для проверки)
    
    Args:
        M: Изгибающий момент в Н·м
        I_eff: Эффективный момент инерции сечения в м⁴
        y_max: Расстояние от нейтральной оси до крайнего волокна в метрах
        area_eff: Эффективная площадь сечения в м² (опционально, для валидации)
        
    Returns:
        float: Нормальное напряжение в Па
        
    Raises:
        ValueError: Если параметры некорректны (I_eff = 0, y_max = 0)
    """
    if I_eff <= 0:
        raise ValueError(f"Момент инерции должен быть положительным, получено {I_eff}")
    
    if y_max == 0:
        raise ValueError("Расстояние до крайнего волокна не может быть нулевым")
    
    # Расчёт напряжения по формуле изгиба
    stress = M * y_max / I_eff
    
    return stress


def calculate_neutral_axis(panel, stringers):
    """
    Определение положения нейтральной оси составного сечения.
    
    Нейтральная ось проходит через центр тяжести сечения.
    Координата центра тяжести рассчитывается по формуле:
    
    y_c = Σ(S_y) / Σ(A)
    
    где:
    - S_y = A * y - статический момент элемента относительно базовой оси
    - A - площадь элемента
    - y - координата центра тяжести элемента
    
    Args:
        panel: Объект класса Panel с параметрами панели
        stringers: Список объектов Stringer
        
    Returns:
        float: Координата нейтральной оси в метрах (от нижнего края кессона)
        
    Raises:
        ValueError: Если параметры панели не установлены
    """
    if panel.box_height is None:
        raise ValueError("Высота кессона не установлена")
    
    if panel.skin_thickness is None:
        raise ValueError("Толщина обшивки не установлена")
    
    if panel.effective_skin_width is None:
        # Если эффективная ширина не рассчитана, используем шаг стрингеров
        if panel.stringer_spacing is None:
            raise ValueError("Шаг стрингеров или эффективная ширина не установлены")
        effective_width = panel.stringer_spacing
    else:
        effective_width = panel.effective_skin_width
    
    # Базовая ось - нижний край кессона
    # Суммируем статические моменты всех элементов
    
    total_area = 0.0
    total_static_moment = 0.0
    
    # Обшивка (верхняя панель)
    skin_area = panel.skin_thickness * effective_width
    # Центр тяжести обшивки - на расстоянии t/2 от верхнего края кессона
    skin_y = panel.box_height - panel.skin_thickness / 2
    total_area += skin_area
    total_static_moment += skin_area * skin_y
    
    # Стрингеры
    for stringer in stringers:
        if stringer.area is None:
            continue
        
        # Координата центра тяжести стрингера
        # Стрингер крепится к верхней обшивке
        if hasattr(stringer, 'centroid_y') and stringer.centroid_y is not None:
            # Используем рассчитанный центр тяжести стрингера
            # Относительно нижнего края стрингера
            stringer_bottom = panel.box_height - panel.skin_thickness
            stringer_y = stringer_bottom - stringer.centroid_y
        else:
            # Упрощённо: центр тяжести стрингера на середине его высоты
            # от верхней обшивки
            if hasattr(stringer, 'web_height') and stringer.web_height:
                stringer_y = panel.box_height - panel.skin_thickness - stringer.web_height / 2
            else:
                # Типовое значение
                stringer_y = panel.box_height - panel.skin_thickness - 0.01  # 1 см от обшивки
        
        total_area += stringer.area
        total_static_moment += stringer.area * stringer_y
    
    if total_area == 0:
        raise ValueError("Общая площадь сечения равна нулю")
    
    # Координата нейтральной оси (центра тяжести)
    neutral_axis_y = total_static_moment / total_area
    
    return neutral_axis_y


def calculate_stress_distribution(panel, stringers, moment):
    """
    Расчёт распределения напряжений в сечении панели.
    
    Рассчитывает напряжения в обшивке и стрингерах от изгибающего момента.
    
    Args:
        panel: Объект класса Panel
        stringers: Список объектов Stringer
        moment: Изгибающий момент в Н·м
        
    Returns:
        dict: Словарь с распределением напряжений:
            {
                'neutral_axis': float,  # координата нейтральной оси
                'skin_stress': float,   # напряжение в обшивке
                'stringer_stresses': list,  # напряжения в стрингерах
                'max_stress': float,    # максимальное напряжение
                'min_stress': float     # минимальное напряжение
            }
    """
    if panel.reduced_inertia is None:
        raise ValueError("Эффективный момент инерции не рассчитан")
    
    # Определение нейтральной оси
    neutral_axis_y = calculate_neutral_axis(panel, stringers)
    
    # Расстояние от нейтральной оси до верхнего края (максимальное сжатие)
    y_top = panel.box_height - neutral_axis_y
    
    # Расстояние от нейтральной оси до нижнего края (растяжение, если есть)
    y_bottom = neutral_axis_y
    
    # Напряжения
    stress_top = calculate_bending_stress(moment, panel.reduced_inertia, y_top)
    stress_bottom = calculate_bending_stress(moment, panel.reduced_inertia, y_bottom)
    
    # Напряжение в обшивке (верхняя панель - сжатие)
    skin_stress = stress_top
    
    # Напряжения в стрингерах
    stringer_stresses = []
    for stringer in stringers:
        if stringer.area is None:
            continue
        
        # Координата центра тяжести стрингера
        if hasattr(stringer, 'centroid_y') and stringer.centroid_y is not None:
            stringer_bottom = panel.box_height - panel.skin_thickness
            stringer_y = stringer_bottom - stringer.centroid_y
        else:
            if hasattr(stringer, 'web_height') and stringer.web_height:
                stringer_y = panel.box_height - panel.skin_thickness - stringer.web_height / 2
            else:
                stringer_y = panel.box_height - panel.skin_thickness - 0.01
        
        y_stringer = stringer_y - neutral_axis_y
        stringer_stress = calculate_bending_stress(moment, panel.reduced_inertia, y_stringer)
        stringer_stresses.append(stringer_stress)
    
    return {
        'neutral_axis': neutral_axis_y,
        'skin_stress': skin_stress,
        'stringer_stresses': stringer_stresses,
        'max_stress': max(abs(stress_top), abs(stress_bottom)),
        'min_stress': min(stress_top, stress_bottom),
        'stress_top': stress_top,
        'stress_bottom': stress_bottom
    }
