#!/usr/bin/env python3
# install.py — скрипт развёртывания структуры проекта

import os
from pathlib import Path

# Определяем структуру папок и файлов
PROJECT_ROOT = Path(__file__).parent.resolve()

DIR_STRUCTURE = [
    "Backup",
    "Plugins",
    "Logs",
    "Data/themes",
    "Data/locales",
]

FILES_TEMPLATES = {
    "requirements.txt": """\
PyQt6>=6.5.0
""",
    "backup_engine.py": """\
# Модуль движка резервного копирования
""",
    "app_definitions.py": """\
# Описание приложений и загрузка плагинов
""",
    "backup_console.py": """\
# Консольный интерфейс
""",
    "backup_app_gui.py": """\
# Графический интерфейс на PyQt6
""",
    "run_console.bat" if os.name == "nt" else "run_console.sh": """\
# Скрипт запуска консольной версии
python backup_console.py %*""",
    "run_gui.bat" if os.name == "nt" else "run_gui.sh": """\
# Скрипт запуска GUI-версии
python backup_app_gui.py""",
    "README.md": """\
# BackupApp

Инструкция по установке и запуску проекта.
"""
}

def create_dirs():
    for rel in DIR_STRUCTURE:
        path = PROJECT_ROOT / rel
        path.mkdir(parents=True, exist_ok=True)
        print(f"Создана папка: {path}")

def create_files():
    for filename, content in FILES_TEMPLATES.items():
        path = PROJECT_ROOT / filename
        # Не перезаписывать, если файл уже существует
        if path.exists():
            print(f"Файл существует: {path}")
            continue
        path.write_text(content, encoding="utf-8")
        # На Unix-образных системах сделать скрипты исполняемыми
        if path.suffix in {".sh"}:
            path.chmod(0o755)
        print(f"Создан файл: {path}")

def main():
    print("=== Развёртывание структуры проекта ===")
    create_dirs()
    create_files()
    print("=== Установка завершена ===")

if __name__ == "__main__":
    main()
