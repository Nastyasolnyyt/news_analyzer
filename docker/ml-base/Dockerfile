# docker/ml-base/Dockerfile
FROM python:3.11-slim

# Системные зависимости для всех ML-сервисов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Общие ML-зависимости (кэшируются отдельно!)
COPY <<EOF /app/requirements-ml-base.txt
torch>=2.1.0
transformers==4.42.4
sentence-transformers>=2.2.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
EOF

RUN pip install --no-cache-dir -r requirements-ml-base.txt \
    && rm requirements-ml-base.txt

# Предзагрузка токенизаторов (опционально, ускорит старт контейнеров)
RUN python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('blanchefort/rubert-base-cased-sentiment')" || true

CMD ["echo", "ML base image ready"]