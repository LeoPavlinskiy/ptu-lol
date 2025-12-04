"""
Класс стрингера с геометрией.
Поддерживает различные типы стрингеров: Z, C (швеллер), T (тавровый), L (уголковый).
"""

import math


class Stringer:
    """
    Класс для представления стрингера с геометрическими параметрами.
    
    Поддерживает различные типы стрингеров и расчёт их геометрических
    характеристик: площади, момента инерции, эффективной площади с обшивкой.
    """
    
    # Поддерживаемые типы стрингеров
    SUPPORTED_TYPES = ['Z', 'C', 'T', 'L']
    
    def __init__(self, stringer_type='Z'):
        """
        Инициализация стрингера.
        
        Args:
            stringer_type: Тип стрингера - 'Z', 'C', 'T' или 'L'
            
        Raises:
            ValueError: Если указан неподдерживаемый тип стрингера
        """
        if stringer_type not in self.SUPPORTED_TYPES:
            raise ValueError(
                f"Неподдерживаемый тип стрингера: {stringer_type}. "
                f"Доступные: {self.SUPPORTED_TYPES}"
            )
        
        self.type = stringer_type  # 'Z', 'C', 'T', 'L'
        
        # Геометрические параметры (в метрах)
        self.web_height = None  # высота стенки
        self.flange_width = None  # ширина полки
        self.web_thickness = None  # толщина стенки
        self.flange_thickness = None  # толщина полки
        self.radius = None  # радиус закругления (для Z и C)
        
        # Расчётные параметры
        self.area = None  # площадь поперечного сечения
        self.inertia = None  # момент инерции относительно собственной оси
        self.effective_area = None  # приведённая площадь с обшивкой
        self.centroid_y = None  # координата центра тяжести по Y
    
    def set_geometry_from_typical(self):
        """
        Установка типовых размеров для Boeing 737-800.
        
        Типовые размеры стрингеров для панелей крыла:
        - Z-образный: наиболее распространённый тип
        - Высота стенки: 20-30 мм
        - Ширина полки: 15-25 мм
        - Толщины: 1.5-3 мм
        """
        if self.type == 'Z':
            # Типовые размеры Z-стрингера для Boeing 737-800
            self.web_height = 0.025  # 25 мм
            self.flange_width = 0.020  # 20 мм
            self.web_thickness = 0.002  # 2 мм
            self.flange_thickness = 0.002  # 2 мм
            self.radius = 0.003  # 3 мм (радиус закругления)
        elif self.type == 'C':
            # Типовые размеры швеллера
            self.web_height = 0.025  # 25 мм
            self.flange_width = 0.020  # 20 мм
            self.web_thickness = 0.002  # 2 мм
            self.flange_thickness = 0.002  # 2 мм
            self.radius = 0.003  # 3 мм
        elif self.type == 'T':
            # Типовые размеры таврового стрингера
            self.web_height = 0.020  # 20 мм
            self.flange_width = 0.025  # 25 мм
            self.web_thickness = 0.002  # 2 мм
            self.flange_thickness = 0.002  # 2 мм
            self.radius = 0.002  # 2 мм
        elif self.type == 'L':
            # Типовые размеры уголкового стрингера
            self.web_height = 0.020  # 20 мм
            self.flange_width = 0.020  # 20 мм
            self.web_thickness = 0.002  # 2 мм
            self.flange_thickness = 0.002  # 2 мм
            self.radius = 0.002  # 2 мм
    
    def calculate_area(self):
        """
        Расчёт площади поперечного сечения стрингера.
        
        Учитывает геометрию в зависимости от типа стрингера.
        Закругления учитываются упрощённо.
        
        Returns:
            float: Площадь поперечного сечения в м²
            
        Updates:
            self.area: Площадь сечения
            
        Raises:
            ValueError: Если геометрические параметры не установлены
        """
        if (self.web_height is None or self.flange_width is None or
            self.web_thickness is None or self.flange_thickness is None):
            raise ValueError("Геометрические параметры стрингера не установлены")
        
        if self.type == 'Z':
            # Z-образный стрингер: две полки + стенка
            # Упрощённо: без учёта закруглений
            area = (
                2 * self.flange_width * self.flange_thickness +  # две полки
                self.web_height * self.web_thickness  # стенка
            )
        elif self.type == 'C':
            # Швеллер: две полки + стенка
            area = (
                2 * self.flange_width * self.flange_thickness +  # две полки
                self.web_height * self.web_thickness  # стенка
            )
        elif self.type == 'T':
            # Тавровый: одна полка + стенка
            area = (
                self.flange_width * self.flange_thickness +  # полка
                self.web_height * self.web_thickness  # стенка
            )
        elif self.type == 'L':
            # Уголковый: две полки (без стенки)
            area = (
                self.web_height * self.web_thickness +  # вертикальная полка
                self.flange_width * self.flange_thickness  # горизонтальная полка
            )
        
        # Вычитаем площадь закруглений (упрощённо)
        if self.radius is not None:
            # Приблизительно: площадь закругления ≈ π * r² / 4 для каждого угла
            corners = 2 if self.type in ['T', 'L'] else 4
            corner_area = corners * math.pi * self.radius**2 / 4
            area -= corner_area
        
        self.area = max(area, 1e-6)  # Минимальная площадь для избежания нуля
        return self.area
    
    def calculate_inertia(self):
        """
        Расчёт момента инерции относительно собственной оси (горизонтальной).
        
        Использует теорему о параллельных осях для составных сечений.
        Ось проходит через центр тяжести сечения.
        
        Returns:
            float: Момент инерции в м⁴
            
        Updates:
            self.inertia: Момент инерции
            self.centroid_y: Координата центра тяжести по Y
            
        Raises:
            ValueError: Если геометрические параметры не установлены
        """
        if self.area is None:
            self.calculate_area()
        
        if (self.web_height is None or self.flange_width is None or
            self.web_thickness is None or self.flange_thickness is None):
            raise ValueError("Геометрические параметры стрингера не установлены")
        
        # Определение центра тяжести (координата Y от нижнего края)
        # Упрощённый расчёт для каждого типа
        
        if self.type == 'Z' or self.type == 'C':
            # Для Z и C: центр тяжести примерно посередине высоты
            # Более точно: учитываем полки
            total_height = self.web_height + 2 * self.flange_thickness
            # Статический момент относительно нижнего края
            S_y = (
                self.flange_width * self.flange_thickness * (total_height - self.flange_thickness / 2) +  # верхняя полка
                self.web_height * self.web_thickness * (self.web_height / 2 + self.flange_thickness) +  # стенка
                self.flange_width * self.flange_thickness * (self.flange_thickness / 2)  # нижняя полка
            )
            self.centroid_y = S_y / self.area
            
            # Момент инерции относительно центра тяжести
            # Верхняя полка
            I_top = (
                self.flange_width * self.flange_thickness**3 / 12 +
                self.flange_width * self.flange_thickness * 
                (total_height - self.flange_thickness / 2 - self.centroid_y)**2
            )
            # Стенка
            I_web = (
                self.web_thickness * self.web_height**3 / 12 +
                self.web_height * self.web_thickness * 
                (self.web_height / 2 + self.flange_thickness - self.centroid_y)**2
            )
            # Нижняя полка
            I_bottom = (
                self.flange_width * self.flange_thickness**3 / 12 +
                self.flange_width * self.flange_thickness * 
                (self.flange_thickness / 2 - self.centroid_y)**2
            )
            self.inertia = I_top + I_web + I_bottom
            
        elif self.type == 'T':
            # Тавровый: полка сверху, стенка снизу
            total_height = self.web_height + self.flange_thickness
            # Центр тяжести
            S_y = (
                self.flange_width * self.flange_thickness * (total_height - self.flange_thickness / 2) +
                self.web_height * self.web_thickness * (self.web_height / 2)
            )
            self.centroid_y = S_y / self.area
            
            # Момент инерции
            I_flange = (
                self.flange_width * self.flange_thickness**3 / 12 +
                self.flange_width * self.flange_thickness * 
                (total_height - self.flange_thickness / 2 - self.centroid_y)**2
            )
            I_web = (
                self.web_thickness * self.web_height**3 / 12 +
                self.web_height * self.web_thickness * 
                (self.web_height / 2 - self.centroid_y)**2
            )
            self.inertia = I_flange + I_web
            
        elif self.type == 'L':
            # Уголковый: две полки под углом 90°
            # Упрощённо: считаем как две прямоугольные полки
            # Центр тяжести
            h_eff = max(self.web_height, self.flange_width)
            S_y = (
                self.web_height * self.web_thickness * (self.web_height / 2) +
                self.flange_width * self.flange_thickness * (h_eff - self.flange_thickness / 2)
            )
            self.centroid_y = S_y / self.area
            
            # Момент инерции
            I_vertical = (
                self.web_thickness * self.web_height**3 / 12 +
                self.web_height * self.web_thickness * 
                (self.web_height / 2 - self.centroid_y)**2
            )
            I_horizontal = (
                self.flange_thickness * self.flange_width**3 / 12 +
                self.flange_width * self.flange_thickness * 
                (h_eff - self.flange_thickness / 2 - self.centroid_y)**2
            )
            self.inertia = I_vertical + I_horizontal
        
        return self.inertia
    
    def calculate_effective_area(self, skin_thickness, effective_width):
        """
        Расчёт приведённой площади стрингера с обшивкой.
        
        Учитывает эффективную ширину обшивки, работающей совместно
        со стрингером (метод эффективной ширины).
        
        Args:
            skin_thickness: Толщина обшивки в метрах
            effective_width: Эффективная ширина обшивки в метрах
            
        Returns:
            float: Приведённая площадь в м²
            
        Updates:
            self.effective_area: Приведённая площадь
        """
        if self.area is None:
            self.calculate_area()
        
        # Площадь эффективной обшивки, работающей со стрингером
        skin_area = skin_thickness * effective_width
        
        # Приведённая площадь = площадь стрингера + эффективная площадь обшивки
        self.effective_area = self.area + skin_area
        
        return self.effective_area
    
    def __repr__(self):
        """Строковое представление объекта."""
        area_str = f"{self.area*1e4:.2f} см²" if self.area else "не рассчитана"
        return (
            f"Stringer(type='{self.type}', area={area_str})"
        )
