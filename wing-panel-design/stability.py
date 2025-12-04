"""
Расчёт критических напряжений.
Функции для расчёта потери устойчивости обшивки и стрингеров.
"""

import math


def local_skin_buckling(skin_thickness, stringer_spacing, material, 
                        boundary_condition='hinged'):
    """
    Расчёт критического напряжения местной потери устойчивости обшивки.
    
    Формула из deep-research-3-result.md, раздел 1:
    σ_cr = k_σ * (π² * E) / (12 * (1 - ν²)) * (t / b_p)²
    
    где:
    - k_σ - коэффициент устойчивости (зависит от граничных условий)
    - E - модуль упругости
    - ν - коэффициент Пуассона
    - t - толщина обшивки
    - b_p - ширина поля обшивки (шаг стрингеров)
    
    Args:
        skin_thickness: Толщина обшивки в метрах
        stringer_spacing: Шаг стрингеров (ширина поля обшивки) в метрах
        material: Объект класса Material
        boundary_condition: Граничные условия - 'hinged', 'clamped' или 'mixed'
            - 'hinged': оба края шарнирно опёрты (k_σ = 4.0)
            - 'clamped': оба края защемлены (k_σ = 6.97)
            - 'mixed': один защемлён, другой шарнирно (k_σ = 5.0)
        
    Returns:
        float: Критическое напряжение в Па
        
    Raises:
        ValueError: Если граничные условия некорректны или параметры неположительны
    """
    # Валидация граничных условий
    valid_conditions = ['hinged', 'clamped', 'mixed']
    if boundary_condition not in valid_conditions:
        raise ValueError(
            f"Неподдерживаемые граничные условия: {boundary_condition}. "
            f"Доступные: {valid_conditions}"
        )
    
    # Валидация параметров
    if skin_thickness <= 0:
        raise ValueError(f"Толщина обшивки должна быть положительной, получено {skin_thickness}")
    
    if stringer_spacing <= 0:
        raise ValueError(f"Шаг стрингеров должен быть положительным, получено {stringer_spacing}")
    
    # Коэффициент устойчивости в зависимости от граничных условий
    # Значения из deep-research-3-result.md
    k_sigma = {
        'hinged': 4.0,      # оба края шарнирно опёрты
        'clamped': 6.97,    # оба края защемлены
        'mixed': 5.0        # один защемлён, другой шарнирно
    }[boundary_condition]
    
    # Параметры материала
    E = material.young_modulus
    nu = material.poisson_ratio
    
    # Ширина поля обшивки
    b_p = stringer_spacing
    
    # Толщина обшивки
    t = skin_thickness
    
    # Расчёт критического напряжения
    # σ_cr = k_σ * (π² * E) / (12 * (1 - ν²)) * (t / b_p)²
    sigma_cr = (
        k_sigma * math.pi**2 * E / 
        (12 * (1 - nu**2)) * 
        (t / b_p)**2
    )
    
    # Проверка физической разумности результата
    if sigma_cr < 0:
        raise ValueError(f"Получено отрицательное критическое напряжение: {sigma_cr}")
    
    if sigma_cr > material.ultimate_strength * 10:
        # Предупреждение: критическое напряжение слишком велико
        # (возможно, обшивка слишком толстая или шаг слишком мал)
        pass  # Не критично, но можно добавить предупреждение
    
    return sigma_cr


