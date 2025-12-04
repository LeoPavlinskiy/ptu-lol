"""
Класс для хранения свойств материала В95-Т1.
Параметры извлечены из deep-research-2-result.md
"""


class Material:
    """
    Класс для хранения механических свойств материала.
    
    Поддерживает сплав В95-Т1 в различных формах (лист, профиль).
    Содержит прочностные характеристики, модули упругости, допускаемые
    напряжения и коэффициенты запаса прочности.
    """
    
    # Поддерживаемые типы материалов
    SUPPORTED_MATERIALS = ['B95T1']
    # Поддерживаемые типы продукции
    SUPPORTED_PRODUCTS = ['sheet', 'profile']
    # Типы нагрузок
    LOAD_TYPES = ['tension', 'compression', 'shear']
    
    def __init__(self, material_type='B95T1', product_type='sheet'):
        """
        Инициализация свойств материала.
        
        Args:
            material_type: Тип материала (по умолчанию 'B95T1')
            product_type: Тип продукции - 'sheet' (лист) или 'profile' (профиль)
            
        Raises:
            ValueError: Если указан неподдерживаемый тип материала или продукции
        """
        # Валидация входных параметров
        if material_type not in self.SUPPORTED_MATERIALS:
            raise ValueError(
                f"Неподдерживаемый тип материала: {material_type}. "
                f"Доступные: {self.SUPPORTED_MATERIALS}"
            )
        if product_type not in self.SUPPORTED_PRODUCTS:
            raise ValueError(
                f"Неподдерживаемый тип продукции: {product_type}. "
                f"Доступные: {self.SUPPORTED_PRODUCTS}"
            )
        
        self.material_type = material_type
        self.product_type = product_type
        
        # Прочностные характеристики в зависимости от типа продукции
        # Параметры из deep-research-2-result.md
        if material_type == 'B95T1' and product_type == 'sheet':
            # Лист В95-Т1
            self.ultimate_strength = 520e6  # Па (σв) - предел прочности
            self.yield_strength = 440e6  # Па (σ0.2) - предел текучести
            self.proportional_limit = 0.8 * self.yield_strength  # Па (σпц)
        elif material_type == 'B95T1' and product_type == 'profile':
            # Профиль В95-Т1 (прессованный)
            self.ultimate_strength = 520e6  # Па (σв)
            self.yield_strength = 450e6  # Па (σ0.2)
            self.proportional_limit = 0.8 * self.yield_strength  # Па (σпц)
        
        # Общие упругие свойства (не зависят от типа продукции)
        self.young_modulus = 74e9  # Па (E) - модуль упругости
        self.shear_modulus = 26e9  # Па (G) - модуль сдвига
        self.poisson_ratio = 0.32  # μ - коэффициент Пуассона
        self.density = 2850  # кг/м³ - плотность
        
        # Допускаемые напряжения (расчётные значения с учётом запаса прочности)
        # Из deep-research-2-result.md
        self.allowable_tension = 350e6  # Па - допускаемое напряжение растяжения
        self.allowable_compression = 300e6  # Па - допускаемое напряжение сжатия
        self.allowable_shear = 180e6  # Па - допускаемое напряжение сдвига
        
        # Коэффициенты запаса прочности
        self.safety_factor_ultimate = 1.5  # Запас по разрушению
        self.safety_factor_yield = 1.15  # Запас по текучести
    
    def get_allowable_stress(self, load_type):
        """
        Получение допускаемого напряжения по типу нагрузки.
        
        Args:
            load_type: Тип нагрузки - 'tension', 'compression' или 'shear'
            
        Returns:
            float: Допускаемое напряжение в Па
            
        Raises:
            ValueError: Если указан неподдерживаемый тип нагрузки
        """
        if load_type not in self.LOAD_TYPES:
            raise ValueError(
                f"Неподдерживаемый тип нагрузки: {load_type}. "
                f"Доступные: {self.LOAD_TYPES}"
            )
        
        if load_type == 'tension':
            return self.allowable_tension
        elif load_type == 'compression':
            return self.allowable_compression
        elif load_type == 'shear':
            return self.allowable_shear
    
    def check_strength(self, stress, load_type='compression'):
        """
        Проверка прочности по допускаемым напряжениям.
        
        Args:
            stress: Действующее напряжение в Па
            load_type: Тип нагрузки - 'tension', 'compression' или 'shear'
            
        Returns:
            dict: Словарь с результатами проверки:
                - 'safe': bool - безопасно ли напряжение
                - 'safety_margin': float - запас прочности (σ_допускаемое / σ_действующее)
                - 'stress': float - действующее напряжение
                - 'allowable': float - допускаемое напряжение
                - 'load_type': str - тип нагрузки
                
        Raises:
            ValueError: Если указан неподдерживаемый тип нагрузки
        """
        allowable = self.get_allowable_stress(load_type)
        
        # Запас прочности
        if abs(stress) < 1e-6:  # Избегаем деления на ноль
            safety_margin = float('inf')
        else:
            safety_margin = allowable / abs(stress)
        
        # Проверка безопасности
        is_safe = abs(stress) <= allowable
        
        return {
            'safe': is_safe,
            'safety_margin': safety_margin,
            'stress': stress,
            'allowable': allowable,
            'load_type': load_type
        }
    
    def get_reduced_modulus(self, stress):
        """
        Расчёт редуцированного модуля упругости.
        
        Для упрощённой модели: если напряжение меньше предела пропорциональности,
        используется обычный модуль упругости. При превышении предела
        пропорциональности модуль снижается.
        
        Args:
            stress: Действующее напряжение в Па
            
        Returns:
            float: Редуцированный модуль упругости в Па
        """
        # Если напряжение меньше предела пропорциональности - упругая область
        if abs(stress) <= self.proportional_limit:
            return self.young_modulus
        
        # В закритической области (упрощённая модель)
        # Касательный модуль снижается пропорционально превышению
        # Это упрощённая модель, для точного расчёта нужны экспериментальные данные
        stress_ratio = abs(stress) / self.yield_strength
        
        if stress_ratio <= 1.0:
            # Между пределом пропорциональности и текучести
            # Линейная интерполяция между E и E_t (касательный модуль)
            # Для алюминия в этой области E_t ≈ 0.7-0.8 E
            E_t = 0.75 * self.young_modulus
            ratio = (abs(stress) - self.proportional_limit) / (
                self.yield_strength - self.proportional_limit
            )
            return self.young_modulus - (self.young_modulus - E_t) * ratio
        else:
            # За пределом текучести - касательный модуль
            # Для алюминия E_t ≈ 0.1-0.2 E в пластической области
            return 0.15 * self.young_modulus
    
    def get_ultimate_stress(self, load_type='compression'):
        """
        Получение предельного напряжения (с учётом коэффициента запаса).
        
        Args:
            load_type: Тип нагрузки - 'tension', 'compression' или 'shear'
            
        Returns:
            float: Предельное напряжение в Па (σ_допускаемое * коэффициент_запаса)
        """
        allowable = self.get_allowable_stress(load_type)
        return allowable * self.safety_factor_ultimate
    
    def __repr__(self):
        """Строковое представление объекта."""
        return (
            f"Material(material_type='{self.material_type}', "
            f"product_type='{self.product_type}', "
            f"σв={self.ultimate_strength/1e6:.0f} МПа, "
            f"σ0.2={self.yield_strength/1e6:.0f} МПа)"
        )
