#!/bin/bash

# Название программы из аргумента
APP=$1
BUILD_DIR="$HOME/build"
DOWNLOAD_DIR="$BUILD_DIR/pkg-download"
EXTRACT_DIR="$BUILD_DIR/module-folder"

# Проверка: передан ли параметр
if [ -z "$APP" ]; then
    echo "---------------------------------------------------------------"
    echo "ОШИБКА: Не указано название программы!"
    echo "Использование: $0 <название_программы>"
    echo ""
    echo "Пример: $0 ranger"
    echo "Скрипт скачает программу, все её зависимости, распакует их"
    echo "в одну папку и покажет итоговый размер для модуля Slax."
    echo "---------------------------------------------------------------"
    exit 1
fi

echo "--- Шаг 1: Очистка и подготовка папок ---"
rm -rf "$BUILD_DIR"
mkdir -p "$DOWNLOAD_DIR"
# Очищаем и создаем папку для распаковки (нужны права sudo для очистки системной папки)
sudo rm -rf "$EXTRACT_DIR"
mkdir -p "$EXTRACT_DIR"

echo "--- Шаг 2: Поиск и скачивание зависимостей для [$APP] ---"
cd "$DOWNLOAD_DIR" || exit

# Собираем список всех зависимостей рекурсивно
PKGS=$(apt-cache depends --recurse --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances "$APP" | grep "^\w" | sort -u)

# Скачиваем всё
apt-get download $PKGS

echo ""
echo "--- Шаг 3: Список скачанных пакетов (.deb): ---"
ls -1 "$DOWNLOAD_DIR"
echo "--------------------------------------------"

echo "--- Шаг 4: Распаковка пакетов в итоговую папку ---"
for f in *.deb; do
    echo "Распаковка: $f ..."
    dpkg -x "$f" "$EXTRACT_DIR"
done

echo ""
echo "--- ИТОГОВЫЙ ОТЧЕТ ---"
echo "Папка с распакованными файлами: $EXTRACT_DIR"
echo -n "Общий вес будущего модуля: "
du -sh "$EXTRACT_DIR" | cut -f1
echo "--------------------------------------------"
echo "Теперь ты можешь создать модуль командой:"
echo "dir2sb $EXTRACT_DIR ~/${APP}.sb"
echo "--------------------------------------------"
