"""
Расчёт геометрии крыла и сечений.
Функции для расчёта геометрических параметров крыла в различных сечениях.
"""


def calculate_chord(z_relative, root_chord, tip_chord, span):
    """
    Расчёт хорды в сечении z_relative.
    
    Линейная интерполяция для трапециевидного крыла:
    c(z) = c_root - (c_root - c_tip) * z_relative
    
    где:
    - c_root - корневая хорда
    - c_tip - концевая хорда
    - z_relative - относительное положение по размаху (0 - корень, 1 - законцовка)
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        root_chord: Корневая хорда в метрах
        tip_chord: Концевая хорда в метрах
        span: Полный размах крыла в метрах
        
    Returns:
        float: Хорда в сечении в метрах
        
    Raises:
        ValueError: Если z_relative вне диапазона [0, 1]
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    # Линейная интерполяция для трапециевидного крыла
    chord = root_chord - (root_chord - tip_chord) * z_relative
    
    return chord


def calculate_box_height(z_relative, aircraft):
    """
    Интерполяция высоты кессона между корнем, серединой и законцовкой.
    
    Используется кусочно-линейная интерполяция:
    - Между корнем (z=0) и серединой (z=0.5): линейная интерполяция
    - Между серединой (z=0.5) и законцовкой (z=1): линейная интерполяция
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        aircraft: Объект класса Aircraft
        
    Returns:
        float: Высота кессона в метрах
        
    Raises:
        ValueError: Если z_relative вне диапазона [0, 1]
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    if z_relative <= 0.5:
        # Интерполяция между корнем и серединой
        t = z_relative / 0.5  # нормализованный параметр [0, 1]
        h = aircraft.box_height_root - (
            aircraft.box_height_root - aircraft.box_height_mid
        ) * t
    else:
        # Интерполяция между серединой и законцовкой
        t = (z_relative - 0.5) / 0.5  # нормализованный параметр [0, 1]
        h = aircraft.box_height_mid - (
            aircraft.box_height_mid - aircraft.box_height_tip
        ) * t
    
    return h


def calculate_spar_positions(z_relative, aircraft):
    """
    Интерполяция положения лонжеронов по размаху крыла.
    
    Линейная интерполяция между корнем и законцовкой для каждого лонжерона:
    x(z) = x_root + (x_tip - x_root) * z_relative
    
    где x - положение лонжерона в долях хорды.
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        aircraft: Объект класса Aircraft
        
    Returns:
        dict: Словарь с позициями лонжеронов в долях хорды:
            {'front': float, 'rear': float}
            
    Raises:
        ValueError: Если z_relative вне диапазона [0, 1]
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    # Линейная интерполяция для переднего лонжерона
    front_spar = (
        aircraft.spar_positions_root['front'] +
        (aircraft.spar_positions_tip['front'] - aircraft.spar_positions_root['front']) *
        z_relative
    )
    
    # Линейная интерполяция для заднего лонжерона
    rear_spar = (
        aircraft.spar_positions_root['rear'] +
        (aircraft.spar_positions_tip['rear'] - aircraft.spar_positions_root['rear']) *
        z_relative
    )
    
    return {'front': front_spar, 'rear': rear_spar}


def calculate_box_width(z_relative, aircraft):
    """
    Расчёт ширины кессона (расстояние между лонжеронами).
    
    Ширина кессона = (позиция заднего лонжерона - позиция переднего лонжерона) * хорда
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        aircraft: Объект класса Aircraft
        
    Returns:
        float: Ширина кессона в метрах
        
    Raises:
        ValueError: Если z_relative вне диапазона [0, 1]
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    # Расчёт хорды
    chord = calculate_chord(
        z_relative,
        aircraft.root_chord,
        aircraft.tip_chord,
        aircraft.wing_span
    )
    
    # Расчёт позиций лонжеронов
    spar_pos = calculate_spar_positions(z_relative, aircraft)
    
    # Ширина кессона = расстояние между лонжеронами
    width = (spar_pos['rear'] - spar_pos['front']) * chord
    
    return width


def calculate_spar_flange_area(z_relative, aircraft, material):
    """
    Оценочный расчёт площади полок лонжеронов.
    
    Упрощённая модель для начальных расчётов. Использует типовые значения
    или упрощённую модель на основе изгибающего момента.
    
    Для детального расчёта нужны дополнительные данные о нагрузках
    и конструктивных требованиях.
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        aircraft: Объект класса Aircraft
        material: Объект класса Material (для получения допускаемых напряжений)
        
    Returns:
        dict: Словарь с площадями полок:
            {'front': float, 'rear': float} в м²
            
    Note:
        Это упрощённая оценочная модель. Для точного расчёта требуется
        полный расчёт напряжений и подбор сечения лонжерона.
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    # Типовые значения площади полок для Boeing 737-800
    # Основаны на приблизительных оценках для двухлонжеронного крыла
    
    # У корня полки больше, к законцовке уменьшаются
    # Типовые значения: 50-100 см² у корня, 10-20 см² у законцовки
    area_root = 0.0075  # 75 см² у корня
    area_tip = 0.0015  # 15 см² у законцовки
    
    # Линейная интерполяция
    area = area_root - (area_root - area_tip) * z_relative
    
    # Оба лонжерона имеют примерно одинаковую площадь полок
    # (в реальности могут отличаться, но для упрощения принимаем одинаковыми)
    return {
        'front': area,
        'rear': area
    }


def calculate_absolute_position(z_relative, span):
    """
    Преобразование относительного положения в абсолютное расстояние от корня.
    
    Args:
        z_relative: Относительное положение по размаху (0.0 - 1.0)
        span: Полный размах крыла в метрах
        
    Returns:
        float: Абсолютное расстояние от корня в метрах
    """
    if not 0 <= z_relative <= 1:
        raise ValueError(f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}")
    
    semispan = span / 2  # полуразмах
    return z_relative * semispan
