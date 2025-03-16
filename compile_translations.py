#!/usr/bin/env python
"""
Скрипт для компиляции файлов переводов (.po -> .mo)
"""

import os
import subprocess
import glob

def compile_translations():
    """Компилирует все файлы переводов в директории translations."""
    print("Компиляция файлов переводов...")
    
    # Находим все .po файлы
    po_files = glob.glob('translations/*/LC_MESSAGES/messages.po')
    
    if not po_files:
        print("Файлы переводов не найдены.")
        return
    
    success_count = 0
    error_count = 0
    
    for po_file in po_files:
        mo_file = po_file.replace('.po', '.mo')
        directory = os.path.dirname(mo_file)
        
        # Создаем директорию, если она не существует
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        try:
            # Компилируем .po файл в .mo файл
            subprocess.run(['pybabel', 'compile', '-i', po_file, '-o', mo_file], check=True)
            print(f"✓ Скомпилирован: {po_file} -> {mo_file}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка компиляции {po_file}: {e}")
            error_count += 1
        except FileNotFoundError:
            print("✗ Ошибка: pybabel не найден. Установите Babel: pip install Babel")
            return
    
    print(f"\nГотово! Скомпилировано файлов: {success_count}, ошибок: {error_count}")

if __name__ == "__main__":
    compile_translations() 