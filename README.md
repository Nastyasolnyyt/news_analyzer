#  News Classifier — Классификатор новостей

Модель машинного обучения для автоматической классификации русскоязычных новостей по категориям.

##  Описание

Проект реализует текстовую классификацию с использованием:
- **Logistic Regression** (sklearn) — модель классификации
- **TF-IDF Vectorizer** — векторизация текста
- **Pandas/NumPy** — обработка данных
- **Файлы с расширением .pkl**

Разделяет на классы :соцальный , экономический, политицеский.

##  Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```
### 2. Загрузить модель и векторизатор
```import joblib
model = joblib.load('models/news_classifier.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
```
### 3. Текст для классификации
```text = ["Цены на бензин выросли в России"]
Векторизация (ВАЖНО: только transform!)
X = vectorizer.transform(text)
```
### 4.Предсказание
```prediction = model.predict(X)[0]
confidence = model.predict_proba(X).max()
print(f" Класс: {prediction}")
print(f" Уверенность: {confidence:.2%}")
```
