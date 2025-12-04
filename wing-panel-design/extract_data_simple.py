#!/usr/bin/env python3
"""
Простой скрипт для извлечения данных из эпюр.
Откройте изображения и введите значения вручную.
"""

L = 17.16  # полуразмах крыла в метрах
sections = [0.2, 0.4, 0.6, 0.8]

print("=" * 60)
print("ИЗВЛЕЧЕНИЕ ДАННЫХ ИЗ ЭПЮР")
print("=" * 60)
print(f"\nПолуразмах крыла L = {L} м")
print("\nОткройте файлы:")
print("  1. data/bot-stuff/photo_2025-12-04 17.57.59.jpeg (изгибающие моменты)")
print("  2. data/bot-stuff/photo_2025-12-04 17.58.00.jpeg (поперечные силы)")
print("\nОпределите значения для сечений:\n")

moments = {}
for z_rel in sections:
    z_abs = z_rel * L
    print(f"Сечение z/L = {z_rel} (z = {z_abs:.3f} м)")
    M = float(input("  Изгибающий момент M (Н·м): "))
    moments[z_rel] = {'z': z_abs, 'M': M}

# Сохранение моментов
with open('data/bot-moments.txt', 'w', encoding='utf-8') as f:
    f.write("# Изгибающие моменты из бота Чедрика (Н·м)\n")
    f.write("# Сечение z/L | z (м) | M (Н·м)\n")
    for z_rel in sorted(moments.keys()):
        data = moments[z_rel]
        f.write(f"{z_rel} | {data['z']:.3f} | {data['M']:.2e}\n")

# Сохранение перегрузок
with open('data/bot-overloads.txt', 'w', encoding='utf-8') as f:
    f.write("# Расчётные перегрузки\n")
    f.write("ny_max = 3.75\n")
    f.write("ny_min = -1.5\n")
    f.write("safety_factor = 1.5\n")

print("\n" + "=" * 60)
print("ДАННЫЕ СОХРАНЕНЫ")
print("=" * 60)
print("\nФайлы созданы:")
print("  - data/bot-moments.txt")
print("  - data/bot-overloads.txt")

