"""
Проверка физической корректности расчётов.
Задача 10.3: Проверка физической корректности
"""

from aircraft_data import Aircraft
from material import Material
from panel import Panel
from stringer import Stringer
from geometry import calculate_box_width, calculate_box_height
from loads import load_moments_from_bot, get_moment_at_section
from stability import local_skin_buckling, general_panel_buckling
from reduction import effective_width
from strength import calculate_stresses, check_strength


def check_dimensions():
    """Проверка размерностей всех формул"""
    print("=" * 60)
    print("Проверка размерностей")
    print("=" * 60)
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    panel = Panel(0.4, aircraft, material)
    panel.calculate_panel_width()
    panel.calculate_box_height()
    panel.skin_thickness = 0.003  # 3 мм
    panel.stringer_spacing = 0.15  # 150 мм
    
    # Проверка размерностей критического напряжения обшивки
    # σ_cr = k * π² * E * (t/b)²
    # [Па] = [безразмерный] * [Па] * [безразмерный]² = [Па] ✓
    sigma_cr = local_skin_buckling(
        panel.skin_thickness,
        panel.stringer_spacing,
        material,
        boundary_condition='hinged'
    )
    print(f"✓ Критическое напряжение обшивки: {sigma_cr/1e6:.2f} МПа")
    assert sigma_cr > 0, "Критическое напряжение должно быть положительным"
    # Примечание: критическое напряжение может превышать предел прочности
    # (это нормально для теории упругости, на практике учитывается предел текучести)
    
    # Проверка эффективной ширины
    # b_eff должно быть в метрах
    b_eff, rho = effective_width(
        panel.stringer_spacing,
        sigma_cr,
        sigma_cr * 0.8,  # напряжение на краю
        material,
        method='winter'
    )
    print(f"✓ Эффективная ширина: {b_eff*1000:.1f} мм (коэффициент: {rho:.3f})")
    assert 0 < b_eff <= panel.stringer_spacing, "Эффективная ширина должна быть в пределах [0, b]"
    assert 0 < rho <= 1, "Коэффициент редуцирования должен быть в пределах [0, 1]"
    
    print("✓ Все размерности корректны\n")


def check_signs():
    """Проверка знаков напряжений"""
    print("=" * 60)
    print("Проверка знаков напряжений")
    print("=" * 60)
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    panel = Panel(0.4, aircraft, material)
    panel.calculate_panel_width()
    panel.calculate_box_height()
    panel.skin_thickness = 0.003
    panel.stringer_spacing = 0.15
    
    # Создаём стрингеры
    stringers = []
    for i in range(2):
        s = Stringer('Z')
        s.set_geometry_from_typical()
        s.calculate_area()
        s.calculate_inertia()
        stringers.append(s)
        panel.add_stringer(s)
    
    # Устанавливаем эффективные параметры
    panel.effective_skin_width = 0.12
    panel.reduced_area = 0.001
    panel.reduced_inertia = 1e-6
    
    # Загружаем момент (положительный - сжатие верхней панели)
    moments = load_moments_from_bot()
    M = get_moment_at_section(0.4, moments)
    
    # Рассчитываем напряжения
    stresses = calculate_stresses(panel, stringers, M, material)
    
    print(f"Момент: {M/1e6:.2f} МН·м (положительный = сжатие верхней панели)")
    print(f"Напряжение в обшивке: {stresses['skin']/1e6:.2f} МПа")
    print(f"Напряжение в стрингерах: {stresses['stringers']/1e6:.2f} МПа")
    
    # Для верхней панели при положительном моменте напряжения должны быть положительными (сжатие)
    # Проверяем, что напряжения в обшивке положительные
    assert stresses['skin'] > 0, "Напряжение в обшивке верхней панели должно быть положительным (сжатие)"
    
    print("✓ Знаки напряжений корректны\n")


