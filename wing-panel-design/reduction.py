"""
Методы редуцирования обшивки.
Функции для расчёта эффективной ширины обшивки и редуцированного модуля упругости.
"""

import math
from stability import local_skin_buckling
from loads import calculate_bending_stress, calculate_neutral_axis


def effective_width(skin_width, sigma_cr, sigma_edge, material, method='winter'):
    """
    Расчёт эффективной ширины обшивки при закритическом деформировании.
    
    Поддерживает два метода:
    1. Метод Винтера - с учётом предела текучести (рекомендуется)
    2. Метод фон Кармана - упругая область
    
    Метод Винтера (из deep-research-4-result.md, раздел 1.3):
    λ_p = sqrt(f_y / σ_cr)
    ρ = (1 - 0.22/λ_p) / λ_p  при λ_p > 0.673
    b_eff = ρ * b
    
    Метод фон Кармана (из deep-research-4-result.md, раздел 1.2):
    b_eff = b * sqrt(σ_cr / σ_edge)  при σ_edge >= σ_cr
    
    Args:
        skin_width: Полная ширина обшивки в метрах (шаг стрингеров)
        sigma_cr: Критическое напряжение местной потери устойчивости в Па
        sigma_edge: Напряжение на краю обшивки (у стрингера) в Па
        material: Объект класса Material
        method: Метод расчёта - 'winter' или 'karman'
            - 'winter': формула Винтера (рекомендуется для авиации)
            - 'karman': формула фон Кармана (упругая область)
        
    Returns:
        tuple: (b_eff, rho) где:
            - b_eff: Эффективная ширина в метрах
            - rho: Коэффициент редуцирования (b_eff / b)
        
    Raises:
        ValueError: Если метод некорректен или параметры неположительны
    """
    # Валидация метода
    valid_methods = ['winter', 'karman']
    if method not in valid_methods:
        raise ValueError(
            f"Неподдерживаемый метод: {method}. Доступные: {valid_methods}"
        )
    
    # Валидация параметров
    if skin_width <= 0:
        raise ValueError(f"Ширина обшивки должна быть положительной, получено {skin_width}")
    
    if sigma_cr <= 0:
        raise ValueError(f"Критическое напряжение должно быть положительным, получено {sigma_cr}")
    
    if sigma_edge < 0:
        raise ValueError(f"Напряжение на краю не может быть отрицательным, получено {sigma_edge}")
    
    if method == 'winter':
        # Метод Винтера
        # Параметр тонкостенности
        lambda_p = math.sqrt(material.yield_strength / sigma_cr)
        
        if lambda_p <= 0.673:
            # Пластинка работает полностью (не потеряла устойчивость)
            rho = 1.0
        else:
            # Редуцирование
            rho = (1 - 0.22 / lambda_p) / lambda_p
        
        b_eff = rho * skin_width
        
    elif method == 'karman':
        # Формула фон Кармана (упругая область)
        if sigma_edge <= sigma_cr:
            # Пластинка ещё не потеряла устойчивость
            b_eff = skin_width
            rho = 1.0
        else:
            # Закритическая область
            b_eff = skin_width * math.sqrt(sigma_cr / sigma_edge)
            rho = b_eff / skin_width
    
    # Проверка физической разумности результата
    if b_eff < 0:
        raise ValueError(f"Получена отрицательная эффективная ширина: {b_eff}")
    
    if b_eff > skin_width:
        # Эффективная ширина не может быть больше полной
        b_eff = skin_width
        rho = 1.0
    
    return b_eff, rho