def local_stringer_buckling(element_width, element_thickness, material,
                            element_type='web'):
    """
    Расчёт критического напряжения местной потери устойчивости элемента стрингера.
    
    Формула из deep-research-3-result.md, раздел 2:
    σ_cr = k_σ,i * (π² * E) / (12 * (1 - ν²)) * (t_i / b_i)²
    
    где:
    - k_σ,i - коэффициент устойчивости для конкретного элемента
    - E - модуль упругости
    - ν - коэффициент Пуассона
    - t_i - толщина элемента
    - b_i - ширина элемента (высота стенки или ширина полки)
    
    Args:
        element_width: Ширина элемента в метрах (высота стенки или ширина полки)
        element_thickness: Толщина элемента в метрах
        material: Объект класса Material
        element_type: Тип элемента стрингера:
            - 'web': стенка между полками (оба края защемлены, k_σ = 6.97)
            - 'flange_internal': внутренний пояс (оба края опёрты, k_σ = 4.0)
            - 'flange_free': свободный вынос полки - консоль (k_σ = 0.43)
            - 'flange_Z': пояс Z-стрингера (k_σ = 0.425)
        
    Returns:
        float: Критическое напряжение в Па
        
    Raises:
        ValueError: Если тип элемента некорректен или параметры неположительны
    """
    # Валидация параметров
    if element_width <= 0:
        raise ValueError(f"Ширина элемента должна быть положительной, получено {element_width}")
    
    if element_thickness <= 0:
        raise ValueError(f"Толщина элемента должна быть положительной, получено {element_thickness}")
    
    # Коэффициенты устойчивости для разных элементов
    # Значения из deep-research-3-result.md, раздел 2
    k_sigma = {
        'web_clamped': 6.97,      # стенка между полками (оба края защемлены)
        'flange_internal': 4.0,    # внутренний пояс (оба края опёрты)
        'flange_free': 0.43,       # свободный вынос полки (консоль)
        'flange_Z': 0.425          # пояс Z-стрингера
    }
    
    # Определение коэффициента в зависимости от типа элемента
    valid_types = ['web', 'flange_internal', 'flange_free', 'flange_Z']
    if element_type not in valid_types:
        raise ValueError(
            f"Неподдерживаемый тип элемента: {element_type}. "
            f"Доступные: {valid_types}"
        )
    
    if element_type == 'web':
        k = k_sigma['web_clamped']
    elif element_type == 'flange_internal':
        k = k_sigma['flange_internal']
    elif element_type == 'flange_free':
        k = k_sigma['flange_free']
    else:  # element_type == 'flange_Z'
        k = k_sigma['flange_Z']
    
    # Параметры материала
    E = material.young_modulus
    nu = material.poisson_ratio
    
    # Расчёт критического напряжения
    # σ_cr = k_σ,i * (π² * E) / (12 * (1 - ν²)) * (t_i / b_i)²
    sigma_cr = (
        k * math.pi**2 * E / 
        (12 * (1 - nu**2)) * 
        (element_thickness / element_width)**2
    )
    
    # Проверка физической разумности результата
    if sigma_cr < 0:
        raise ValueError(f"Получено отрицательное критическое напряжение: {sigma_cr}")
    
    return sigma_cr


def check_stringer_local_buckling(stringer, material, stress):
    """
    Проверка местной устойчивости всех элементов стрингера.
    
    Проверяет каждый элемент сечения стрингера (стенка, полки) на потерю
    местной устойчивости при заданном рабочем напряжении.
    
    Args:
        stringer: Объект класса Stringer
        material: Объект класса Material
        stress: Рабочее напряжение в Па (сжимающее)
        
    Returns:
        dict: Словарь с результатами проверки для каждого элемента:
            {
                'web': {
                    'sigma_cr': float,  # критическое напряжение
                    'safe': bool,       # безопасно ли напряжение
                    'safety_margin': float  # запас прочности
                },
                'flanges': [
                    {
                        'type': str,    # тип полки
                        'sigma_cr': float,
                        'safe': bool,
                        'safety_margin': float
                    },
                    ...
                ],
                'overall_safe': bool    # безопасны ли все элементы
            }
    """
    results = {
        'web': None,
        'flanges': [],
        'overall_safe': True
    }
    
    # Проверка стенки
    if stringer.web_height is not None and stringer.web_thickness is not None:
        try:
            sigma_cr_web = local_stringer_buckling(
                stringer.web_height,
                stringer.web_thickness,
                material,
                'web'
            )
            
            is_safe = abs(stress) < sigma_cr_web
            safety_margin = sigma_cr_web / abs(stress) if abs(stress) > 1e-6 else float('inf')
            
            results['web'] = {
                'sigma_cr': sigma_cr_web,
                'safe': is_safe,
                'safety_margin': safety_margin
            }
            
            if not is_safe:
                results['overall_safe'] = False
                
        except (ValueError, ZeroDivisionError):
            results['web'] = {
                'sigma_cr': None,
                'safe': None,
                'safety_margin': None,
                'error': 'Не удалось рассчитать критическое напряжение'
            }
    
    # Проверка полок
    if stringer.flange_width is not None and stringer.flange_thickness is not None:
        # Определяем тип полки в зависимости от типа стрингера
        if stringer.type == 'Z':
            # Для Z-стрингера: полки как пояс Z-стрингера
            flange_type = 'flange_Z'
        elif stringer.type == 'C':
            # Для швеллера: одна полка свободная, другая внутренняя
            # Упрощённо: обе как внутренние
            flange_type = 'flange_internal'
        elif stringer.type == 'T':
            # Для таврового: полка как внутренняя
            flange_type = 'flange_internal'
        elif stringer.type == 'L':
            # Для уголкового: одна полка свободная
            flange_type = 'flange_free'
        else:
            flange_type = 'flange_internal'  # по умолчанию
        
        try:
            sigma_cr_flange = local_stringer_buckling(
                stringer.flange_width,
                stringer.flange_thickness,
                material,
                flange_type
            )
            
            is_safe = abs(stress) < sigma_cr_flange
            safety_margin = sigma_cr_flange / abs(stress) if abs(stress) > 1e-6 else float('inf')
            
            results['flanges'].append({
                'type': flange_type,
                'sigma_cr': sigma_cr_flange,
                'safe': is_safe,
                'safety_margin': safety_margin
            })
            
            if not is_safe:
                results['overall_safe'] = False
                
        except (ValueError, ZeroDivisionError):
            results['flanges'].append({
                'type': flange_type,
                'sigma_cr': None,
                'safe': None,
                'safety_margin': None,
                'error': 'Не удалось рассчитать критическое напряжение'
            })
    
    return results


