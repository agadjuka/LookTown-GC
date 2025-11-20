#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска эдитора промптов и инструментов.
"""

import os
import sys
from pathlib import Path

# Переходим в папку скрипта
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Устанавливаем PYTHONPATH
os.environ["PYTHONPATH"] = str(script_dir)

# Импортируем и запускаем Flask приложение
from editor.app import app

if __name__ == "__main__":
    print("=" * 80)
    print("Эдитор промптов и инструментов")
    print("=" * 80)
    print()
    print("Эдитор будет доступен по адресу: http://localhost:5000")
    print("Нажмите Ctrl+C для остановки")
    print()
    
    app.run(host="localhost", port=5000, debug=True)

