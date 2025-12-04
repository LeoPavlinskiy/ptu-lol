"""
Расчёт напряжений и проверка прочности.
Функции для расчёта напряжений в панели и проверки прочности.
"""

from loads import calculate_bending_stress, calculate_neutral_axis, calculate_stress_distribution


def calculate_stresses(panel, stringers, moment, material):
    """
    Расчёт напряжений в панели с учётом редуцирования.
    
    Использует эффективные параметры (A_eff, I_eff), рассчитанные
    с учётом редуцирования обшивки.
    
    Args:
        panel: Объект класса Panel с рассчитанными эффективными параметрами
        stringers: Список объектов Stringer
        moment: Изгибающий момент в Н·м
        material: Объект класса Material
        
    Returns:
        dict: Словарь с распределением напряжений:
            {
                'skin': float,        # напряжение в обшивке (Па)
                'stringers': float,   # напряжение в стрингерах (Па)
                'max': float,         # максимальное напряжение (Па)
                'min': float,         # минимальное напряжение (Па)
                'neutral_axis': float # координата нейтральной оси (м)
            }
        
    Raises:
        ValueError: Если эффективные параметры не рассчитаны
    """
    # Проверка эффективных параметров
    if panel.reduced_inertia is None:
        raise ValueError("Эффективный момент инерции не рассчитан")
    
    if panel.reduced_area is None:
        raise ValueError("Эффективная площадь не рассчитана")
    
    if panel.box_height is None:
        panel.calculate_box_height()
    
    # Используем функцию из loads.py для расчёта распределения напряжений
    stress_dist = calculate_stress_distribution(panel, stringers, moment)
    
    # Формируем результат
    stresses = {
        'skin': stress_dist['skin_stress'],
        'stringers': stress_dist['stringer_stresses'][0] if stress_dist['stringer_stresses'] else stress_dist['skin_stress'],
        'max': stress_dist['max_stress'],
        'min': stress_dist['min_stress'],
        'neutral_axis': stress_dist['neutral_axis'],
        'stress_top': stress_dist['stress_top'],
        'stress_bottom': stress_dist['stress_bottom']
    }
    
    return stresses


def check_strength(stress, material, load_type='compression'):
    """
    Проверка прочности по допускаемым напряжениям.
    
    Проверяет, не превышает ли напряжение допускаемое значение
    для заданного типа нагрузки.
    
    Args:
        stress: Действующее напряжение в Па (положительное для сжатия/растяжения)
        material: Объект класса Material
        load_type: Тип нагрузки - 'tension', 'compression' или 'shear'
            (по умолчанию 'compression')
        
    Returns:
        dict: Словарь с результатами проверки:
            {
                'safe': bool,              # безопасно ли напряжение
                'safety_margin': float,    # запас прочности
                'stress': float,           # действующее напряжение
                'allowable': float,        # допускаемое напряжение
                'limit': float,            # предел (пропорциональности или текучести)
                'load_type': str           # тип нагрузки
            }
    """
    # Работаем с абсолютным значением напряжения
    stress_abs = abs(stress)
    
    # Получаем допускаемое напряжение
    allowable = material.get_allowable_stress(load_type)
    
    # Предел пропорциональности (для проверки упругой работы)
    sigma_pc = material.proportional_limit
    
    # Проверка прочности
    is_safe_allowable = stress_abs <= allowable
    is_safe_proportional = stress_abs <= sigma_pc
    
    # Запас прочности
    if stress_abs < 1e-6:  # Избегаем деления на ноль
        safety_margin_allowable = float('inf')
        safety_margin_proportional = float('inf')
    else:
        safety_margin_allowable = allowable / stress_abs
        safety_margin_proportional = sigma_pc / stress_abs
    
    # Общая безопасность (должно быть безопасно и по допускаемому, и по пределу пропорциональности)
    is_safe = is_safe_allowable and is_safe_proportional
    
    return {
        'safe': is_safe,
        'safe_allowable': is_safe_allowable,
        'safe_proportional': is_safe_proportional,
        'safety_margin_allowable': safety_margin_allowable,
        'safety_margin_proportional': safety_margin_proportional,
        'stress': stress,
        'allowable': allowable,
        'proportional_limit': sigma_pc,
        'load_type': load_type
    }


def check_panel_strength(panel, stringers, moment, material):
    """
    Полная проверка прочности панели.
    
    Рассчитывает напряжения и проверяет прочность всех элементов панели.
    
    Args:
        panel: Объект класса Panel с рассчитанными параметрами
        stringers: Список объектов Stringer
        moment: Изгибающий момент в Н·м
        material: Объект класса Material
        
    Returns:
        dict: Словарь с результатами проверки:
            {
                'stresses': dict,          # распределение напряжений
                'skin_check': dict,        # проверка обшивки
                'stringer_checks': list,   # проверка стрингеров
                'overall_safe': bool       # безопасна ли панель в целом
            }
    """
    # Расчёт напряжений
    stresses = calculate_stresses(panel, stringers, moment, material)
    
    # Проверка обшивки (сжатие)
    skin_check = check_strength(stresses['skin'], material, 'compression')
    
    # Проверка стрингеров (сжатие)
    stringer_checks = []
    for i, stringer in enumerate(stringers):
        if stresses.get('stringers'):
            # Используем напряжение стрингера, если есть
            if isinstance(stresses['stringers'], list) and i < len(stresses['stringers']):
                stringer_stress = stresses['stringers'][i]
            else:
                stringer_stress = stresses['max']
        else:
            stringer_stress = stresses['max']
        
        stringer_check = check_strength(stringer_stress, material, 'compression')
        stringer_checks.append({
            'stringer_index': i,
            'check': stringer_check
        })
    
    # Общая безопасность
    overall_safe = (
        skin_check['safe'] and
        all(sc['check']['safe'] for sc in stringer_checks)
    )
    
    return {
        'stresses': stresses,
        'skin_check': skin_check,
        'stringer_checks': stringer_checks,
        'overall_safe': overall_safe
    }
