FROM python:3.9-slim

# Rendszerfüggőségek és FFmpeg telepítése
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libpq-dev \
    && apt-get clean

# Frissítsük a pip-et
RUN pip install --upgrade pip

WORKDIR /app

# Pytorch CPU verzió telepítése
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Python csomagok telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Alkalmazás másolása
COPY . .

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