def general_panel_buckling(panel, stringers, material, panel_length,
                            boundary_condition='hinged', E_red=None):
    """
    Расчёт критического напряжения общей потери устойчивости панели.
    
    Использует формулу Эйлера для эквивалентного стержня:
    N_cr = (π² * E_red * I_eff) / (μ * L)²
    σ_cr = N_cr / A_eff = (π² * E_red) / λ_eff²
    
    где:
    - λ_eff = (μ * L) / r_eff - эффективная гибкость
    - r_eff = √(I_eff / A_eff) - эффективный радиус инерции
    - μ - коэффициент приведённой длины
    - L - длина панели
    - E_red - редуцированный модуль упругости
    - I_eff - эффективный момент инерции
    - A_eff - эффективная площадь
    
    Из deep-research-3-result.md, раздел 3
    
    Args:
        panel: Объект класса Panel с рассчитанными эффективными параметрами
        stringers: Список объектов Stringer (используется для проверки)
        material: Объект класса Material
        panel_length: Длина панели по оси сжатия в метрах
        boundary_condition: Граничные условия по концам панели:
            - 'hinged': оба конца шарнирно опёрты (μ = 1.0)
            - 'clamped': оба конца защемлены (μ = 0.5)
            - 'mixed': один защемлён, другой шарнирно (μ = 0.7)
            - 'cantilever': консоль (μ = 2.0)
        E_red: Редуцированный модуль упругости в Па (опционально).
               Если None, используется обычный модуль упругости.
        
    Returns:
        float: Критическое напряжение общей устойчивости в Па
        
    Raises:
        ValueError: Если параметры некорректны или не рассчитаны
    """
    # Валидация граничных условий
    valid_conditions = ['hinged', 'clamped', 'mixed', 'cantilever']
    if boundary_condition not in valid_conditions:
        raise ValueError(
            f"Неподдерживаемые граничные условия: {boundary_condition}. "
            f"Доступные: {valid_conditions}"
        )
    
    # Валидация параметров панели
    if panel.reduced_area is None:
        raise ValueError("Эффективная площадь панели не рассчитана")
    
    if panel.reduced_inertia is None:
        raise ValueError("Эффективный момент инерции панели не рассчитан")
    
    if panel_length <= 0:
        raise ValueError(f"Длина панели должна быть положительной, получено {panel_length}")
    
    # Коэффициент приведённой длины
    # Значения из deep-research-3-result.md, раздел 4.2
    mu = {
        'hinged': 1.0,      # оба конца шарнирно опёрты
        'clamped': 0.5,     # оба конца защемлены
        'mixed': 0.7,       # один защемлён, другой шарнирно
        'cantilever': 2.0   # консоль (один конец свободный, другой защемлён)
    }[boundary_condition]
    
    # Эффективные параметры (уже рассчитаны с учётом редуцирования)
    A_eff = panel.reduced_area
    I_eff = panel.reduced_inertia
    
    # Редуцированный модуль упругости
    if E_red is None:
        E_red = material.young_modulus
    elif E_red <= 0:
        raise ValueError(f"Редуцированный модуль должен быть положительным, получено {E_red}")
    
    # Эффективный радиус инерции
    if A_eff <= 0:
        raise ValueError(f"Эффективная площадь должна быть положительной, получено {A_eff}")
    
    r_eff = math.sqrt(I_eff / A_eff)
    
    # Эффективная гибкость
    lambda_eff = (mu * panel_length) / r_eff
    
    if lambda_eff <= 0:
        raise ValueError(f"Эффективная гибкость должна быть положительной, получено {lambda_eff}")
    
    # Критическое напряжение по формуле Эйлера
    # σ_cr = (π² * E_red) / λ_eff²
    sigma_cr = (math.pi**2 * E_red) / (lambda_eff**2)
    
    # Проверка физической разумности результата
    if sigma_cr < 0:
        raise ValueError(f"Получено отрицательное критическое напряжение: {sigma_cr}")
    
    return sigma_cr