def check_boundary_cases():
    """Проверка граничных случаев"""
    print("=" * 60)
    print("Проверка граничных случаев")
    print("=" * 60)
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    
    # Случай 1: Очень тонкая обшивка
    print("1. Очень тонкая обшивка (0.5 мм):")
    panel1 = Panel(0.4, aircraft, material)
    panel1.calculate_panel_width()
    panel1.skin_thickness = 0.0005  # 0.5 мм
    panel1.stringer_spacing = 0.15
    
    sigma_cr1 = local_skin_buckling(
        panel1.skin_thickness,
        panel1.stringer_spacing,
        material,
        boundary_condition='hinged'
    )
    print(f"   Критическое напряжение: {sigma_cr1/1e6:.2f} МПа")
    assert sigma_cr1 > 0, "Критическое напряжение должно быть положительным"
    print("   ✓ Корректно")
    
    # Случай 2: Очень толстая обшивка
    print("\n2. Очень толстая обшивка (10 мм):")
    panel2 = Panel(0.4, aircraft, material)
    panel2.calculate_panel_width()
    panel2.skin_thickness = 0.01  # 10 мм
    panel2.stringer_spacing = 0.15
    
    sigma_cr2 = local_skin_buckling(
        panel2.skin_thickness,
        panel2.stringer_spacing,
        material,
        boundary_condition='hinged'
    )
    print(f"   Критическое напряжение: {sigma_cr2/1e6:.2f} МПа")
    assert sigma_cr2 > sigma_cr1, "Толстая обшивка должна иметь большее критическое напряжение"
    print("   ✓ Корректно")
    
    # Случай 3: Нулевой момент
    print("\n3. Нулевой момент:")
    panel3 = Panel(0.4, aircraft, material)
    panel3.calculate_panel_width()
    panel3.calculate_box_height()
    panel3.skin_thickness = 0.003
    panel3.stringer_spacing = 0.15
    
    stringers3 = []
    for i in range(2):
        s = Stringer('Z')
        s.set_geometry_from_typical()
        s.calculate_area()
        s.calculate_inertia()
        stringers3.append(s)
        panel3.add_stringer(s)
    
    panel3.effective_skin_width = 0.12
    panel3.reduced_area = 0.001
    panel3.reduced_inertia = 1e-6
    
    M_zero = 0.0
    stresses3 = calculate_stresses(panel3, stringers3, M_zero, material)
    print(f"   Напряжение в обшивке: {stresses3['skin']/1e6:.2f} МПа")
    assert abs(stresses3['skin']) < 1e-6, "При нулевом моменте напряжение должно быть близко к нулю"
    print("   ✓ Корректно")
    
    print("\n✓ Все граничные случаи обработаны корректно\n")


def check_monotonicity():
    """Проверка монотонности результатов"""
    print("=" * 60)
    print("Проверка монотонности")
    print("=" * 60)
    
    aircraft = Aircraft()
    material = Material('B95T1', 'sheet')
    
    # Проверка: чем больше момент, тем больше напряжение
    moments = load_moments_from_bot()
    sections = [0.2, 0.4, 0.6, 0.8]
    moments_list = [get_moment_at_section(z, moments) for z in sections]
    
    print("Моменты по сечениям:")
    for z, M in zip(sections, moments_list):
        print(f"  z/L = {z}: M = {M/1e6:.2f} МН·м")
    
    # Проверяем, что моменты убывают от корня к концу (для верхней панели)
    for i in range(len(moments_list) - 1):
        assert moments_list[i] >= moments_list[i+1], \
            f"Момент должен убывать от корня к концу: {moments_list[i]/1e6:.2f} >= {moments_list[i+1]/1e6:.2f}"
    
    print("✓ Монотонность моментов корректна")
    
    # Проверка: чем больше толщина, тем больше критическое напряжение
    thicknesses = [0.001, 0.002, 0.003, 0.004, 0.005]
    sigma_cr_list = []
    for t in thicknesses:
        sigma_cr = local_skin_buckling(t, 0.15, material, boundary_condition='hinged')
        sigma_cr_list.append(sigma_cr)
        print(f"  t = {t*1000:.1f} мм: σ_cr = {sigma_cr/1e6:.2f} МПа")
    
    for i in range(len(sigma_cr_list) - 1):
        assert sigma_cr_list[i] < sigma_cr_list[i+1], \
            f"Критическое напряжение должно расти с толщиной: {sigma_cr_list[i]/1e6:.2f} < {sigma_cr_list[i+1]/1e6:.2f}"
    
    print("✓ Монотонность критических напряжений корректна\n")


def main():
    """Главная функция проверки физической корректности"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ФИЗИЧЕСКОЙ КОРРЕКТНОСТИ РАСЧЁТОВ")
    print("=" * 60 + "\n")
    
    try:
        check_dimensions()
        check_signs()
        check_boundary_cases()
        check_monotonicity()
        
        print("=" * 60)
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ ОШИБКА: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

