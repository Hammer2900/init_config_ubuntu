#!/bin/bash

# CLI-приложение (Bash), создающее структуру временной папки рядом с указанным файлом или директорией.
# Папка будет иметь случайное имя с суффиксом '_project_tmp' и содержать:
# - __init__.py (пустой)
# - main.py (содержит '# python')
# - help.txt (содержит '# txt')

# Проверка наличия аргумента
if [ -z "$1" ]; then
  echo "Ошибка: Укажите путь к целевому файлу или директории."
  echo "Использование: $0 <target_path>"
  exit 1
fi

TARGET_PATH="$1"

# Получаем абсолютный путь
# Используем realpath, если доступен (стандартно в GNU coreutils)
if command -v realpath &> /dev/null; then
    RESOLVED_PATH=$(realpath "$TARGET_PATH")
    if [ $? -ne 0 ]; then
        echo "Ошибка: Не удалось определить путь для '$TARGET_PATH'"
        exit 1
    fi
else
    # Простая попытка для случаев без realpath (менее надежно)
    if [ -d "$TARGET_PATH" ]; then
        RESOLVED_PATH=$(cd "$TARGET_PATH"; pwd)
    elif [ -f "$TARGET_PATH" ]; then
        RESOLVED_PATH=$(cd "$(dirname "$TARGET_PATH")"; pwd)/$(basename "$TARGET_PATH")
    else
        echo "Ошибка: Путь '$TARGET_PATH' не существует или не является файлом/директорией."
        exit 1
    fi
fi


# Определяем базовую директорию
if [ -d "$RESOLVED_PATH" ]; then
  BASE_DIR="$RESOLVED_PATH"
else
  BASE_DIR=$(dirname "$RESOLVED_PATH")
fi

# Генерируем случайное имя
# Используем /dev/urandom для лучшей случайности, если доступен
if [ -e /dev/urandom ]; then
    RAND_PART=$(head /dev/urandom | tr -dc 'a-z0-9' | head -c 10)
else
    # Менее надежный fallback с использованием $RANDOM (если /dev/urandom недоступен)
    RAND_PART=$(echo "$RANDOM$RANDOM$RANDOM" | md5sum | head -c 10) # Пример fallback
fi
RAND_NAME="${RAND_PART}_project_tmp"
PROJECT_DIR="$BASE_DIR/$RAND_NAME"

# Создаем директорию проекта
if ! mkdir "$PROJECT_DIR"; then
    echo "Ошибка: Не удалось создать директорию '$PROJECT_DIR'"
    exit 1
fi

# Создаем файлы
touch "$PROJECT_DIR/__init__.py"
echo '# python' > "$PROJECT_DIR/main.py"
echo '# txt' > "$PROJECT_DIR/help.txt"

# Выводим информацию
echo ""
echo "✅ Создана структура проекта:"
echo "📁 ${PROJECT_DIR}"
echo "├── 🐍 ${PROJECT_DIR}/__init__.py"
echo "├── 🐍 ${PROJECT_DIR}/main.py"
echo "└── 📄 ${PROJECT_DIR}/help.txt"
echo ""

exit 0
