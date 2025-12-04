"""
Тест главного модуля main.py
Проверяет корректность работы основных функций.
"""

import sys
from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from geometry import calculate_box_width, calculate_box_height
from loads import load_moments_from_bot, get_moment_at_section
from main import preliminary_panel_design


def test_preliminary_design():
    """Тест предварительного подбора параметров панели"""
    print("Тест предварительного подбора параметров панели:")
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    panel = Panel(0.4, aircraft, material)
    panel.calculate_panel_width()
    panel.calculate_box_height()
    
    moments = load_moments_from_bot()
    M = get_moment_at_section(0.4, moments)
    
    panel, stringers = preliminary_panel_design(panel, M, material)
    
    print(f"   ✓ Толщина обшивки: {panel.skin_thickness*1000:.2f} мм")
    print(f"   ✓ Количество стрингеров: {panel.stringer_count}")
    print(f"   ✓ Шаг стрингеров: {panel.stringer_spacing*1000:.1f} мм")
    print(f"   ✓ Количество созданных стрингеров: {len(stringers)}")
    
    assert panel.skin_thickness is not None
    assert panel.stringer_count is not None
    assert panel.stringer_spacing is not None
    assert len(stringers) == panel.stringer_count
    
    print("   ✓ Тест пройден\n")


def test_imports():
    """Тест импортов"""
    print("Тест импортов:")
    try:
        from main import main, preliminary_panel_design
        from output import print_results, output_results
        print("   ✓ Все импорты успешны\n")
    except ImportError as e:
        print(f"   ✗ Ошибка импорта: {e}\n")
        raise


if __name__ == '__main__':
    print("=" * 60)
    print("Тестирование main.py")
    print("=" * 60)
    
    try:
        test_imports()
        test_preliminary_design()
        
        print("=" * 60)
        print("Все тесты пройдены успешно!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

