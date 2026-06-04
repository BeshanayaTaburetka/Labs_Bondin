#!/bin/bash
#
# find_777.sh
# Анализатор прав доступа: рекурсивно ищет файлы с правами 777
# Использование: ./find_777.sh /путь/к/директории

set -o nounset
set -o pipefail

print_usage() {
    echo "Использование: $0 /путь/к/директории"
    echo "Пример:       $0 /var/www"
}

if [[ $# -ne 1 ]]; then
    echo "Ошибка: требуется ровно один аргумент — каталог для анализа." >&2
    print_usage
    exit 1
fi

TARGET_DIR="$1"

if [[ ! -e "$TARGET_DIR" ]]; then
    echo "Ошибка: путь '$TARGET_DIR' не существует." >&2
    exit 2
fi

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Ошибка: путь '$TARGET_DIR' не является каталогом." >&2
    exit 3
fi

if [[ ! -r "$TARGET_DIR" ]]; then
    echo "Ошибка: нет прав на чтение каталога '$TARGET_DIR'." >&2
    exit 4
fi

echo "Анализ каталога: $TARGET_DIR"
echo "Поиск файлов с правами доступа 777 (rwxrwxrwx)..."
echo

FOUND_FILES=$(find "$TARGET_DIR" -type f -perm 0777 2>/dev/null)

if [[ $? -ne 0 ]]; then
    echo "Предупреждение: при поиске возникли ошибки (нет прав к некоторым подкаталогам)." >&2
fi

if [[ -z "$FOUND_FILES" ]]; then
    echo "Файлы с правами 777 не найдены."
    exit 0
fi

echo "Найдены файлы с правами 777:"
echo "$FOUND_FILES"

COUNT=$(echo "$FOUND_FILES" | wc -l)
echo
echo "Всего файлов с правами 777: $COUNT"

exit 0


