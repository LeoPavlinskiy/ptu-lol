"""
Класс для хранения данных о самолёте Boeing 737-800.
Параметры извлечены из deep-research-1-result.md
"""


class Aircraft:
    """
    Класс для хранения геометрических и конструктивных параметров самолёта.
    
    Содержит данные о Boeing 737-800: геометрию крыла, расположение лонжеронов,
    высоту кессона и другие параметры, необходимые для расчёта прочности.
    """
    
    def __init__(self):
        """
        Инициализация параметров самолёта Boeing 737-800.
        Все параметры извлечены из deep-research-1-result.md
        """
        # Основные параметры
        self.name = "Boeing 737-800"
        self.class_type = "пассажирский, магистральный, узкофюзеляжный"
        self.mtow = 79016  # кг (максимальная взлётная масса)
        self.normal_takeoff_mass = 70000  # кг (для расчётов)
        
        # Геометрия крыла
        self.wing_span = 34.32  # м (полный размах)
        self.wing_area = 124.6  # м²
        self.aspect_ratio = 9.45
        self.sweep_le = 28.5  # градусы (стреловидность по передней кромке)
        self.incidence_angle = 3.0  # градусы (угол установки крыла)
        self.dihedral = 6.0  # градусы (поперечный угол V)
        self.airfoil_type = "Boeing 737 midspan airfoil"
        
        # Хорды
        self.root_chord = 6.65  # м (корневая хорда)
        self.tip_chord = 1.25  # м (концевая хорда)
        self.taper_ratio = 0.19  # коэффициент сужения
        
        # Конструктивно-силовая схема
        self.spar_count = 2  # количество основных лонжеронов
        self.spar_positions_root = {
            'front': 0.15,  # доля хорды от передней кромки
            'rear': 0.60
        }
        self.spar_positions_tip = {
            'front': 0.20,
            'rear': 0.74
        }
        self.structure_type = "лонжеронно-стрингерный кессонный"
        
        # Высота кессона (для интерполяции)
        self.box_height_root = 0.5  # м (у корня)
        self.box_height_mid = 0.35  # м (на середине размаха, z=0.5L)
        self.box_height_tip = 0.2  # м (у законцовки)
    
    def _validate_z_relative(self, z_relative):
        """
        Валидация относительного положения по размаху.
        
        Args:
            z_relative: Относительное положение (0 <= z_relative <= 1)
            
        Raises:
            ValueError: Если z_relative вне допустимого диапазона
        """
        if not 0 <= z_relative <= 1:
            raise ValueError(
                f"z_relative должно быть в диапазоне [0, 1], получено {z_relative}"
            )
    
    def get_chord(self, z_relative):
        """
        Расчёт хорды в сечении по относительному положению.
        
        Для трапециевидного крыла используется линейная интерполяция:
        c(z) = c_root - (c_root - c_tip) * z_relative
        
        Args:
            z_relative: Относительное положение по размаху (0 - корень, 1 - законцовка)
            
        Returns:
            float: Хорда в метрах
            
        Raises:
            ValueError: Если z_relative вне допустимого диапазона
        """
        self._validate_z_relative(z_relative)
        
        # Линейная интерполяция для трапециевидного крыла
        chord = self.root_chord - (self.root_chord - self.tip_chord) * z_relative
        
        # Проверка физической разумности
        if chord < 0:
            raise ValueError(f"Получена отрицательная хорда: {chord} м")
        
        return chord
    
    def get_box_height(self, z_relative):
        """
        Расчёт высоты кессона в сечении.
        
        Используется кусочно-линейная интерполяция между тремя точками:
        - Корень (z=0): box_height_root
        - Середина (z=0.5): box_height_mid
        - Законцовка (z=1): box_height_tip
        
        Args:
            z_relative: Относительное положение по размаху (0 - корень, 1 - законцовка)
            
        Returns:
            float: Высота кессона в метрах
            
        Raises:
            ValueError: Если z_relative вне допустимого диапазона
        """
        self._validate_z_relative(z_relative)
        
        if z_relative <= 0.5:
            # Интерполяция между корнем и серединой
            t = z_relative / 0.5  # нормализованный параметр [0, 1]
            height = self.box_height_root - (
                self.box_height_root - self.box_height_mid
            ) * t
        else:
            # Интерполяция между серединой и законцовкой
            t = (z_relative - 0.5) / 0.5  # нормализованный параметр [0, 1]
            height = self.box_height_mid - (
                self.box_height_mid - self.box_height_tip
            ) * t
        
        # Проверка физической разумности
        if height < 0:
            raise ValueError(f"Получена отрицательная высота кессона: {height} м")
        
        return height
    
    def get_spar_positions(self, z_relative):
        """
        Расчёт положения лонжеронов в сечении.
        
        Линейная интерполяция между корнем и законцовкой для каждого лонжерона.
        
        Args:
            z_relative: Относительное положение по размаху (0 - корень, 1 - законцовка)
            
        Returns:
            dict: Словарь с позициями лонжеронов в долях хорды:
                {'front': float, 'rear': float}
                
        Raises:
            ValueError: Если z_relative вне допустимого диапазона
        """
        self._validate_z_relative(z_relative)
        
        # Линейная интерполяция для переднего лонжерона
        front_spar = (
            self.spar_positions_root['front'] +
            (self.spar_positions_tip['front'] - self.spar_positions_root['front']) *
            z_relative
        )
        
        # Линейная интерполяция для заднего лонжерона
        rear_spar = (
            self.spar_positions_root['rear'] +
            (self.spar_positions_tip['rear'] - self.spar_positions_root['rear']) *
            z_relative
        )
        
        # Проверка физической разумности
        if not 0 <= front_spar <= 1:
            raise ValueError(
                f"Передний лонжерон вне допустимого диапазона: {front_spar}"
            )
        if not 0 <= rear_spar <= 1:
            raise ValueError(
                f"Задний лонжерон вне допустимого диапазона: {rear_spar}"
            )
        if front_spar >= rear_spar:
            raise ValueError(
                f"Передний лонжерон ({front_spar}) должен быть перед задним ({rear_spar})"
            )
        
        return {'front': front_spar, 'rear': rear_spar}
    
    def get_box_width(self, z_relative):
        """
        Расчёт ширины кессона (расстояние между лонжеронами).
        
        Ширина кессона = (позиция заднего лонжерона - позиция переднего лонжерона) * хорда
        
        Args:
            z_relative: Относительное положение по размаху (0 - корень, 1 - законцовка)
            
        Returns:
            float: Ширина кессона в метрах
            
        Raises:
            ValueError: Если z_relative вне допустимого диапазона
        """
        self._validate_z_relative(z_relative)
        
        # Получаем хорду и позиции лонжеронов
        chord = self.get_chord(z_relative)
        spar_positions = self.get_spar_positions(z_relative)
        
        # Ширина кессона = расстояние между лонжеронами
        box_width = (spar_positions['rear'] - spar_positions['front']) * chord
        
        # Проверка физической разумности
        if box_width < 0:
            raise ValueError(f"Получена отрицательная ширина кессона: {box_width} м")
        
        return box_width
    
    def get_semispan(self):
        """
        Полуразмах крыла (половина размаха).
        
        Returns:
            float: Полуразмах в метрах
        """
        return self.wing_span / 2
    
    def get_absolute_position(self, z_relative):
        """
        Преобразование относительного положения в абсолютное расстояние от корня.
        
        Args:
            z_relative: Относительное положение по размаху (0 - корень, 1 - законцовка)
            
        Returns:
            float: Абсолютное расстояние от корня в метрах
        """
        self._validate_z_relative(z_relative)
        return z_relative * self.get_semispan()