def reduced_modulus(panel, stringers, material, stress_level):
    """
    Расчёт редуцированного модуля упругости.
    
    Редуцированный модуль учитывает различие в работе стрингеров
    (упругая область, модуль E) и обшивки (может быть в пластической области,
    касательный модуль E_t).
    
    Формула из deep-research-4-result.md, раздел 3:
    E_red = (E * A_s + E_t * A_skin_eff) / (A_s + A_skin_eff)
    
    где:
    - E - модуль упругости (для стрингеров)
    - E_t - касательный модуль (для обшивки в пластической области)
    - A_s - площадь стрингеров
    - A_skin_eff - эффективная площадь обшивки
    
    Args:
        panel: Объект класса Panel с рассчитанными параметрами
        stringers: Список объектов Stringer
        material: Объект класса Material
        stress_level: Уровень напряжения в Па (для определения касательного модуля)
        
    Returns:
        float: Редуцированный модуль упругости в Па
        
    Raises:
        ValueError: Если параметры некорректны или не установлены
    """
    # Валидация параметров
    if panel.skin_thickness is None:
        raise ValueError("Толщина обшивки не установлена")
    
    if panel.effective_skin_width is None:
        # Если эффективная ширина не рассчитана, используем шаг стрингеров
        if panel.stringer_spacing is None:
            raise ValueError("Шаг стрингеров или эффективная ширина не установлены")
        effective_width = panel.stringer_spacing
    else:
        effective_width = panel.effective_skin_width
    
    # Модуль упругости
    E = material.young_modulus
    
    # Площадь стрингеров
    A_s = sum(
        s.area for s in stringers
        if s.area is not None
    )
    
    if A_s <= 0:
        raise ValueError("Площадь стрингеров должна быть положительной")
    
    # Эффективная площадь обшивки
    A_skin_eff = panel.skin_thickness * effective_width
    
    if A_skin_eff < 0:
        raise ValueError(f"Эффективная площадь обшивки не может быть отрицательной: {A_skin_eff}")
    
    # Касательный модуль (упрощённая модель)
    # Для алюминия в упругой области (до ~0.6-0.7 f_y) E_t ≈ E
    # В пластической области E_t снижается
    
    if stress_level < 0:
        stress_level = abs(stress_level)  # Работаем с абсолютным значением
    
    # Порог перехода в пластическую область (60% от предела текучести)
    threshold = 0.6 * material.yield_strength
    
    if stress_level < threshold:
        # Упругая область - касательный модуль равен модулю упругости
        E_t = E
    else:
        # Пластическая область - упрощённая модель
        # Линейное снижение от E до 0.1*E при достижении предела текучести
        if stress_level >= material.yield_strength:
            # За пределом текучести - минимальный касательный модуль
            E_t = 0.1 * E
        else:
            # Между порогом и пределом текучести - линейная интерполяция
            stress_range = material.yield_strength - threshold
            stress_excess = stress_level - threshold
            E_t_min = 0.1 * E
            E_t = E - (E - E_t_min) * (stress_excess / stress_range)
    
    # Проверка разумности касательного модуля
    if E_t < 0:
        E_t = 0.01 * E  # Минимальное значение
    if E_t > E:
        E_t = E  # Не может быть больше модуля упругости
    
    # Редуцированный модуль
    # E_red = (E * A_s + E_t * A_skin_eff) / (A_s + A_skin_eff)
    total_area = A_s + A_skin_eff
    
    if total_area <= 0:
        raise ValueError(f"Общая площадь должна быть положительной: {total_area}")
    
    E_red = (E * A_s + E_t * A_skin_eff) / total_area
    
    # Проверка физической разумности результата
    if E_red < 0:
        raise ValueError(f"Получен отрицательный редуцированный модуль: {E_red}")
    
    if E_red > E:
        # Редуцированный модуль не может быть больше обычного
        E_red = E
    
    return E_red


