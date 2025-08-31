from pathlib import Path

# Автоматическое определение корневой директории
ROOT_DIR = Path(__file__).parent.absolute()

# Пути к данным
DATA_DIR = ROOT_DIR / 'data'

# 📁 Файлы данных (теперь полные пути)
BMW_PARSED = DATA_DIR / 'bmw_parsed.csv'
BMW_PREPROCESSED = DATA_DIR / 'bmw_preprocessed.csv'
BMW_ENCODED = DATA_DIR / 'bmw_preprocessed.csv'

# ✅ Функция для проверки существования файлов
def check_paths():
    """Проверяет существование файлов и выводит информацию"""
    paths = {
        'CARS_CSV': BMW_PARSED,
        'BMW_DATA_CSV': BMW_PREPROCESSED, 
        'BMW_PARSED': BMW_PARSED
    }
    
    for name, path in paths.items():
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (не найден)")
    
    return paths

# Автоматическая проверка при импорте
print("📁 Проверка путей в config.py:")
_ = check_paths()