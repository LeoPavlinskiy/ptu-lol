"""
Класс панели с параметрами.
Представляет верхнюю панель крыла в заданном сечении.
"""


class Panel:
    """
    Класс для представления панели крыла в заданном сечении.
    
    Содержит геометрические параметры панели, информацию о стрингерах
    и эффективные параметры после редуцирования обшивки.
    """
    
    def __init__(self, z_relative, aircraft, material):
        """
        Инициализация панели.
        
        Args:
            z_relative: Относительное положение сечения по размаху (0.0 - 1.0)
            aircraft: Объект класса Aircraft с параметрами самолёта
            material: Объект класса Material с параметрами материала
        """
        self.z_relative = z_relative  # Положение сечения (0.2, 0.4, 0.6, 0.8)
        self.aircraft = aircraft
        self.material = material
        
        # Геометрия панели
        self.skin_thickness = None  # м (толщина обшивки, подбирается)
        self.stringer_spacing = None  # м (шаг стрингеров)
        self.stringer_count = None  # количество стрингеров
        self.panel_width = None  # м (ширина панели между лонжеронами)
        self.box_height = None  # м (высота кессона в сечении)
        
        # Стрингеры
        self.stringers = []  # список объектов Stringer
        
        # Эффективные параметры (после редуцирования)
        self.effective_skin_width = None  # м (эффективная ширина обшивки)
        self.reduced_area = None  # м² (приведённая площадь сечения)
        self.reduced_inertia = None  # м⁴ (приведённый момент инерции)
    
    def calculate_panel_width(self):
        """
        Расчёт ширины панели между лонжеронами.
        
        Использует метод get_box_width() из класса Aircraft.
        
        Returns:
            float: Ширина панели в метрах
            
        Updates:
            self.panel_width: Ширина панели
        """
        self.panel_width = self.aircraft.get_box_width(self.z_relative)
        return self.panel_width
    
    def calculate_box_height(self):
        """
        Расчёт высоты кессона в сечении.
        
        Использует метод get_box_height() из класса Aircraft.
        
        Returns:
            float: Высота кессона в метрах
            
        Updates:
            self.box_height: Высота кессона
        """
        self.box_height = self.aircraft.get_box_height(self.z_relative)
        return self.box_height
    
    def add_stringer(self, stringer):
        """
        Добавление стрингера в панель.
        
        Args:
            stringer: Объект класса Stringer
        """
        self.stringers.append(stringer)
        # Обновляем количество стрингеров
        self.stringer_count = len(self.stringers)
    
    def calculate_effective_area(self):
        """
        Расчёт эффективной площади сечения панели с учётом редуцирования.
        
        Эффективная площадь включает:
        - Площадь стрингеров
        - Эффективную площадь обшивки (с учётом редуцирования)
        
        Returns:
            float: Эффективная площадь в м²
            
        Updates:
            self.reduced_area: Эффективная площадь
            
        Note:
            Требует предварительного расчёта effective_skin_width
            и установки skin_thickness
        """
        if self.skin_thickness is None:
            raise ValueError("Толщина обшивки не установлена")
        
        if self.effective_skin_width is None:
            # Если эффективная ширина не рассчитана, используем полную ширину
            if self.stringer_spacing is None:
                raise ValueError("Шаг стрингеров не установлен")
            self.effective_skin_width = self.stringer_spacing
        
        # Площадь обшивки (эффективная)
        skin_area = self.skin_thickness * self.effective_skin_width
        
        # Площадь стрингеров
        stringer_area = sum(
            stringer.area for stringer in self.stringers
            if stringer.area is not None
        )
        
        # Общая эффективная площадь
        self.reduced_area = skin_area + stringer_area
        
        return self.reduced_area
    
    def calculate_effective_inertia(self):
        """
        Расчёт эффективного момента инерции сечения панели.
        
        Учитывает:
        - Момент инерции обшивки относительно нейтральной оси
        - Момент инерции стрингеров относительно нейтральной оси
        - Площади элементов и их расстояния до нейтральной оси (теорема Штейнера)
        
        Returns:
            float: Эффективный момент инерции в м⁴
            
        Updates:
            self.reduced_inertia: Эффективный момент инерции
            
        Note:
            Требует предварительного расчёта эффективной площади
            и определения положения нейтральной оси
        """
        if self.reduced_area is None:
            # Если площадь не рассчитана, рассчитываем её
            self.calculate_effective_area()
        
        if self.skin_thickness is None or self.effective_skin_width is None:
            raise ValueError("Параметры обшивки не установлены")
        
        if self.box_height is None:
            self.calculate_box_height()
        
        # Определение нейтральной оси (упрощённо - по центру кессона)
        # Для точного расчёта нужно учитывать положение всех элементов
        neutral_axis_y = self.box_height / 2
        
        # Момент инерции обшивки
        # Обшивка как прямоугольник толщиной t и шириной b_eff
        skin_inertia = (
            self.skin_thickness * self.effective_skin_width**3 / 12
        )
        # Расстояние от центра обшивки до нейтральной оси
        skin_y = neutral_axis_y - self.skin_thickness / 2
        skin_area = self.skin_thickness * self.effective_skin_width
        # Момент инерции обшивки относительно нейтральной оси (теорема Штейнера)
        skin_inertia_total = skin_inertia + skin_area * skin_y**2
        
        # Момент инерции стрингеров
        stringer_inertia_total = 0.0
        for stringer in self.stringers:
            if stringer.inertia is None or stringer.area is None:
                continue
            
            # Собственный момент инерции стрингера
            stringer_inertia_own = stringer.inertia
            
            # Расстояние от центра стрингера до нейтральной оси
            # (упрощённо - стрингер у верхней обшивки)
            stringer_y = neutral_axis_y - self.skin_thickness - (
                stringer.web_height / 2 if hasattr(stringer, 'web_height') 
                and stringer.web_height else 0.01
            )
            
            # Момент инерции стрингера относительно нейтральной оси
            stringer_inertia_total += (
                stringer_inertia_own + stringer.area * stringer_y**2
            )
        
        # Общий эффективный момент инерции
        self.reduced_inertia = skin_inertia_total + stringer_inertia_total
        
        return self.reduced_inertia
    
    def get_geometry_summary(self):
        """
        Получение сводки геометрических параметров панели.
        
        Returns:
            dict: Словарь с геометрическими параметрами
        """
        if self.panel_width is None:
            self.calculate_panel_width()
        
        if self.box_height is None:
            self.calculate_box_height()
        
        return {
            'z_relative': self.z_relative,
            'z_absolute': self.aircraft.get_absolute_position(self.z_relative),
            'panel_width': self.panel_width,
            'box_height': self.box_height,
            'skin_thickness': self.skin_thickness,
            'stringer_spacing': self.stringer_spacing,
            'stringer_count': self.stringer_count,
            'effective_skin_width': self.effective_skin_width,
            'reduced_area': self.reduced_area,
            'reduced_inertia': self.reduced_inertia,
        }
    
    def __repr__(self):
        """Строковое представление объекта."""
        z_abs = (
            self.aircraft.get_absolute_position(self.z_relative)
            if self.aircraft else None
        )
        width_str = f"{self.panel_width:.3f}" if self.panel_width else "не рассчитана"
        return (
            f"Panel(z/L={self.z_relative}, z={z_abs:.3f} м, "
            f"width={width_str} м)"
        )
