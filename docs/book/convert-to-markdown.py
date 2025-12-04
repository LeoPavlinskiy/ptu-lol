#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации DJVU книги в Markdown
"""

import re
import os
from pathlib import Path

def clean_text(text):
    """Очистка текста от лишних символов"""
    # Удаляем символы перевода страницы
    text = text.replace('\x0c', '\n\n---\n\n')
    # Удаляем множественные пробелы
    text = re.sub(r' +', ' ', text)
    # Удаляем множественные переносы строк
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def detect_structure(line):
    """Определение типа строки (заголовок, параграф и т.д.)"""
    line = line.strip()
    
    # Пустая строка
    if not line:
        return 'empty'
    
    # Заголовки глав
    if re.match(r'^Глава [IVX]+\.', line):
        return 'chapter'
    
    # Параграфы (разные варианты написания)
    if re.match(r'^§\s*\d+\.', line) or re.match(r'^§\s*\d+\s', line):
        return 'section'
    
    # Номера страниц
    if re.match(r'^\d+$', line) and len(line) <= 4:
        return 'page_number'
    
    # Оглавление
    if 'ОГЛАВЛЕНИЕ' in line:
        return 'toc'
    
    return 'text'

def process_text_to_markdown(text_file, output_file, images_dir):
    """Обработка текста и создание Markdown файла"""
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Разбиваем на страницы по символу перевода страницы
    pages = content.split('\x0c')
    
    markdown_lines = []
    in_toc = False
    
    # Добавляем заголовок книги
    markdown_lines.append("# Устойчивость деформируемых систем\n\n")
    markdown_lines.append("**А. С. Вольмир**\n\n")
    markdown_lines.append("Издание второе, переработанное и дополненное\n\n")
    markdown_lines.append("Москва, 1967\n\n")
    markdown_lines.append("---\n\n")
    
    # Обрабатываем каждую страницу
    for page_num, page_text in enumerate(pages, start=1):
        page_lines = page_text.strip().split('\n')
        
        # Вставляем изображение страницы в начале
        img_path = f"{images_dir}/page-{page_num:04d}.tiff"
        if os.path.exists(img_path):
            markdown_lines.append(f"\n![Страница {page_num}]({img_path})\n\n")
        
        # Обрабатываем строки страницы
        for line in page_lines:
            line = line.strip()
            if not line:
                continue
            
            line_type = detect_structure(line)
            
            if line_type == 'toc':
                in_toc = True
                if "## Оглавление" not in '\n'.join(markdown_lines[-10:]):
                    markdown_lines.append("## Оглавление\n\n")
                continue
            
            if line_type == 'chapter':
                in_toc = False
                markdown_lines.append(f"\n# {line}\n\n")
                continue
            
            if line_type == 'section':
                in_toc = False
                markdown_lines.append(f"\n## {line}\n\n")
                continue
            
            if line_type == 'page_number':
                # Пропускаем номера страниц в тексте
                continue
            
            if line_type == 'text' and line:
                # Обычный текст
                if not in_toc:
                    markdown_lines.append(f"{line}\n\n")
                else:
                    # В оглавлении сохраняем как есть
                    markdown_lines.append(f"{line}\n")
                continue
    
    # Записываем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(markdown_lines)
    
    print(f"Markdown файл создан: {output_file}")
    print(f"Обработано страниц: {len(pages)}")

if __name__ == "__main__":
    text_file = "book-text-raw.txt"
    output_file = "book.md"
    images_dir = "book-images"
    
    process_text_to_markdown(text_file, output_file, images_dir)

