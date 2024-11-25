FROM python:3.9-slim

# Rendszerkönyvtárak és eszközök telepítése
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    gcc \
    libffi-dev \
    libsndfile1 \
    && apt-get clean

# PIP frissítése
RUN pip install --upgrade pip

WORKDIR /app

# Pytorch és egyéb függőségek telepítése
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Python csomagok telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Alkalmazás másolása
COPY . .

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
