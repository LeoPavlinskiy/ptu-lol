#!/usr/bin/env python3
"""
Простой тест для класса Panel
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel

def test_panel():
    """Тестирование основных методов класса Panel"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КЛАССА Panel")
    print("=" * 60)
    
    # Создание объектов
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    
    # Тест 1: Создание панели
    print("\n1. Создание панели:")
    panel = Panel(0.2, aircraft, material)
    print(f"   {panel}")
    print(f"   Положение: z/L = {panel.z_relative}")
    
    # Тест 2: Расчёт ширины панели
    print("\n2. Расчёт ширины панели:")
    width = panel.calculate_panel_width()
    print(f"   Ширина панели: {width:.3f} м")
    
    # Тест 3: Расчёт высоты кессона
    print("\n3. Расчёт высоты кессона:")
    height = panel.calculate_box_height()
    print(f"   Высота кессона: {height:.3f} м")
    
    # Тест 4: Установка параметров обшивки
    print("\n4. Установка параметров обшивки:")
    panel.skin_thickness = 0.003  # 3 мм
    panel.stringer_spacing = 0.15  # 15 см
    panel.effective_skin_width = 0.15  # начальное значение
    print(f"   Толщина обшивки: {panel.skin_thickness*1000:.1f} мм")
    print(f"   Шаг стрингеров: {panel.stringer_spacing*1000:.0f} мм")
    
    # Тест 5: Создание простого стрингера (заглушка)
    print("\n5. Добавление стрингеров:")
    
    # Создаём простой объект-заглушку для стрингера
    class SimpleStringer:
        def __init__(self):
            self.area = 0.0005  # 5 см²
            self.inertia = 1e-8  # м⁴
            self.web_height = 0.02  # 2 см
    
    stringer1 = SimpleStringer()
    stringer2 = SimpleStringer()
    panel.add_stringer(stringer1)
    panel.add_stringer(stringer2)
    print(f"   Добавлено стрингеров: {panel.stringer_count}")
    
    # Тест 6: Расчёт эффективной площади
    print("\n6. Расчёт эффективной площади:")
    try:
        area = panel.calculate_effective_area()
        print(f"   Эффективная площадь: {area*1e4:.2f} см²")
        print(f"   - Площадь обшивки: {panel.skin_thickness * panel.effective_skin_width * 1e4:.2f} см²")
        print(f"   - Площадь стрингеров: {sum(s.area for s in panel.stringers) * 1e4:.2f} см²")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 7: Расчёт эффективного момента инерции
    print("\n7. Расчёт эффективного момента инерции:")
    try:
        inertia = panel.calculate_effective_inertia()
        print(f"   Эффективный момент инерции: {inertia*1e8:.2f} см⁴")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 8: Сводка параметров
    print("\n8. Сводка геометрических параметров:")
    summary = panel.get_geometry_summary()
    for key, value in summary.items():
        if value is not None:
            if isinstance(value, float):
                if 'area' in key:
                    print(f"   {key}: {value*1e4:.2f} см²")
                elif 'inertia' in key:
                    print(f"   {key}: {value*1e8:.2f} см⁴")
                elif 'thickness' in key or 'width' in key or 'height' in key:
                    print(f"   {key}: {value*1000:.2f} мм")
                else:
                    print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
    
    # Тест 9: Панели для всех расчётных сечений
    print("\n9. Панели для всех расчётных сечений:")
    for z_rel in [0.2, 0.4, 0.6, 0.8]:
        p = Panel(z_rel, aircraft, material)
        p.calculate_panel_width()
        p.calculate_box_height()
        z_abs = aircraft.get_absolute_position(z_rel)
        print(f"   z/L = {z_rel}: z = {z_abs:.3f} м, "
              f"ширина = {p.panel_width:.3f} м, "
              f"высота = {p.box_height:.3f} м")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == '__main__':
    test_panel()

