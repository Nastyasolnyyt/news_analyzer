from asyncio.log import logger

from natasha import Segmenter, NewsEmbedding, NewsNERTagger, Doc
import pymorphy2 

class Config:
    """Настройки поисковой системы"""
    MIN_WORD_LENGTH = 3
    MAX_LENGTH_DIFF = 6
    ABBREVIATIONS = {
        'рф': ['российская федерация', 'россия'],
        'сша': ['соединенные штаты америки', 'америка'],

    }

class EntityExtractor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)
        self.morph = pymorphy2.MorphAnalyzer()  #  Для лемматизации

    def normalize(self, word):
        return word.lower().strip()

    def extract(self, text):
        if not text or len(text.strip()) < 10:
            return []
        
        try:
            doc = Doc(text)
            doc.segment(self.segmenter)
            doc.tag_ner(self.ner_tagger)

            # Use dict to deduplicate by lemma - keeps first occurrence
            seen_lemmas = {}
            
            for span in doc.spans:
                entity_text = span.text.strip()
                entity_type = span.type
                normalized = self.normalize(entity_text)
                
                # Лемматизация к именительному падежу
                lemma = self.morph.parse(normalized)[0].normal_form

                if len(normalized) >= 3:
                    # Skip if we've already seen this lemma
                    if lemma not in seen_lemmas:
                        seen_lemmas[lemma] = {
                            'text': entity_text,      # Оригинальное написание
                            'normalized': normalized, # Для поиска (lowercase)
                            'lemma': lemma,           # Именительный падеж для БД
                            'type': entity_type
                        }

            return list(seen_lemmas.values())
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []


class SmartSearch:
    """Умный поиск новостей по сущностям"""

    def __init__(self):
        self.extractor = EntityExtractor()
        self.abbreviations = Config.ABBREVIATIONS

        # Обратный индекс: расшифровка → аббревиатура
        self.reverse_abbr = {}
        for abbr, expansions in self.abbreviations.items():
            for exp in expansions:
                self.reverse_abbr[exp] = abbr

    def check_abbreviation(self, query_word, entity_word):
        """Проверяет связь аббревиатуры и полного названия"""
        q = query_word.lower()
        e = entity_word.lower()

        # 1. Запрос аббревиатура -> ищем в расшифровках сущности
        if q in self.abbreviations:
            for expansion in self.abbreviations[q]:
                if expansion in e or e in expansion:
                    return True

        # 2. Сущность аббревиатура -> ищем в расшифровках запроса
        if e in self.abbreviations:
            for expansion in self.abbreviations[e]:
                if expansion in q or q in expansion:
                    return True

        # 3. Обратный поиск
        if e in self.reverse_abbr and self.reverse_abbr[e] == q:
            return True
        if q in self.reverse_abbr and self.reverse_abbr[q] == e:
            return True

        return False

    def match(self, news_entities, user_query):
        """Проверяет, подходит ли новость под запрос"""
        query_norm = user_query.lower()
        query_words = [w for w in query_norm.split() if len(w) >= Config.MIN_WORD_LENGTH]

        for q_word in query_words:
            for entity in news_entities:
                e_norm = entity['normalized']

                # 1. Проверка на аббревиатуры
                if self.check_abbreviation(q_word, e_norm):
                    return True

                # 2. Точное совпадение
                if q_word == e_norm:
                    return True

                # 3. Вхождение (сбер -> сбербанк ИЛИ сбербанк -> сбербанка)
                if q_word in e_norm or e_norm in q_word:
                    if abs(len(q_word) - len(e_norm)) <= Config.MAX_LENGTH_DIFF:
                        return True

        return False

    def index_news(self, news_text):
        """Извлекает сущности для сохранения в БД"""
        return self.extractor.extract(news_text)

    def search(self, news_db, user_query):
        """Ищет новости по запросу"""
        results = []
        for news in news_db:
            if self.match(news['entities'], user_query):
                results.append(news)
        return results


# ============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == '__main__':
    # Инициализация
    search = SmartSearch()

    # Список новостей (Датасет)
    news_list = [
        "Клиенты Сбербанка получили новые бонусы",
        "Акции Сбера выросли на 5%",
        "В Сбер всё стабильно",
        "Тинькофф Банк запустил новую карту",
        "В Т-банке изменились условия",
        "Яндекс объявил о слиянии",
        "Газпром увеличил добычу",
        "Работники тинькофф банка получили сберкнижки",
        "В РФ выросли цены",
        "Российская Федерация подписала договор",
        "ФАС оштрафовала компанию",
        "Федеральная антимонопольная служба вынесла решение",
        "новые сберкнижки выдали россиянам "
    ]

    print(" Индексация новостей...")
    news_db = []
    for text in news_list:
        entities = search.index_news(text)
        news_db.append({'text': text, 'entities': entities})

    print("\nПоиск по запросу: 'сбер'")
    results = search.search(news_db, "сбер")
    for r in results:
        print(f" {r['text']}")

    print("\n Поиск по запросу: 'фас'")
    results = search.search(news_db, "фас")
    for r in results:
        print(f" {r['text']}")

    print("\n Поиск по запросу: 'тинькофф'")
    results = search.search(news_db, "тинькофф")
    for r in results:
        print(f"  {r['text']}")