#!/usr/bin/env python3
"""
Скрипт для извлечения данных из эпюр изгибающих моментов и поперечных сил.
Требует ручного ввода значений с графиков.
"""

import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Параметры
L = 17.16  # полуразмах крыла в метрах
sections = [0.2, 0.4, 0.6, 0.8]  # относительные положения сечений

def show_image(image_path):
    """Показать изображение для анализа"""
    img = Image.open(image_path)
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')
    plt.title(f'График: {os.path.basename(image_path)}')
    plt.tight_layout()
    plt.show()
    return img

def extract_moments():
    """Извлечение изгибающих моментов из первого графика"""
    print("=" * 60)
    print("ИЗВЛЕЧЕНИЕ ИЗГИБАЮЩИХ МОМЕНТОВ")
    print("=" * 60)
    print(f"\nПолуразмах крыла L = {L} м")
    print("\nНеобходимо определить значения изгибающих моментов для сечений:")
    
    moments = {}
    for z_rel in sections:
        z_abs = z_rel * L
        print(f"\nСечение z/L = {z_rel} (z = {z_abs:.3f} м)")
        print("Откройте график и определите значение изгибающего момента M (Н·м)")
        try:
            M = float(input("Введите M (Н·м): "))
            moments[z_rel] = {'z': z_abs, 'M': M}
        except ValueError:
            print("Ошибка: введите числовое значение")
            M = float(input("Введите M (Н·м): "))
            moments[z_rel] = {'z': z_abs, 'M': M}
    
    return moments

def extract_forces():
    """Извлечение поперечных сил из второго графика (опционально)"""
    print("\n" + "=" * 60)
    print("ИЗВЛЕЧЕНИЕ ПОПЕРЕЧНЫХ СИЛ (опционально)")
    print("=" * 60)
    
    response = input("\nЕсть ли данные о поперечных силах? (y/n): ")
    if response.lower() != 'y':
        return None
    
    forces = {}
    for z_rel in sections:
        z_abs = z_rel * L
        print(f"\nСечение z/L = {z_rel} (z = {z_abs:.3f} м)")
        try:
            Q = float(input("Введите Q (Н): "))
            forces[z_rel] = {'z': z_abs, 'Q': Q}
        except ValueError:
            print("Ошибка: введите числовое значение")
            Q = float(input("Введите Q (Н): "))
            forces[z_rel] = {'z': z_abs, 'Q': Q}
    
    return forces

def save_moments(moments, filepath):
    """Сохранение изгибающих моментов в файл"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Изгибающие моменты из бота Чедрика (Н·м)\n")
        f.write("# Сечение z/L | z (м) | M (Н·м)\n")
        for z_rel in sorted(moments.keys()):
            data = moments[z_rel]
            f.write(f"{z_rel} | {data['z']:.3f} | {data['M']:.2e}\n")
    print(f"\nДанные сохранены в {filepath}")

def save_overloads(filepath):
    """Сохранение перегрузок в файл"""
    # Значения из bot.md
    ny_max = 3.75
    ny_min = -1.5
    safety_factor = 1.5
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Расчётные перегрузки\n")
        f.write(f"ny_max = {ny_max}\n")
        f.write(f"ny_min = {ny_min}\n")
        f.write(f"safety_factor = {safety_factor}\n")
    print(f"\nПерегрузки сохранены в {filepath}")

def main():
    # Показать изображения
    image1_path = 'data/bot-stuff/photo_2025-12-04 17.57.59.jpeg'
    image2_path = 'data/bot-stuff/photo_2025-12-04 17.58.00.jpeg'
    
    print("Открываю изображения для анализа...")
    print(f"Изображение 1: {image1_path}")
    print(f"Изображение 2: {image2_path}")
    
    # Показать первое изображение
    if os.path.exists(image1_path):
        show_image(image1_path)
    
    # Извлечь моменты
    moments = extract_moments()
    
    # Показать второе изображение
    if os.path.exists(image2_path):
        show_image(image2_path)
    
    # Извлечь силы (опционально)
    forces = extract_forces()
    
    # Сохранить данные
    save_moments(moments, 'data/bot-moments.txt')
    save_overloads('data/bot-overloads.txt')
    
    print("\n" + "=" * 60)
    print("ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    print("\nИзвлечённые значения:")
    for z_rel in sorted(moments.keys()):
        data = moments[z_rel]
        print(f"  z/L = {z_rel}: M = {data['M']:.2e} Н·м")

if __name__ == '__main__':
    main()

