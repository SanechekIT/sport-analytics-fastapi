import sys
import pip
import os
from pathlib import Path
import importlib

print("SPORT ANALYTICS API - ДИАГНОСТИКА")
print("=" * 60)

# Базовая информация
print("\n СИСТЕМНАЯ ИНФОРМАЦИЯ:")
print(f"Python: {sys.version}")
print(f"Pip: {pip.__version__}")
print(f"Текущая директория: {os.getcwd()}")

# Проверка версии Python
print("\n ПРОВЕРКА ВЕРСИИ PYTHON:")
if sys.version_info >= (3, 8):
    print(" Python 3.8+ (OK)")
else:
    print("⚠️  Рекомендуется Python 3.8 или выше")

# Проверка структуры проекта
print("\n СТРУКТУРА ПРОЕКТА:")
structure = {
    'api': 'API endpoints',
    'database': 'Database connection',
    'models': 'Data models',
    'repositories': 'Data repositories',
    'shemas': 'Pydantic schemas',
    'main.py': 'Main application',
    'config.py': 'Configuration',
    'auth.py': 'Authentication',
    'requirements.txt': 'Dependencies'
}

for item, description in structure.items():
    path = Path(item)
    if path.exists():
        if path.is_dir():
            print(f" {item}/ - {description}")
        else:
            print(f" {item} - {description}")
    else:
        print(f"❌ {item} - {description} (отсутствует)")

# Проверка зависимостей
print("\n ЗАВИСИМОСТИ:")
required_packages = [
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'pydantic',
    'databases',
    'alembic',
    'python-jose[cryptography]',
    'passlib[bcrypt]',
    'python-multipart'
]

installed = []
missing = []

for package in required_packages:
    # Очищаем имя пакета от [options]
    package_name = package.split('[')[0].replace('-', '_')
    try:
        importlib.import_module(package_name)
        print(f" {package}")
        installed.append(package)
    except ImportError:
        print(f" {package} (не установлен)")
        missing.append(package)

# Проверка импортов модулей проекта
print("\n🔌 ИМПОРТЫ МОДУЛЕЙ:")
modules_to_check = [
    'api.routes',
    'database.database',
    'models.workout',
    'repositories.workout_repository',
    'shemas.workout',
    'auth'
]

for module in modules_to_check:
    try:
        importlib.import_module(module)
        print(f" {module}")
    except ImportError as e:
        print(f" {module} (ошибка: {e})")

# Проверка конфигурации
print("\n⚙️  КОНФИГУРАЦИЯ:")
try:
    import config
    print(" config.py загружен")
    
    # Проверяем основные переменные
    config_vars = ['DATABASE_URL', 'SECRET_KEY', 'ALGORITHM']
    for var in config_vars:
        if hasattr(config, var):
            print(f"  {var}")
        else:
            print(f"  {var} (не найдена)")
except ImportError:
    print(" config.py не найден")

# Проверка базы данных
print("\n БАЗА ДАННЫХ:")
try:
    from database.database import engine
    print(" Database engine configured")
    
    # Проверяем наличие миграций
    if Path('alembic').exists() or Path('migrations').exists():
        print(" Миграции настроены")
    else:
        print(" Миграции не найдены")
except Exception as e:
    print(f" Ошибка подключения к БД: {e}")

# Финальный вердикт
print("\n" + "=" * 60)
print("📊 ИТОГОВАЯ ДИАГНОСТИКА:")

if missing:
    print(f"\n Отсутствуют зависимости ({len(missing)}):")
    for pkg in missing:
        print(f"   • {pkg}")
    print("\n Установите зависимости:")
    print("   pip install -r requirements.txt")
else:
    print("\n Все зависимости установлены!")

# Проверяем наличие main.py и возможность запуска
if Path('main.py').exists():
    print("\n ДЛЯ ЗАПУСКА:")
    print("   uvicorn main:app --reload")
    print("   или")
    print("   python main.py")

print("\n" + "=" * 60) 