def iterative_reduction(panel, stringers, material, moment,
                        panel_length, max_iterations=10, tolerance=0.02,
                        method='winter', boundary_condition='hinged'):
    """
    Итерационный расчёт с учётом редуцирования обшивки.
    
    Алгоритм из deep-research-4-result.md, раздел 4:
    1. Начальное приближение (без редукции)
    2. Расчёт критического напряжения обшивки
    3. Расчёт действующего напряжения
    4. Проверка и редуцирование обшивки
    5. Пересчёт эффективных параметров
    6. Повторение до сходимости
    
    Args:
        panel: Объект класса Panel
        stringers: Список объектов Stringer
        material: Объект класса Material
        moment: Изгибающий момент в Н·м
        panel_length: Длина панели в метрах
        max_iterations: Максимальное количество итераций (по умолчанию 10)
        tolerance: Допустимая относительная погрешность для сходимости (по умолчанию 0.02 = 2%)
        method: Метод редуцирования - 'winter' или 'karman' (по умолчанию 'winter')
        boundary_condition: Граничные условия для обшивки - 'hinged', 'clamped' или 'mixed'
            (по умолчанию 'hinged')
        
    Returns:
        tuple: (panel, stringers, iteration, convergence_info) где:
            - panel: Обновлённый объект Panel с рассчитанными эффективными параметрами
            - stringers: Список стрингеров (без изменений)
            - iteration: Номер итерации, на которой достигнута сходимость
            - convergence_info: Словарь с информацией о сходимости:
                {
                    'converged': bool,
                    'iterations': int,
                    'final_b_eff': float,
                    'final_sigma_edge': float,
                    'final_sigma_cr': float
                }
        
    Raises:
        ValueError: Если параметры панели не установлены
    """
    # Валидация параметров
    if panel.skin_thickness is None:
        raise ValueError("Толщина обшивки не установлена")
    
    if panel.stringer_spacing is None:
        raise ValueError("Шаг стрингеров не установлен")
    
    if panel.box_height is None:
        panel.calculate_box_height()
    
    # Начальное приближение (без редукции)
    b_eff_prev = panel.stringer_spacing  # полная ширина
    panel.effective_skin_width = b_eff_prev
    
    # Начальный расчёт эффективных параметров
    panel.calculate_effective_area()
    panel.calculate_effective_inertia()
    
    # Начальный редуцированный модуль
    E_red_prev = material.young_modulus
    
    convergence_info = {
        'converged': False,
        'iterations': 0,
        'final_b_eff': None,
        'final_sigma_edge': None,
        'final_sigma_cr': None
    }
    
    # Итерационный цикл
    for iteration in range(max_iterations):
        # Расчёт критического напряжения обшивки
        sigma_cr_skin = local_skin_buckling(
            panel.skin_thickness,
            panel.stringer_spacing,
            material,
            boundary_condition
        )
        
        # Расчёт действующего напряжения на краю обшивки
        # Используем эффективный момент инерции и расстояние до верхнего края
        if panel.reduced_inertia is None or panel.reduced_inertia <= 0:
            # Если момент инерции не рассчитан, используем упрощённую оценку
            y_max = panel.box_height / 2
            sigma_edge = moment * y_max / (panel.reduced_area * (panel.box_height / 2)**2)
        else:
            # Точный расчёт через момент инерции
            y_max = panel.box_height / 2  # расстояние до верхнего края
            sigma_edge = calculate_bending_stress(
                moment,
                panel.reduced_inertia,
                y_max
            )
        
        # Редуцирование обшивки
        if sigma_edge > sigma_cr_skin:
            # Обшивка потеряла устойчивость - редуцируем
            b_eff, rho = effective_width(
                panel.stringer_spacing,
                sigma_cr_skin,
                sigma_edge,
                material,
                method
            )
        else:
            # Обшивка ещё не потеряла устойчивость
            b_eff = panel.stringer_spacing
            rho = 1.0
        
        # Обновление эффективной ширины
        panel.effective_skin_width = b_eff
        
        # Пересчёт эффективных параметров
        panel.calculate_effective_area()
        panel.calculate_effective_inertia()
        
        # Редуцированный модуль
        E_red = reduced_modulus(panel, stringers, material, sigma_edge)
        
        # Проверка сходимости
        # Критерий: относительное изменение эффективной ширины
        if b_eff_prev > 0:
            relative_change = abs(b_eff - b_eff_prev) / b_eff_prev
        else:
            relative_change = 1.0
        
        # Дополнительный критерий: изменение редуцированного модуля
        if E_red_prev > 0:
            E_change = abs(E_red - E_red_prev) / E_red_prev
        else:
            E_change = 1.0
        
        # Сходимость достигнута, если оба изменения малы
        if relative_change < tolerance and E_change < tolerance:
            convergence_info['converged'] = True
            convergence_info['iterations'] = iteration + 1
            convergence_info['final_b_eff'] = b_eff
            convergence_info['final_sigma_edge'] = sigma_edge
            convergence_info['final_sigma_cr'] = sigma_cr_skin
            break
        
        # Сохранение значений для следующей итерации
        b_eff_prev = b_eff
        E_red_prev = E_red
    
    # Если не сошлось за max_iterations итераций
    if not convergence_info['converged']:
        convergence_info['iterations'] = max_iterations
        convergence_info['final_b_eff'] = b_eff
        convergence_info['final_sigma_edge'] = sigma_edge
        convergence_info['final_sigma_cr'] = sigma_cr_skin
    
    return panel, stringers, convergence_info['iterations'], convergence_info
