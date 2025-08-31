# v2/notebook_utils.py
import sys
from pathlib import Path

def setup_paths():
    """Настройка путей для импорта из корня"""
    # Определяем корневую директорию
    current_dir = Path.cwd()
    if current_dir.name == 'v1':
        root_dir = current_dir.parent.parent
    else:
        root_dir = current_dir.parent
    
    sys.path.append(str(root_dir))
    return root_dir

# Настройка путей
ROOT_DIR = setup_paths()

# Импортируем config с полными путями
try:
    from config import *
    print(f"✅ Config успешно импортирован!")
        
except ImportError as e:
    print(f"❌ Ошибка импорта config: {e}")