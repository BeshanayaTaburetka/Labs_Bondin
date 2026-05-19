import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from collections import Counter
import re
import threading
from queue import Queue


# ============ МНОГОПОТОЧНЫЙ КРАУЛЕР (5 ПОТОКОВ) ============

class MultiCrawler:
    def __init__(self, start_url, max_depth=1, threads=5):
        self.start_url = start_url
        self.max_depth = max_depth
        self.threads = threads

        # Общие данные для всех потоков
        self.visited = []  # Список посещённых страниц
        self.visited_lock = threading.Lock()  # Защита от одновременного доступа
        self.pages = []  # Собранные тексты
        self.pages_lock = threading.Lock()

        # Очередь заданий
        self.queue = Queue()
        self.queue.put((start_url, 0))

        # Домен сайта
        self.domain = urlparse(start_url).netloc

        print(f"Сайт: {self.domain}")
        print(f"Глубина: {max_depth}")
        print(f"Потоков: {threads}")

    # Скачать страницу
    def download(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.text
            return None
        except:
            return None

    # Очистить HTML от тегов
    def clean_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style']):
            tag.decompose()
        text = soup.get_text()
        return ' '.join(text.split())

    # Найти все ссылки на странице
    def find_links(self, html, current_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            link = urljoin(current_url, a['href'])
            if urlparse(link).netloc == self.domain:
                link = link.split('#')[0]
                if link not in links:
                    links.append(link)

        return links

    # Функция которую выполняет каждый поток
    def worker(self):
        while True:
            try:
                # Берём задание из очереди (ждём 1 секунду)
                url, depth = self.queue.get(timeout=1)
            except:
                break  # Очередь пуста - выходим

            # Проверяем не посещали ли уже
            with self.visited_lock:
                if url in self.visited:
                    self.queue.task_done()
                    continue
                self.visited.append(url)

            print(f"[{len(self.visited)}] Обрабатываю: {url} (глубина {depth})")

            # Скачиваем страницу
            html = self.download(url)

            if html:
                # Получаем текст
                text = self.clean_html(html)

                # Сохраняем результат
                with self.pages_lock:
                    self.pages.append({
                        'url': url,
                        'depth': depth,
                        'text': text
                    })

                # Если можно идти глубже
                if depth < self.max_depth:
                    # Находим ссылки
                    links = self.find_links(html, url)
                    print(f"    Найдено ссылок: {len(links)}")

                    # Добавляем новые ссылки в очередь
                    with self.visited_lock:
                        for link in links:
                            if link not in self.visited:
                                self.queue.put((link, depth + 1))

                    print(f"    Очередь: {self.queue.qsize()} страниц")

            self.queue.task_done()

    # Запустить обход
    def run(self):
        print("\nНачинаю обход...\n")

        # Создаём и запускаем потоки
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        # Ждём пока все задания выполнятся
        self.queue.join()

        # Останавливаем потоки
        for t in threads:
            t.join()

        print(f"\nОбход закончен. Всего страниц: {len(self.pages)}")
        return self.pages


# ============ АНАЛИЗАТОР ============

class Analyzer:
    # Стоп-слова
    STOP = {'и', 'в', 'на', 'с', 'по', 'к', 'у', 'о', 'для', 'от', 'до',
            'из', 'за', 'под', 'это', 'все', 'было', 'его', 'её', 'их',
            'нет', 'не', 'ни', 'или', 'а', 'но', 'как', 'так', 'что',
            'the', 'and', 'for', 'with', 'from', 'this', 'that'}

    def count_words(self, pages):
        print("\nАнализирую текст...")

        counter = Counter()
        total = 0

        for page in pages:
            # Только слова длиннее 3 букв
            words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]{4,}\b', page['text'].lower())

            for word in words:
                if word not in self.STOP:
                    counter[word] += 1
                    total += 1

        top = counter.most_common(10)

        print(f"\n{'=' * 40}")
        print(f"Страниц: {len(pages)}")
        print(f"Всего слов: {total}")
        print(f"Уникальных слов: {len(counter)}")
        print(f"\nТОП-10 СЛОВ:")
        for i, (word, count) in enumerate(top, 1):
            print(f"  {i}. {word} - {count}")
        print(f"{'=' * 40}")

        return {
            'pages': len(pages),
            'total_words': total,
            'unique_words': len(counter),
            'top_words': dict(top)
        }


# ============ СОХРАНЕНИЕ ============

def save_json(data, filename='results.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nСохранено в {filename}")


# ============ ЗАПУСК ============

def main():
    print("\n" + "=" * 40)
    print("   ВЕБ-КРАУЛЕР (5 ПОТОКОВ ОДНОВРЕМЕННО)")
    print("=" * 40)

    # Ввод данных
    url = input("\nВведите URL: ").strip()
    if not url:
        url = "https://example.com"
        print(f"Использую: {url}")

    try:
        depth = int(input("Глубина (0 или 1): ") or "1")
        if depth > 1:
            depth = 1
    except:
        depth = 1

    try:
        threads = int(input("Количество потоков (по умолч. 5): ") or "5")
        if threads < 1:
            threads = 5
        if threads > 10:
            threads = 10
            print("Ограничил до 10 потоков")
    except:
        threads = 5

    # Запуск
    crawler = MultiCrawler(url, depth, threads)
    pages = crawler.run()

    if pages:
        analyzer = Analyzer()
        results = analyzer.count_words(pages)
        save_json(results)
        print("\nГОТОВО!")
    else:
        print("\nНичего не собрано. Проверьте URL.")


if __name__ == "__main__":
    main()