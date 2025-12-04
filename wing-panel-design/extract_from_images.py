#!/usr/bin/env python3
"""
Скрипт для автоматического извлечения данных из графиков.
Требует установки: pip install pillow numpy opencv-python
"""

import sys
import os

# Проверка зависимостей
try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Ошибка: требуется установить зависимости:")
    print("  pip install pillow numpy")
    print("\nИспользуйте extract_data_simple.py для ручного ввода")
    sys.exit(1)

L = 17.16  # полуразмах крыла в метрах
sections = [0.2, 0.4, 0.6, 0.8]

def extract_moments_from_image(image_path):
    """
    Попытка автоматического извлечения моментов из графика.
    Требует ручной калибровки осей.
    """
    print(f"Анализ изображения: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Файл не найден: {image_path}")
        return None
    
    img = Image.open(image_path)
    print(f"Размер изображения: {img.size}")
    print("\nДля автоматического извлечения требуется:")
    print("1. Определить масштаб осей (пиксели -> метры/Н·м)")
    print("2. Определить положение начала координат")
    print("3. Определить положение кривой")
    print("\nРекомендуется использовать extract_data_simple.py для ручного ввода")
    
    return None

if __name__ == '__main__':
    image_path = 'data/bot-stuff/photo_2025-12-04 17.57.59.jpeg'
    
    # Попытка автоматического извлечения
    moments = extract_moments_from_image(image_path)
    
    if moments is None:
        print("\n" + "=" * 60)
        print("Используйте extract_data_simple.py для ручного ввода значений")
        print("=" * 60)

